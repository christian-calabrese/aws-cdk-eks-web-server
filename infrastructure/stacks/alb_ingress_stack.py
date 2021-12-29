from aws_cdk import (
    aws_iam as iam,
    aws_eks as eks,
    core,
)


class ALBIngressController(core.Construct):

    def __init__(self, scope: core.Construct, id: str, params, cluster: eks.Cluster) -> None:
        super().__init__(scope, id)
        self.cluster = cluster

        iam_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateServiceLinkedRole",
                        "ec2:DescribeAccountAttributes",
                        "ec2:DescribeAddresses",
                        "ec2:DescribeAvailabilityZones",
                        "ec2:DescribeInternetGateways",
                        "ec2:DescribeVpcs",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeInstances",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DescribeTags",
                        "ec2:GetCoipPoolUsage",
                        "ec2:DescribeCoipPools",
                        "elasticloadbalancing:DescribeLoadBalancers",
                        "elasticloadbalancing:DescribeLoadBalancerAttributes",
                        "elasticloadbalancing:DescribeListeners",
                        "elasticloadbalancing:DescribeListenerCertificates",
                        "elasticloadbalancing:DescribeSSLPolicies",
                        "elasticloadbalancing:DescribeRules",
                        "elasticloadbalancing:DescribeTargetGroups",
                        "elasticloadbalancing:DescribeTargetGroupAttributes",
                        "elasticloadbalancing:DescribeTargetHealth",
                        "elasticloadbalancing:DescribeTags"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "cognito-idp:DescribeUserPoolClient",
                        "acm:ListCertificates",
                        "acm:DescribeCertificate",
                        "iam:ListServerCertificates",
                        "iam:GetServerCertificate",
                        "waf-regional:GetWebACL",
                        "waf-regional:GetWebACLForResource",
                        "waf-regional:AssociateWebACL",
                        "waf-regional:DisassociateWebACL",
                        "wafv2:GetWebACL",
                        "wafv2:GetWebACLForResource",
                        "wafv2:AssociateWebACL",
                        "wafv2:DisassociateWebACL",
                        "shield:GetSubscriptionState",
                        "shield:DescribeProtection",
                        "shield:CreateProtection",
                        "shield:DeleteProtection"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                        "ec2:RevokeSecurityGroupIngress"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateSecurityGroup"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateTags"
                    ],
                    "Resource": "arn:aws:ec2:*:*:security-group/*",
                    "Condition": {
                        "StringEquals": {
                            "ec2:CreateAction": "CreateSecurityGroup"
                        },
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateTags",
                        "ec2:DeleteTags"
                    ],
                    "Resource": "arn:aws:ec2:*:*:security-group/*",
                    "Condition": {
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "true",
                            "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                        "ec2:RevokeSecurityGroupIngress",
                        "ec2:DeleteSecurityGroup"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Null": {
                            "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:CreateLoadBalancer",
                        "elasticloadbalancing:CreateTargetGroup"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:CreateListener",
                        "elasticloadbalancing:DeleteListener",
                        "elasticloadbalancing:CreateRule",
                        "elasticloadbalancing:DeleteRule"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:RemoveTags"
                    ],
                    "Resource": [
                        "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*",
                        "arn:aws:elasticloadbalancing:*:*:loadbalancer/net/*/*",
                        "arn:aws:elasticloadbalancing:*:*:loadbalancer/app/*/*"
                    ],
                    "Condition": {
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "true",
                            "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:RemoveTags"
                    ],
                    "Resource": [
                        "arn:aws:elasticloadbalancing:*:*:listener/net/*/*/*",
                        "arn:aws:elasticloadbalancing:*:*:listener/app/*/*/*",
                        "arn:aws:elasticloadbalancing:*:*:listener-rule/net/*/*/*",
                        "arn:aws:elasticloadbalancing:*:*:listener-rule/app/*/*/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:ModifyLoadBalancerAttributes",
                        "elasticloadbalancing:SetIpAddressType",
                        "elasticloadbalancing:SetSecurityGroups",
                        "elasticloadbalancing:SetSubnets",
                        "elasticloadbalancing:DeleteLoadBalancer",
                        "elasticloadbalancing:ModifyTargetGroup",
                        "elasticloadbalancing:ModifyTargetGroupAttributes",
                        "elasticloadbalancing:DeleteTargetGroup"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Null": {
                            "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:RegisterTargets",
                        "elasticloadbalancing:DeregisterTargets"
                    ],
                    "Resource": "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:SetWebAcl",
                        "elasticloadbalancing:ModifyListener",
                        "elasticloadbalancing:AddListenerCertificates",
                        "elasticloadbalancing:RemoveListenerCertificates",
                        "elasticloadbalancing:ModifyRule"
                    ],
                    "Resource": "*"
                }
            ]
        }

        cluster_role_manifest = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "alb-ingress-controller",
                "labels": {
                    "app.kubernetes.io/name": "alb-ingress-controller"
                }
            },
            "rules": [{
                "apiGroups": [
                    "",
                    "extensions",
                    "networking.k8s.io",
                    "elbv2.k8s.aws"
                ],
                "resources": [
                    "configmaps",
                    "endpoints",
                    "events",
                    "ingresses",
                    "ingressclasses",
                    "ingresses/status",
                    "services",
                    "pods/status",
                    "nodes",
                    "pods",
                    "secrets",
                    "services",
                    "namespaces",
                    "targetgroupbindings"
                ],
                "verbs": [
                    "create",
                    "get",
                    "list",
                    "update",
                    "watch",
                    "patch"
                ]
            }]
        }

        cluster_role_binding_manifest = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "alb-ingress-controller",
                "labels": {
                    "app.kubernetes.io/name": "alb-ingress-controller"
                }
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "alb-ingress-controller"
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "alb-ingress-controller",
                    "namespace": "kube-system"
                }
            ]
        }

        service_account_manifest = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "alb-ingress-controller",
                "labels": {
                    "app.kubernetes.io/name": "alb-ingress-controller"
                },
                "namespace": "kube-system"
            }
        }

        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "alb-ingress-controller",
                "labels": {
                    "app.kubernetes.io/name": "alb-ingress-controller"
                },
                "namespace": "kube-system"
            },
            "spec": {
                "selector": {"matchLabels": {"app.kubernetes.io/name": "alb-ingress-controller"}},
                "template": {
                    "metadata": {"labels": {"app.kubernetes.io/name": "alb-ingress-controller"}},
                    "spec": {
                        "containers": [{
                            "name": "alb-ingress-controller",
                            "args": [
                                '--ingress-class=alb',
                                '--cluster-name={}'.format(self.cluster.cluster_name),
                                '--aws-vpc-id={}'.format(self.cluster.vpc.vpc_id)
                            ],
                            "image": "docker.io/amazon/aws-alb-ingress-controller:v2.2.0",
                        }
                        ],
                        "serviceAccountName": "alb-ingress-controller"
                    }
                }
            }
        }

        '''
        service_acct = eks.ServiceAccount(
            self, "ALBIngressSA",
            cluster=self.cluster,
        )

        for statement in iam_policy["Statement"]:
            #service_acct.add_to_principal_policy(iam.PolicyStatement.from_json(statement))
            self.cluster.role.add_to_principal_policy(iam.PolicyStatement.from_json(statement))
            self.cluster.default_nodegroup.role.add_to_principal_policy(iam.PolicyStatement.from_json(statement))

        
        alb_ingress_access_manifests = eks.KubernetesManifest(self, "ClusterRoleALB", cluster=self.cluster,
                                                              manifest=[cluster_role_manifest,
                                                                        cluster_role_binding_manifest,
                                                                        service_account_manifest])

        self.alb_controller_chart = self.cluster.add_helm_chart(
            "SimpleEKS-EKS-ALBController-HelmChart",
            chart="aws-load-balancer-controller",
            namespace="kube-system",
            repository="https://aws.github.io/eks-charts",
            timeout=core.Duration.minutes(10),
            values={
                "clusterName": self.cluster.cluster_name,
                "serviceAccount.create": False,
                "serviceAccount.name": service_acct.service_account_name
            }
        )'''

        alb_controller = eks.AlbController(self, "ALBIngressDeployment", cluster=cluster, version=eks.AlbControllerVersion.V2_3_0)

        # alb_ingress_deployment = eks.KubernetesManifest(self, "ALBIngressDeployment", cluster=self.cluster,
        #                                               manifest=[deployment_manifest])
