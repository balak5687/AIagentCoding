"""
DynamoDB Table Configuration

Defines table schemas, GSIs, and provisioning settings for all DynamoDB tables.
"""
import os


def get_work_orders_table_config():
    """
    Get configuration for work_orders table including GSIs.

    Returns:
        dict: Table configuration with name, keys, GSIs, and provisioning settings
    """
    environment = os.getenv("ENVIRONMENT", "development")

    config = {
        "TableName": f"work_orders_{environment}",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"}  # Partition key
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "priority", "AttributeType": "N"},
            {"AttributeName": "due_date", "AttributeType": "S"},
            {"AttributeName": "delivery_status", "AttributeType": "S"}
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "priority-due_date-index",
                "KeySchema": [
                    {"AttributeName": "priority", "KeyType": "HASH"},
                    {"AttributeName": "due_date", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            },
            {
                "IndexName": "delivery_status-index",
                "KeySchema": [
                    {"AttributeName": "delivery_status", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            }
        ],
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10
        },
        "StreamSpecification": {
            "StreamEnabled": True,
            "StreamViewType": "NEW_AND_OLD_IMAGES"
        },
        "Tags": [
            {"Key": "Environment", "Value": environment},
            {"Key": "Application", "Value": "SDLCAgent"},
            {"Key": "ManagedBy", "Value": "Terraform"}
        ]
    }

    return config


def get_all_table_configs():
    """
    Get configurations for all DynamoDB tables.

    Returns:
        list: List of table configurations
    """
    return [
        get_work_orders_table_config()
        # Add other table configs here as needed
    ]
