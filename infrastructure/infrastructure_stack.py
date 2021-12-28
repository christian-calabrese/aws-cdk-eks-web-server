from aws_cdk import (
    core as cdk
)

from infrastructure.stacks.eks_stack import EksStack
from infrastructure.stacks.pipeline_stack import PipelineStack
from infrastructure.stacks.vpc_stack import VpcStack


class InfrastructureStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, params, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc_stack = VpcStack(scope=self, id="VpcStack", params=params)
        self.eks_stack = EksStack(scope=self, id="EKSStack", params=params,
                                  vpc_stack=self.vpc_stack)

        if params.get("ci_cd_enabled", False):
            self.pipeline_stack = PipelineStack(scope=self, id="PipelineStack", params=params, eks_stack=self.eks_stack)
