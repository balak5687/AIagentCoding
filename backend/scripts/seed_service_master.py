#!/usr/bin/env python3
"""
Seed script for ServiceMaster data.

Populates the database with common automotive services including:
- Service types and descriptions
- Standard durations
- Base prices
- Mileage-based maintenance rules
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate and add project root to path
project_root = Path(__file__).parent.parent
if not project_root.exists() or not project_root.is_dir():
    logger.error(f"Invalid project root path: {project_root}")
    sys.exit(1)

sys.path.insert(0, str(project_root))

from models.service_master import ServiceMaster
from repositories.service_master_repository import ServiceMasterRepository

# Validation constants
MAX_SERVICE_TYPE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
VALID_SEVERITIES = {"routine", "maintenance", "critical"}


def get_seed_data() -> List[dict]:
    """
    Returns seed data for automotive services.

    Includes common maintenance and repair services with:
    - Industry-standard durations
    - Base pricing (regional variation expected)
    - Mileage-based recommendation rules
    """
    return [
        {
            "service_type": "Oil Change",
            "description": "Standard oil and filter change with multi-point inspection",
            "standard_duration": 30,  # minutes
            "base_price": 49.99,
            "required_parts": ["oil_filter", "engine_oil"],
            "mileage_rules": {
                "interval_miles": 5000,
                "interval_months": 6,
                "severity": "routine"
            }
        },
        {
            "service_type": "Tire Rotation",
            "description": "Rotate all four tires to ensure even wear",
            "standard_duration": 45,
            "base_price": 35.00,
            "required_parts": [],
            "mileage_rules": {
                "interval_miles": 7500,
                "interval_months": 6,
                "severity": "routine"
            }
        },
        {
            "service_type": "Brake Pad Replacement",
            "description": "Replace front or rear brake pads and inspect rotors",
            "standard_duration": 120,
            "base_price": 299.99,
            "required_parts": ["brake_pads", "brake_cleaner"],
            "mileage_rules": {
                "interval_miles": 40000,
                "interval_months": 36,
                "severity": "maintenance"
            }
        },
        {
            "service_type": "Air Filter Replacement",
            "description": "Replace engine air filter for optimal performance",
            "standard_duration": 15,
            "base_price": 39.99,
            "required_parts": ["air_filter"],
            "mileage_rules": {
                "interval_miles": 15000,
                "interval_months": 12,
                "severity": "routine"
            }
        },
        {
            "service_type": "Battery Test and Replacement",
            "description": "Test battery health and replace if needed",
            "standard_duration": 30,
            "base_price": 179.99,
            "required_parts": ["battery"],
            "mileage_rules": {
                "interval_miles": None,  # Time-based only
                "interval_months": 48,
                "severity": "maintenance"
            }
        },
        {
            "service_type": "Transmission Fluid Service",
            "description": "Drain and replace transmission fluid and filter",
            "standard_duration": 90,
            "base_price": 189.99,
            "required_parts": ["transmission_fluid", "transmission_filter"],
            "mileage_rules": {
                "interval_miles": 60000,
                "interval_months": 48,
                "severity": "maintenance"
            }
        },
        {
            "service_type": "Coolant Flush",
            "description": "Flush cooling system and replace coolant",
            "standard_duration": 60,
            "base_price": 129.99,
            "required_parts": ["coolant"],
            "mileage_rules": {
                "interval_miles": 50000,
                "interval_months": 60,
                "severity": "maintenance"
            }
        },
        {
            "service_type": "Wheel Alignment",
            "description": "Four-wheel alignment check and adjustment",
            "standard_duration": 75,
            "base_price": 89.99,
            "required_parts": [],
            "mileage_rules": {
                "interval_miles": 12000,
                "interval_months": 12,
                "severity": "routine"
            }
        },
        {
            "service_type": "Timing Belt Replacement",
            "description": "Replace timing belt and inspect related components",
            "standard_duration": 300,  # 5 hours
            "base_price": 899.99,
            "required_parts": ["timing_belt", "water_pump", "tensioner"],
            "mileage_rules": {
                "interval_miles": 100000,
                "interval_months": 84,  # 7 years
                "severity": "critical"
            }
        },
        {
            "service_type": "Spark Plug Replacement",
            "description": "Replace spark plugs for optimal engine performance",
            "standard_duration": 60,
            "base_price": 149.99,
            "required_parts": ["spark_plugs"],
            "mileage_rules": {
                "interval_miles": 30000,
                "interval_months": 36,
                "severity": "maintenance"
            }
        },
        {
            "service_type": "Cabin Air Filter Replacement",
            "description": "Replace cabin air filter for clean interior air",
            "standard_duration": 20,
            "base_price": 45.00,
            "required_parts": ["cabin_air_filter"],
            "mileage_rules": {
                "interval_miles": 15000,
                "interval_months": 12,
                "severity": "routine"
            }
        },
        {
            "service_type": "Wiper Blade Replacement",
            "description": "Replace front and rear wiper blades",
            "standard_duration": 15,
            "base_price": 29.99,
            "required_parts": ["wiper_blades"],
            "mileage_rules": {
                "interval_miles": None,
                "interval_months": 12,
                "severity": "routine"
            }
        },
        {
            "service_type": "Full Vehicle Inspection",
            "description": "Comprehensive 50-point safety and maintenance inspection",
            "standard_duration": 90,
            "base_price": 0.00,  # Often complimentary
            "required_parts": [],
            "mileage_rules": {
                "interval_miles": 10000,
                "interval_months": 12,
                "severity": "routine"
            }
        },
        {
            "service_type": "Fuel System Cleaning",
            "description": "Clean fuel injectors and intake system",
            "standard_duration": 45,
            "base_price": 159.99,
            "required_parts": ["fuel_system_cleaner"],
            "mileage_rules": {
                "interval_miles": 30000,
                "interval_months": 24,
                "severity": "maintenance"
            }
        },
        {
            "service_type": "Differential Service",
            "description": "Drain and replace differential fluid",
            "standard_duration": 60,
            "base_price": 119.99,
            "required_parts": ["differential_fluid"],
            "mileage_rules": {
                "interval_miles": 50000,
                "interval_months": 48,
                "severity": "maintenance"
            }
        }
    ]


def validate_service_data(service_dict: dict) -> bool:
    """
    Validate service data before insertion.

    Args:
        service_dict: Dictionary containing service data

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["service_type", "description", "standard_duration", "base_price"]

    # Check required fields
    for field in required_fields:
        if field not in service_dict:
            logger.error(f"Missing required field: {field}")
            return False

    # Validate string lengths
    if len(service_dict.get("service_type", "")) > MAX_SERVICE_TYPE_LENGTH:
        logger.error(f"service_type exceeds {MAX_SERVICE_TYPE_LENGTH} characters: {service_dict['service_type']}")
        return False

    if len(service_dict.get("description", "")) > MAX_DESCRIPTION_LENGTH:
        logger.error(f"description exceeds {MAX_DESCRIPTION_LENGTH} characters: {service_dict['description']}")
        return False

    # Validate numeric values
    if service_dict.get("standard_duration", 0) <= 0:
        logger.error(f"Invalid standard_duration: {service_dict.get('standard_duration')}")
        return False

    if service_dict.get("base_price", -1) < 0:
        logger.error(f"Invalid base_price: {service_dict.get('base_price')}")
        return False

    # Validate required_parts if present
    if "required_parts" in service_dict:
        if not isinstance(service_dict["required_parts"], list):
            logger.error(f"required_parts must be a list: {service_dict['required_parts']}")
            return False

    # Validate mileage_rules if present
    if "mileage_rules" in service_dict:
        rules = service_dict["mileage_rules"]
        if not isinstance(rules, dict):
            logger.error(f"mileage_rules must be a dictionary: {rules}")
            return False

        if "severity" in rules and rules["severity"] not in VALID_SEVERITIES:
            logger.error(f"Invalid severity '{rules['severity']}', must be one of {VALID_SEVERITIES}")
            return False

        if "interval_miles" in rules and rules["interval_miles"] is not None:
            if not isinstance(rules["interval_miles"], int) or rules["interval_miles"] <= 0:
                logger.error(f"interval_miles must be a positive integer: {rules['interval_miles']}")
                return False

        if "interval_months" in rules and rules["interval_months"] is not None:
            if not isinstance(rules["interval_months"], int) or rules["interval_months"] <= 0:
                logger.error(f"interval_months must be a positive integer: {rules['interval_months']}")
                return False

    return True


def seed_service_master() -> bool:
    """
    Seed the ServiceMaster table with initial data.

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Initializing ServiceMaster repository...")
        repository = ServiceMasterRepository()

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        return False
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing repository: {e}")
        return False

    seed_data = get_seed_data()
    logger.info(f"Preparing to seed {len(seed_data)} services...")

    # Pre-flight duplicate detection
    service_types = [s.get("service_type", "") for s in seed_data]
    seen = set()
    duplicates = [st for st in service_types if st in seen or seen.add(st)]
    if duplicates:
        logger.error(f"Duplicate service_types found in seed data: {duplicates}")
        return False

    success_count = 0
    failed_services = []

    for service_dict in seed_data:
        service_type = service_dict.get("service_type", "Unknown")

        try:
            # Validate data
            if not validate_service_data(service_dict):
                logger.warning(f"Skipping invalid service: {service_type}")
                failed_services.append(service_type)
                continue

            # Create ServiceMaster object
            service = ServiceMaster(**service_dict)

            # Save to database
            result = repository.create(service)

            # Validate return value
            if result is None or not hasattr(result, 'service_id'):
                logger.error(f"Invalid return value from repository.create() for {service_type}")
                failed_services.append(service_type)
                continue

            logger.info(f"✓ Seeded: {service_type} (ID: {result.service_id})")
            success_count += 1

        except ValueError as e:
            logger.error(f"Validation error for {service_type}: {e}")
            failed_services.append(service_type)
        except KeyError as e:
            logger.error(f"Missing key in {service_type}: {e}")
            failed_services.append(service_type)
        except Exception as e:
            logger.error(f"Failed to seed {service_type}: {e}")
            failed_services.append(service_type)

    # Summary
    logger.info("=" * 50)
    logger.info(f"Seeding complete: {success_count}/{len(seed_data)} successful")

    if failed_services:
        logger.warning(f"Failed services: {', '.join(failed_services)}")
        return False

    logger.info("All services seeded successfully!")
    return True


if __name__ == "__main__":
    logger.info("Starting ServiceMaster seed script...")
    success = seed_service_master()
    sys.exit(0 if success else 1)
