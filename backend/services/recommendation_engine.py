"""Smart recommendations engine for vehicle maintenance."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from enum import Enum

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationReason(Enum):
    """Reason codes for recommendations."""
    MILEAGE_THRESHOLD = "mileage_threshold"
    TIME_THRESHOLD = "time_threshold"
    OVERDUE = "overdue"
    PREVENTIVE = "preventive"


def _validate_vehicle_id(vehicle_id: str) -> None:
    """Validate vehicle ID format."""
    if not vehicle_id or not isinstance(vehicle_id, str):
        raise ValueError("vehicle_id must be a non-empty string")

    if len(vehicle_id) > 100:
        raise ValueError("vehicle_id exceeds maximum length")


def _validate_mileage(mileage: int) -> None:
    """Validate mileage value."""
    if not isinstance(mileage, int):
        raise ValueError("mileage must be an integer")

    if mileage < 0:
        raise ValueError("mileage cannot be negative")

    if mileage > 1_000_000:
        raise ValueError("mileage exceeds reasonable limit")


class SmartRecommendationEngine:
    """
    Smart recommendation engine that analyzes service history,
    mileage thresholds, and time-based rules to suggest maintenance.
    """

    def __init__(self, dynamodb_resource: Optional[Any] = None):
        """
        Initialize recommendation engine.

        Args:
            dynamodb_resource: Optional DynamoDB resource (for testing)
        """
        if dynamodb_resource is None:
            dynamodb_resource = boto3.resource('dynamodb')

        self.dynamodb = dynamodb_resource
        self.service_history_table = self.dynamodb.Table('service_history')
        self.service_rules_table = self.dynamodb.Table('service_rules')
        self.recommendation_history_table = self.dynamodb.Table('recommendation_history')

        logger.info("Initialized SmartRecommendationEngine")

    def get_smart_recommendations(
        self,
        vehicle_id: str,
        current_mileage: int
    ) -> List[Dict[str, Any]]:
        """
        Generate smart recommendations based on service history and rules.

        Args:
            vehicle_id: Vehicle identifier
            current_mileage: Current vehicle mileage

        Returns:
            List of recommendation dictionaries with details

        Raises:
            ValueError: If input validation fails
            ClientError: If DynamoDB query fails
        """
        # Validate inputs
        _validate_vehicle_id(vehicle_id)
        _validate_mileage(current_mileage)

        try:
            # Get service history for vehicle
            logger.info(f"Fetching service history for vehicle {vehicle_id}")
            service_history = self._get_service_history(vehicle_id)

            # Get all service rules
            logger.info("Fetching service rules")
            service_rules = self._get_service_rules()

            # Generate recommendations
            recommendations = []

            for rule in service_rules:
                recommendation = self._evaluate_service_rule(
                    rule,
                    service_history,
                    current_mileage
                )

                if recommendation:
                    recommendations.append(recommendation)

            # Sort by priority and score
            recommendations.sort(
                key=lambda x: (
                    self._priority_weight(x['priority']),
                    -x['score']
                )
            )

            # Store recommendation history
            if recommendations:
                self._store_recommendation_history(vehicle_id, recommendations)

            logger.info(
                f"Generated {len(recommendations)} recommendations "
                f"for vehicle {vehicle_id}"
            )

            return recommendations

        except ClientError as e:
            logger.error(f"DynamoDB error generating recommendations: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating recommendations: {e}")
            raise

    def _get_service_history(self, vehicle_id: str) -> List[Dict[str, Any]]:
        """
        Fetch service history for a vehicle.

        Args:
            vehicle_id: Vehicle identifier

        Returns:
            List of service history records
        """
        try:
            items = []
            response = self.service_history_table.query(
                KeyConditionExpression=Key('vehicle_id').eq(vehicle_id)
            )

            items.extend(response.get('Items', []))

            # Paginate through results
            while 'LastEvaluatedKey' in response:
                response = self.service_history_table.query(
                    KeyConditionExpression=Key('vehicle_id').eq(vehicle_id),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))

            return items

        except ClientError as e:
            logger.error(f"Error fetching service history: {e}")
            raise

    def _get_service_rules(self) -> List[Dict[str, Any]]:
        """
        Fetch all service rules.

        Returns:
            List of service rule records
        """
        try:
            items = []
            response = self.service_rules_table.scan()

            items.extend(response.get('Items', []))

            # Paginate through results
            while 'LastEvaluatedKey' in response:
                response = self.service_rules_table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))

            return items

        except ClientError as e:
            logger.error(f"Error fetching service rules: {e}")
            raise

    def _evaluate_service_rule(
        self,
        rule: Dict[str, Any],
        service_history: List[Dict[str, Any]],
        current_mileage: int
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate a service rule against history and current state.

        Args:
            rule: Service rule definition
            service_history: Vehicle service history
            current_mileage: Current vehicle mileage

        Returns:
            Recommendation dict if rule triggered, None otherwise
        """
        service_type = rule.get('service_type')

        # Find last service of this type
        last_service = self._find_last_service(service_history, service_type)

        # Check mileage threshold
        mileage_check = self._check_mileage_threshold(
            rule,
            last_service,
            current_mileage
        )

        # Check time threshold
        time_check = self._check_time_threshold(rule, last_service)

        # If either threshold is met, create recommendation
        if mileage_check or time_check:
            return self._create_recommendation(
                rule,
                last_service,
                mileage_check,
                time_check,
                current_mileage
            )

        return None

    def _find_last_service(
        self,
        service_history: List[Dict[str, Any]],
        service_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find the most recent service of a given type.

        Args:
            service_history: List of service records
            service_type: Service type to find

        Returns:
            Most recent service record or None
        """
        matching_services = [
            s for s in service_history
            if s.get('service_type') == service_type
        ]

        if not matching_services:
            return None

        # Sort by date descending
        matching_services.sort(
            key=lambda x: x.get('service_date', ''),
            reverse=True
        )

        return matching_services[0]

    def _check_mileage_threshold(
        self,
        rule: Dict[str, Any],
        last_service: Optional[Dict[str, Any]],
        current_mileage: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check if mileage threshold is met.

        Args:
            rule: Service rule definition
            last_service: Last service record or None
            current_mileage: Current vehicle mileage

        Returns:
            Dict with check results if threshold met, None otherwise
        """
        mileage_interval = rule.get('mileage_interval')

        if not mileage_interval:
            return None

        if last_service:
            last_mileage = int(last_service.get('mileage', 0))
            miles_since_service = current_mileage - last_mileage

            if miles_since_service >= mileage_interval:
                return {
                    'triggered': True,
                    'miles_since_service': miles_since_service,
                    'miles_overdue': miles_since_service - mileage_interval
                }
        else:
            # No previous service - recommend if current mileage exceeds interval
            if current_mileage >= mileage_interval:
                return {
                    'triggered': True,
                    'miles_since_service': current_mileage,
                    'miles_overdue': 0
                }

        return None

    def _check_time_threshold(
        self,
        rule: Dict[str, Any],
        last_service: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if time threshold is met.

        Args:
            rule: Service rule definition
            last_service: Last service record or None

        Returns:
            Dict with check results if threshold met, None otherwise
        """
        time_interval_days = rule.get('time_interval_days')

        if not time_interval_days:
            return None

        if last_service:
            last_date_str = last_service.get('service_date')

            if last_date_str:
                try:
                    last_date = datetime.fromisoformat(last_date_str)
                    days_since_service = (datetime.now() - last_date).days

                    if days_since_service >= time_interval_days:
                        return {
                            'triggered': True,
                            'days_since_service': days_since_service,
                            'days_overdue': days_since_service - time_interval_days
                        }
                except ValueError:
                    logger.warning(f"Invalid date format: {last_date_str}")

        return None

    def _create_recommendation(
        self,
        rule: Dict[str, Any],
        last_service: Optional[Dict[str, Any]],
        mileage_check: Optional[Dict[str, Any]],
        time_check: Optional[Dict[str, Any]],
        current_mileage: int
    ) -> Dict[str, Any]:
        """
        Create a recommendation from rule and checks.

        Args:
            rule: Service rule definition
            last_service: Last service record or None
            mileage_check: Mileage threshold check result
            time_check: Time threshold check result
            current_mileage: Current vehicle mileage

        Returns:
            Recommendation dictionary
        """
        # Determine priority
        priority = self._determine_priority(mileage_check, time_check)

        # Calculate score (0-100)
        score = self._calculate_score(mileage_check, time_check)

        # Determine reason
        reasons = []
        if mileage_check and mileage_check.get('triggered'):
            if mileage_check.get('miles_overdue', 0) > 0:
                reasons.append(RecommendationReason.OVERDUE.value)
            else:
                reasons.append(RecommendationReason.MILEAGE_THRESHOLD.value)

        if time_check and time_check.get('triggered'):
            if time_check.get('days_overdue', 0) > 0:
                if RecommendationReason.OVERDUE.value not in reasons:
                    reasons.append(RecommendationReason.OVERDUE.value)
            else:
                reasons.append(RecommendationReason.TIME_THRESHOLD.value)

        return {
            'service_type': rule.get('service_type'),
            'service_name': rule.get('service_name'),
            'priority': priority,
            'score': score,
            'reasons': reasons,
            'mileage_info': mileage_check,
            'time_info': time_check,
            'current_mileage': current_mileage,
            'last_service': last_service,
            'estimated_cost': rule.get('estimated_cost'),
            'description': rule.get('description')
        }

    def _determine_priority(
        self,
        mileage_check: Optional[Dict[str, Any]],
        time_check: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determine recommendation priority based on checks.

        Args:
            mileage_check: Mileage threshold check result
            time_check: Time threshold check result

        Returns:
            Priority level string
        """
        # Critical if significantly overdue
        if mileage_check and mileage_check.get('miles_overdue', 0) > 5000:
            return RecommendationPriority.CRITICAL.value

        if time_check and time_check.get('days_overdue', 0) > 180:
            return RecommendationPriority.CRITICAL.value

        # High if somewhat overdue
        if mileage_check and mileage_check.get('miles_overdue', 0) > 1000:
            return RecommendationPriority.HIGH.value

        if time_check and time_check.get('days_overdue', 0) > 60:
            return RecommendationPriority.HIGH.value

        # Medium if just at threshold
        if (mileage_check and mileage_check.get('triggered')) or \
           (time_check and time_check.get('triggered')):
            return RecommendationPriority.MEDIUM.value

        return RecommendationPriority.LOW.value

    def _calculate_score(
        self,
        mileage_check: Optional[Dict[str, Any]],
        time_check: Optional[Dict[str, Any]]
    ) -> int:
        """
        Calculate recommendation score (0-100).

        Args:
            mileage_check: Mileage threshold check result
            time_check: Time threshold check result

        Returns:
            Score from 0-100
        """
        score = 50  # Base score

        # Add points for mileage overdue
        if mileage_check:
            miles_overdue = mileage_check.get('miles_overdue', 0)
            # 1 point per 100 miles overdue, max 30 points
            score += min(30, miles_overdue // 100)

        # Add points for time overdue
        if time_check:
            days_overdue = time_check.get('days_overdue', 0)
            # 1 point per 3 days overdue, max 20 points
            score += min(20, days_overdue // 3)

        return min(100, score)

    def _priority_weight(self, priority: str) -> int:
        """
        Convert priority to numeric weight for sorting.

        Args:
            priority: Priority level string

        Returns:
            Numeric weight (lower is higher priority)
        """
        weights = {
            RecommendationPriority.CRITICAL.value: 1,
            RecommendationPriority.HIGH.value: 2,
            RecommendationPriority.MEDIUM.value: 3,
            RecommendationPriority.LOW.value: 4
        }
        return weights.get(priority, 5)

    def _store_recommendation_history(
        self,
        vehicle_id: str,
        recommendations: List[Dict[str, Any]]
    ) -> None:
        """
        Store recommendation history for a vehicle.

        Args:
            vehicle_id: Vehicle identifier
            recommendations: List of recommendations to store
        """
        try:
            timestamp = datetime.now().isoformat()

            self.recommendation_history_table.put_item(
                Item={
                    'vehicle_id': vehicle_id,
                    'timestamp': timestamp,
                    'recommendations': recommendations,
                    'recommendation_count': len(recommendations)
                }
            )

            logger.info(
                f"Stored {len(recommendations)} recommendations "
                f"for vehicle {vehicle_id}"
            )

        except ClientError as e:
            logger.error(f"Error storing recommendation history: {e}")
            # Don't raise - this is non-critical


def get_vehicle_recommendations(
    vehicle_id: str,
    current_mileage: int,
    engine: Optional[SmartRecommendationEngine] = None
) -> List[Dict[str, Any]]:
    """
    Get smart recommendations for a vehicle.

    Convenience function that creates engine if not provided.

    Args:
        vehicle_id: Vehicle identifier
        current_mileage: Current vehicle mileage
        engine: Optional recommendation engine instance

    Returns:
        List of recommendations
    """
    if engine is None:
        engine = SmartRecommendationEngine()

    return engine.get_smart_recommendations(vehicle_id, current_mileage)
