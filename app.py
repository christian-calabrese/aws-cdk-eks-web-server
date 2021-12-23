import json
import os

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core
from aws_cdk.core import Tags

from infrastructure.infrastructure_stack import InfrastructureStack
from infrastructure.utils.environment import Environment

app = core.App()
env_name = os.environ.get("ENVIRONMENT", "dev")
with open(f"infrastructure/parameters/{env_name}.json", "r") as f:
    params = json.loads(f.read(), object_hook=lambda d: Environment(**d))

with open(f"infrastructure/parameters/uncommitted/.env.json", "r") as f:
    uncommitted_env = json.loads(f.read())

params.__dict__.update(uncommitted_env)

main_stack = InfrastructureStack(app, "SimpleEKS-MainStack",
                                 env=core.Environment(region="eu-west-1"), params=params)
Tags.of(main_stack).add("stack_name", "ChristianCalabreseStack")
app.synth()