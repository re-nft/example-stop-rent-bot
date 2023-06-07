# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError

from dotenv import load_dotenv
import json
import os
load_dotenv()

_env = dict()
SECRETS = [
    "PRIVATE_KEY",
    "DISCORD_WEBHOOK_TOKEN",
    "PROVIDER_URL"
]

# if there is no env file, we assume we are running on aws
NO_ENV_FILE = os.getenv(SECRETS[0]) is None


def get_secrets_from_env_file():
    for secret in SECRETS:
        if secret not in _env:
            _env[secret] = os.getenv(secret)


def get_secrets_from_kms():

    secret_name = "polygon-claim-rent"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    get_secret_value_response = get_secret_value_response['SecretString']

    # SecretString looks like the below
    # note that [..] is a placeholder for actual value
    # {'ARN': 'arn:aws:secretsmanager:region:user_id:secret:[..],
    # 'Name': '[..]', 'VersionId': '[..]',
    # 'SecretString': '{"ENV_VAR_FOO":"",
    #                  "ENV_VAR_BAR":"",
    #                  ...,
    #                  "ENV_VAR_BAZ":""}'
    # 'VersionStages': ['AWSCURRENT'],
    # 'CreatedDate': datetime.datetime(2023, 2, 18, 15, 58, 21, 468000, tzinfo=tzlocal()),
    # 'ResponseMetadata': {'RequestId': '[..]', 
    #                      'HTTPStatusCode': 200,
    #                      'HTTPHeaders': {'x-amzn-requestid': '[..]',
    #  'content-type': 'application/x-amz-json-1.1', 'content-length': '720',
    #                                      'date': 'Sat, 18 Feb 2023 17:22:14 GMT'}, 'RetryAttempts': 0}}

    kms_secrets = json.loads(get_secret_value_response)
    for secret in SECRETS:
        if secret not in _env:
            _env[secret] = kms_secrets[secret]


def get_env_var(k: str):
    if k not in _env:
        raise Exception(f'{k} was not retrieved')
    return _env[k]


if NO_ENV_FILE:
    get_secrets_from_kms()
else:
    get_secrets_from_env_file()
