import boto3
import json
import os

from aws_cdk import core
from aws_cdk.core import Tags

from infrastructure.infrastructure_stack import InfrastructureStack
from infrastructure.utils.environment import Environment

app = core.App()
env_name = os.environ.get("ENVIRONMENT", "dev")
with open(f"infrastructure/parameters/{env_name}.json", "r") as f:
    params = json.loads(f.read(), object_hook=lambda d: Environment(**d))

if os.path.isfile("infrastructure/parameters/uncommitted/.env.json"):
    with open("infrastructure/parameters/uncommitted/.env.json", "r") as f:
        uncommitted_env = json.loads(f.read())
else:
    secrets_manager = boto3.client("secretsmanager")
    secret = secrets_manager.get_secret_value(
            SecretId=params.github_token_secret_name
        )
    uncommitted_env = json.loads(secret['SecretString'])

params.__dict__.update(uncommitted_env)

main_stack = InfrastructureStack(app, "CC-MainStack",
                                 env=core.Environment(region="eu-west-1"), params=params)
Tags.of(main_stack).add("stack_name", "ChristianCalabreseStack")
app.synth()