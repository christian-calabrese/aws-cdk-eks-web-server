import os

from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecr_assets as ecr_assets,
    aws_eks as eks,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
    aws_autoscaling as autoscaling,
    core,
)

from infrastructure.stacks.alb_ingress_stack import ALBIngressController
from infrastructure.stacks.metrics_server_stack import MetricsServerManifest
from infrastructure.stacks.vpc_stack import VpcStack


class EksStack(core.NestedStack):

    def __init__(self, scope: core.Construct, id: str, params, vpc_stack: VpcStack,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.params = params
        self.capacity_details = self.determine_cluster_size()
        self.cluster_admin = iam.Role(
            self,
            'AdminRole',
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy")],
            assumed_by=iam.AccountRootPrincipal()
        )

        self.cluster_admin.assume_role_policy.add_statements(iam.PolicyStatement(
            actions=["sts:AssumeRole"],
            effect=iam.Effect.ALLOW,
            principals=[iam.ServicePrincipal("eks.amazonaws.com")]
        ))

        self.cluster = eks.Cluster(
            self, "Simple-EKS-Cluster",
            version=eks.KubernetesVersion.of(self.params.eks.eks_version),
            cluster_name=self.params.eks.cluster_name,
            masters_role=self.cluster_admin,
            vpc=vpc_stack.vpc,
            vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE)],
            **self.capacity_details
        )

        asg_spot = autoscaling.AutoScalingGroup(self, 'AsgSpot',
                                                vpc=self.cluster.vpc,
                                                spot_price='0.1094',
                                                desired_capacity=self.params.eks.spot_instance_count,
                                                max_capacity=10,
                                                instance_type=self.capacity_details["default_capacity_instance"],
                                                update_type=autoscaling.UpdateType.ROLLING_UPDATE,
                                                machine_image=eks.EksOptimizedImage(
                                                    kubernetes_version=eks.KubernetesVersion.of(
                                                        self.params.eks.eks_version).version)

                                                )

        asg_on_demand = autoscaling.AutoScalingGroup(self, 'AsgOnDemand',
                                                     vpc=self.cluster.vpc,
                                                     desired_capacity=self.params.eks.on_demand_instance_count,
                                                     max_capacity=self.params.eks.on_demand_instance_count,
                                                     instance_type=self.capacity_details["default_capacity_instance"],
                                                     update_type=autoscaling.UpdateType.ROLLING_UPDATE,
                                                     machine_image=eks.EksOptimizedImage(
                                                         kubernetes_version=eks.KubernetesVersion.of(
                                                             self.params.eks.eks_version).version)
                                                     )

        asg_spot.scale_on_cpu_utilization("SimpleEKS-ScaleSpotOnCPUUtilization", target_utilization_percent=75)

        self.cluster.connect_auto_scaling_group_capacity(asg_on_demand,
                                                         map_role=True)

        self.cluster.connect_auto_scaling_group_capacity(asg_spot,
                                                         map_role=True)

        # TODO: Cover case in which deploying stack with role
        for user in self.params.eks.privileged_iam_principals.users:
            user_id = user.split("/")[-1].upper()
            self.cluster.aws_auth.add_user_mapping(
                user=iam.User.from_user_arn(self, user_id, user_arn=user),
                groups=["system:masters"])

        for role in self.params.eks.privileged_iam_principals.roles:
            role_id = role.split("/")[-1].upper()
            self.cluster.aws_auth.add_role_mapping(
                role=iam.Role.from_role_arn(self, role_id, role_arn=role),
                groups=["system:masters"])

        if self.params.eks.fargate_enabled:
            self.cluster.add_fargate_profile(
                "FargateEnabled",
                selectors=[
                    eks.Selector(
                        namespace='default',
                        labels={'fargate': 'enabled'}
                    )
                ]
            )

        self.metrics_server_manifest = MetricsServerManifest(self, "SimpleEKS-MetricsServer-Manifest", self.params,
                                                             self.cluster)

        self.prometheus_chart = self.cluster.add_helm_chart(
            "SimpleEKS-EKS-Prometheus-HelmChart",
            release="prometheus",
            chart="prometheus",
            create_namespace=True,
            namespace="prometheus",
            repository="https://prometheus-community.github.io/helm-charts",
            values={
                "alertmanager": {
                    "persistentVolume": {
                        "storageClass": "gp2"
                    }
                },
                "server": {
                    "persistentVolume": {
                        "storageClass": "gp2"
                    }
                },
                "prometheus": {
                    "prometheusSpec": {
                        "additionalScrapeConfigs": [
                            {
                                "job_name": "nginx-ingress",
                                "metrics_path": "/metrics",
                                "scrape_interval": "5s",
                                "static_configs": [
                                    {
                                        "targets": [
                                            "nginx-ingress-controller-metrics:9113"
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        )

        self.grafana_chart = self.cluster.add_helm_chart(
            "SimpleEKS-EKS-Grafana-HelmChart",
            chart="grafana",
            namespace="grafana",
            release="grafana",
            version="6.0.0",
            repository="https://grafana.github.io/helm-charts",
            timeout=core.Duration.minutes(10),
            values={
                "persistence": {
                    "storageClassName": "gp2",
                    "enabled": True
                },
                "adminPassword": "TestPWD!",
                "datasources": {
                    "datasources.yaml": {
                        "apiVersion": 1,
                        "datasources": [
                            {
                                "name": "Prometheus",
                                "type": "prometheus",
                                "url": "http://prometheus-server.prometheus.svc.cluster.local",
                                "access": "proxy",
                                "isDefault": True
                            }
                        ]
                    }
                },
                "dashboards": {
                    "default": {
                        "prometheus-stats": {
                            "gnetId": 1860,
                            "revision": 24,
                            "datasource": "Prometheus"
                        }
                    }
                },
                "service": {
                    "type": "LoadBalancer"
                }
            }
        )

        self.alb_ingress_stack = ALBIngressController(scope=self, id="ALBIngress", params=params,
                                                      cluster=self.cluster)

        docker_image = ecr_assets.DockerImageAsset(
            self, "SimpleEKS-ECR-WebServer-Image",
            directory=f"{os.path.dirname(__file__)}/../../images/web_server",
            file="Dockerfile",
            repository_name=params.eks.container_image_name
        )

        chart_asset = s3_assets.Asset(self, "ChartAsset",
                                      path=f"{os.path.dirname(__file__)}/../../helm/ccekswebserver"
                                      )

        self.web_server_chart = self.cluster.add_helm_chart(
            "SimpleEKS-EKS-WebServer-HelmChart",
            chart_asset=chart_asset,
            namespace="default",
            timeout=core.Duration.minutes(10),
            values={
                "image": {
                    "uri": docker_image.image_uri
                },
                "replicaCount": params.eks.web_server_replicas
            },
            wait=True
        )

    def determine_cluster_size(self):
        if self.params.eks.get("capacity_details", "small") == 'small':
            instance_details = ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL)
        elif self.params.eks.get("capacity_details", "small") == 'large':
            instance_details = ec2.InstanceType.of(ec2.InstanceClass.COMPUTE5, ec2.InstanceSize.LARGE)

        return {'default_capacity': 0, 'default_capacity_instance': instance_details,
                'default_capacity_type': eks.DefaultCapacityType.NODEGROUP}
