# WebServer highly available on Amazon EKS

___

## 1. Developer's guide

The IaC has been developed with AWS CDK and Python. Git Flow has been used in the git repository to achieve a better 
branching strategy.

The architecture can be deployed over different environments and with different parameters. The json parameter files are 
contained in the `/infrastructure/parameters` folder and they are chosen at runtime following the `ENVIRONMENT` 
environment variable.

The repository is split in the following way:

```
root
│   README.md
│   app.py - The entrypoint script
│
└───infrastructure
│   │   infrastructure_stack.py - The architecture's main stack
│   │
│   └───parameters - The folder containing the environment's parameters
│   │    │   dev.json
│   │    │   prod.json
│   │
│   └───stacks - The folder containing the stacks code
│   │    │   vpc_stack.py
│   │    │   eks_stack.py
│   │    │   alb_ingress_stack.py
│   │    │   metrics_server_stack.py
│   │    │   pipeline_stack.py
│   │
│   └───utils - A folder containing utility scripts
└───images
│   │
│   └───web_server - The folder containing the files needed for the docker image build
│        │   Dockerfile
│        │   index.html - The custom index page to be served by the web server
│
└───helm
    │
    └───ccekswebserver - The folder containing the helm charts needed to spin up the web server
```

### Installazione requisiti

1. Install Python (https://www.python.org/downloads/)
2. Install node.js (https://nodejs.org/en/download/)
3. Install the npm dependency of CDK `npm i -g aws-cdk:1.137.0`
4. Install the development dependencies for Python `pip3 install -r requirements-dev.txt`
5. Create a Python virtual environment if it doesn't exist `python3 -m venv ./.venv`
6. Activate the Python virtual environment to avoid the polluting the global environment
    1. Windows `.\.venv\bin\activate`
    2. Unix `source .venv/bin/activate`
7. Install Python's dependencies `pip3 install -r requirements.txt`
8. Set the environment variable ENVIRONMENT to dev or prod - if it doesn't exist, dev is the default
9. If it's the first time that the infrastructure is deployed on the AWS account, [it's important to execute the command](https://docs.aws.amazon.com/cdk/latest/guide/bootstrapping.html) `cdk bootstrap`  
10. Deploy the infrastructure with `cdk deploy`

## 2. Architectural choices

### VPC:

The conformation of the VPC is easily customizable through the use of parameters. The stack that deploys the VPC
always create public and private subnets. The number of availability zones on which subnets are created is driven
from the `az_number` parameter. In a production environment, this parameter is set to `3` to allow deployment
the various resources in high reliability.

Furthermore, to better manage the costs related to the network infrastructure, it is possible to decide through the
`nats_number` parameter the number of nat gateways to deploy. In development environments it is possible to use a single
nat gateway to reduce costs (a nat gateway charges around $ 30 per month on AWS billing). In production,
instead, it is recommended to set the `nats_number` parameter to `3` (one per natted subnet) to avoid cutting
fully access to the internet of the application in case of fail of an AZ.

### Compute:

EKS was chosen as a computing resource on which to host the web server, prometheus and grafana. EKS nodes will be spawned on natted subnets to allow access to different AWS services such as ECR
and the internet.

Additionally, an autoscaling rule has been implemented which scales out when the container reaches 75% of
cpu utilization with a 30 second scale-in and scale-out cooldown. To balance the load towards the pods that host the web server in the different AZs, an Application Load Balancer has been created. To keep EKS costs down, it was
added the possibility to create a part of the nodes in Spot mode. Via the `eks.spot_instance_count`
and `eks.on_demand_instance_count` parameters, you can decide the strategy used by the autoscalers to choose the type of node to
spawn.

### CI/CD:

To meet the CI / CD requirements, it was chosen to create a simple pipeline via the CodePipeline service.
It consists of two phases:

1. Source: the code of this repository is automatically fetched from GitHub (*) at each commit. To allow
    the integration between CodePipeline and GitHub requires using an oAuth token saved in a secret on secrets
    manager before creating the pipeline.
2. Build and deploy: this phase is managed through CodeBuild container based on Amazon Linux 2. Inside of them,
    NodeJs and Python runtimes are installed. The first is necessary for the use of CDK and the second for the
    interpretation of the IaC of this repository.

The advantage of using CDK is in fact the possibility of maintaining a strong synergy between the infrastructure and the
code. In the case of this project, for example, the web server Dockerfile for creating containers, the helm charts and
definition of their infrastructure are included in the same repository, completely avoiding disjoint deployments of the parts.
In fact, CDK will push the docker images to ECR and helm charts to S3 in conjunction with the
`cdk deploy` command. This feature is exploited more when Lambda functions are present.
In fact, it is possible to keep the CDK and Back-End infrastructure code in the same code base and use the same or different
programming languages.

(&ast;) To create the codestar connection between CodePipeline and GitHub, you need to have created a personal access
token on github. This token will be securely preserved in the secret called `simple_eks_secret_github_token`.
The IaC is implemented with the possibility to take this token from the `/infrastructure/parameters/uncommitted/.env.json` file.
As can be seen from the path, this file is not committed to git, so you can use the `example.env.json` file as a base. 
It's also possible to deploy the architecture without the CI/CD stack in such a way that the creation of
a GitHub token is not necessary. To enable/disable its creation, you can change the value of the
`ci_cd_enabled` parameter.

### Possible optimizations:

There are many opportunities for optimization and improvement of the project. 
In this paragraph the most important ones I identified are listed:

1. Testing: the framework used (CDK) allows IaC testing to ensure that the resources created are
    correct in all their parts. To avoid incorrect deployments, you can add a test phase in the pipeline of
    CI/CD to block the deployment process in case of failure. The directory where to implement the tests is already present. 
2. In this moment, the implemented IaC allows access to the web server via the HTTP protocol. It is very important,
    however, to discontinue its use in favor of HTTPS. To do this, one can generate an SSL certificate via AWS
    Certificate Manager. Thanks to the TLS session termination feature of the Load Balancers, it is then possible to enable
    HTTPS easily with the created certificate.

___
<h4 style="text-align: right">Christian Calabrese</h4>
