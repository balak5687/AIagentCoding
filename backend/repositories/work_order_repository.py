"""
Work Order Repository

Provides data access methods for work_orders DynamoDB table.
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


# Custom Exceptions
class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass


class ItemNotFoundError(RepositoryError):
    """Raised when item is not found"""
    pass


class ItemAlreadyExistsError(RepositoryError):
    """Raised when item already exists"""
    pass


class ConcurrencyError(RepositoryError):
    """Raised when concurrent modification is detected"""
    pass


class WorkOrderRepository:
    """Repository for work order data access"""

    def __init__(self, dynamodb_resource=None):
        """
        Initialize repository with DynamoDB resource.

        Args:
            dynamodb_resource: boto3 DynamoDB resource (optional, will create if not provided)
        """
        self.dynamodb = dynamodb_resource or boto3.resource('dynamodb')
        environment = os.getenv("ENVIRONMENT", "development")
        self.table_name = f"work_orders_{environment}"
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, work_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new work order.

        Args:
            work_order: Work order data

        Returns:
            Created work order

        Raises:
            ItemAlreadyExistsError: If work order with same ID already exists
            RepositoryError: If creation fails
        """
        try:
            # Add metadata
            work_order['created_at'] = datetime.utcnow().isoformat()
            work_order['updated_at'] = datetime.utcnow().isoformat()
            work_order['version'] = 1

            # Put item with condition to prevent overwrite
            self.table.put_item(
                Item=work_order,
                ConditionExpression='attribute_not_exists(id)'
            )
            return work_order

        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ItemAlreadyExistsError(f"Work order with id {work_order.get('id')} already exists")
            raise RepositoryError(f"Failed to create work order: {str(e)}")

    def get_by_id(self, work_order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get work order by ID.

        Args:
            work_order_id: Work order ID

        Returns:
            Work order data or None if not found

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            response = self.table.get_item(Key={'id': work_order_id})
            return response.get('Item')

        except ClientError as e:
            raise RepositoryError(f"Failed to get work order: {str(e)}")

    def update(self, work_order_id: str, updates: Dict[str, Any], expected_version: int) -> Dict[str, Any]:
        """
        Update a work order with optimistic locking.

        Args:
            work_order_id: Work order ID
            updates: Fields to update
            expected_version: Expected version for optimistic locking

        Returns:
            Updated work order

        Raises:
            ItemNotFoundError: If work order doesn't exist
            ConcurrencyError: If version mismatch (concurrent modification)
            RepositoryError: If update fails
        """
        try:
            # Build update expression
            update_expr_parts = []
            expr_attr_names = {}
            expr_attr_values = {}

            for key, value in updates.items():
                if key not in ['id', 'version', 'created_at']:  # Skip immutable fields
                    placeholder = f"#{key}"
                    value_placeholder = f":{key}"
                    update_expr_parts.append(f"{placeholder} = {value_placeholder}")
                    expr_attr_names[placeholder] = key
                    expr_attr_values[value_placeholder] = value

            # Add updated_at and increment version
            update_expr_parts.append("#updated_at = :updated_at")
            update_expr_parts.append("#version = :new_version")
            expr_attr_names["#updated_at"] = "updated_at"
            expr_attr_names["#version"] = "version"
            expr_attr_values[":updated_at"] = datetime.utcnow().isoformat()
            expr_attr_values[":new_version"] = expected_version + 1
            expr_attr_values[":expected_version"] = expected_version

            update_expr = "SET " + ", ".join(update_expr_parts)

            # Update with conditions: item exists AND version matches
            response = self.table.update_item(
                Key={'id': work_order_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ConditionExpression='attribute_exists(id) AND #version = :expected_version',
                ReturnValues='ALL_NEW'
            )

            return response['Attributes']

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                # Check if item exists
                item = self.get_by_id(work_order_id)
                if not item:
                    raise ItemNotFoundError(f"Work order with id {work_order_id} not found")
                else:
                    raise ConcurrencyError(
                        f"Version mismatch for work order {work_order_id}. "
                        f"Expected version {expected_version}, current version {item.get('version')}"
                    )
            raise RepositoryError(f"Failed to update work order: {str(e)}")

    def delete(self, work_order_id: str) -> None:
        """
        Delete a work order.

        Args:
            work_order_id: Work order ID

        Raises:
            ItemNotFoundError: If work order doesn't exist
            RepositoryError: If deletion fails
        """
        try:
            self.table.delete_item(
                Key={'id': work_order_id},
                ConditionExpression='attribute_exists(id)'
            )

        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ItemNotFoundError(f"Work order with id {work_order_id} not found")
            raise RepositoryError(f"Failed to delete work order: {str(e)}")

    def list_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all work orders with pagination support.

        Args:
            limit: Maximum number of items to return (None for all)

        Returns:
            List of work orders

        Raises:
            RepositoryError: If scan fails
        """
        try:
            items = []
            scan_kwargs = {}

            if limit:
                scan_kwargs['Limit'] = limit

            # Paginate through all results
            while True:
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))

                # Check if we've hit the limit
                if limit and len(items) >= limit:
                    items = items[:limit]
                    break

                # Check if there are more pages
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

                # Set up for next page
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

                # Adjust limit for next page if needed
                if limit:
                    remaining = limit - len(items)
                    scan_kwargs['Limit'] = remaining

            return items

        except ClientError as e:
            raise RepositoryError(f"Failed to list work orders: {str(e)}")

    def query_by_priority_and_due_date(
        self,
        priority: int,
        due_date_start: Optional[str] = None,
        due_date_end: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query work orders by priority and due date range using GSI.

        Args:
            priority: Priority level
            due_date_start: Start date (ISO format) for range query (optional)
            due_date_end: End date (ISO format) for range query (optional)
            limit: Maximum number of items to return

        Returns:
            List of work orders

        Raises:
            RepositoryError: If query fails
        """
        try:
            query_kwargs = {
                'IndexName': 'priority-due_date-index',
                'KeyConditionExpression': Key('priority').eq(priority)
            }

            # Add range condition if provided
            if due_date_start and due_date_end:
                query_kwargs['KeyConditionExpression'] &= Key('due_date').between(due_date_start, due_date_end)
            elif due_date_start:
                query_kwargs['KeyConditionExpression'] &= Key('due_date').gte(due_date_start)
            elif due_date_end:
                query_kwargs['KeyConditionExpression'] &= Key('due_date').lte(due_date_end)

            if limit:
                query_kwargs['Limit'] = limit

            items = []

            # Paginate through results
            while True:
                response = self.table.query(**query_kwargs)
                items.extend(response.get('Items', []))

                # Check if we've hit the limit
                if limit and len(items) >= limit:
                    items = items[:limit]
                    break

                # Check if there are more pages
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

                # Set up for next page
                query_kwargs['ExclusiveStartKey'] = last_evaluated_key

                # Adjust limit for next page if needed
                if limit:
                    remaining = limit - len(items)
                    query_kwargs['Limit'] = remaining

            return items

        except ClientError as e:
            raise RepositoryError(f"Failed to query by priority and due date: {str(e)}")

    def query_by_delivery_status(
        self,
        delivery_status: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query work orders by delivery status using GSI.

        Args:
            delivery_status: Delivery status
            limit: Maximum number of items to return

        Returns:
            List of work orders

        Raises:
            RepositoryError: If query fails
        """
        try:
            query_kwargs = {
                'IndexName': 'delivery_status-index',
                'KeyConditionExpression': Key('delivery_status').eq(delivery_status)
            }

            if limit:
                query_kwargs['Limit'] = limit

            items = []

            # Paginate through results
            while True:
                response = self.table.query(**query_kwargs)
                items.extend(response.get('Items', []))

                # Check if we've hit the limit
                if limit and len(items) >= limit:
                    items = items[:limit]
                    break

                # Check if there are more pages
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

                # Set up for next page
                query_kwargs['ExclusiveStartKey'] = last_evaluated_key

                # Adjust limit for next page if needed
                if limit:
                    remaining = limit - len(items)
                    query_kwargs['Limit'] = remaining

            return items

        except ClientError as e:
            raise RepositoryError(f"Failed to query by delivery status: {str(e)}")
