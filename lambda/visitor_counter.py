import json
import os
import boto3

# Connect once, when Lambda starts, so each visit is faster.
TABLE_NAME = os.environ.get("TABLE_NAME", "cloud-resume-visitors")
table = boto3.resource("dynamodb").Table(TABLE_NAME)


def lambda_handler(event, context):
    # Add 1 to visit_count in one step and get the new total back.
    response = table.update_item(
        Key={"id": "visitors"},
        UpdateExpression="ADD visit_count :inc",
        ExpressionAttributeValues={":inc": 1},
        ReturnValues="UPDATED_NEW",
    )
    count = int(response["Attributes"]["visit_count"])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"count": count}),
    }