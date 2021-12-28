from aws_cdk import (
    aws_ec2 as ec2,
    core
)


def tag_all_subnets(subnets, tag_name, tag_value):
    for subnet in subnets:
        core.Tags.of(subnet).add(tag_name, tag_value)
