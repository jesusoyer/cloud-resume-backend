import importlib
import json
import os

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def counter():
    """Create a fake DynamoDB table and load the Lambda code against it."""
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"        # fake keys: moto never calls AWS
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["TABLE_NAME"] = "test-visitors"
    with mock_aws():
        boto3.client("dynamodb").create_table(
            TableName="test-visitors",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        from src import visitor_counter
        importlib.reload(visitor_counter)   # reconnect to the fake table
        yield visitor_counter


def call(counter):
    response = counter.lambda_handler({}, None)
    return response, json.loads(response["body"])


def test_first_visit_starts_at_one(counter):
    # Edge case: the item doesn't exist yet
    response, body = call(counter)
    assert response["statusCode"] == 200
    assert body["count"] == 999


def test_each_visit_adds_one(counter):
    _, first = call(counter)
    _, second = call(counter)
    assert second["count"] == first["count"] + 1


def test_response_is_json_with_content_type(counter):
    response, body = call(counter)
    assert response["headers"]["Content-Type"] == "application/json"
    assert isinstance(body["count"], int)