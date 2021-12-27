from aws_cdk import (
    aws_ec2 as ec2,
    core
)

from infrastructure.utils.utils import tag_all_subnets


class VpcStack(core.NestedStack):
    def __init__(self, scope: core.Construct, id: str, params,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.nats_number = params.vpc.get("nats_number", 0)
        if self.nats_number == 0:
            self.vpc = ec2.Vpc(
                self,
                "VPC",
                nat_gateways=self.nats_number,
                max_azs=params.vpc.az_number,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        cidr_mask=24,
                        name='VPC-Public-Subnet',
                        subnet_type=ec2.SubnetType.PUBLIC,
                    ),
                    ec2.SubnetConfiguration(
                        cidr_mask=24,
                        name='VPC-Private-Subnet',
                        subnet_type=ec2.SubnetType.ISOLATED,
                    )
                ],
                enable_dns_support=True,
                enable_dns_hostnames=True
            )
        else:
            self.vpc = ec2.Vpc(
                self,
                "VPC",
                nat_gateways=self.nats_number,
                max_azs=params.vpc.az_number,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        cidr_mask=24,
                        name='VPC-Public-Subnet',
                        subnet_type=ec2.SubnetType.PUBLIC,
                    ),
                    ec2.SubnetConfiguration(
                        cidr_mask=24,
                        name='VPC-Private-Subnet',
                        subnet_type=ec2.SubnetType.ISOLATED,
                    ),
                    ec2.SubnetConfiguration(
                        cidr_mask=24,
                        name='VPC-Natted-Subnet',
                        subnet_type=ec2.SubnetType.PRIVATE,
                    )
                ],
                enable_dns_support=True,
                enable_dns_hostnames=True
            )

        tag_all_subnets(self.vpc.private_subnets,
                        f"kubernetes.io/cluster/{params.eks.cluster_name}", "shared")
