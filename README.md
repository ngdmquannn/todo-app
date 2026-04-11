# PacToDo - Enterprise 3-Tier Cloud Application

PacToDo is a web application deployed on a production-ready AWS 3-tier architecture, designed to demonstrate how a real-world cloud application is built, scaled, and operated with high availability and minimal operational overhead.

The architecture prioritizes scalability, fault tolerance, security, and cost efficiency, following modern cloud-native best practices.
## 🚀 Quick Start
You can run locally by git clone this project and using docker compose, the application will be running at **http://localhost:80**

```bash
git clone https://gitlab.com/aws-uit/AWS-project.git
cd Fullstack-TodoApp
cp .env.dev .env
docker-compose up --build
# Access: http://localhost
```

**Tech Stack:** React.js + Flask + PostgreSQL

---

## 📋 Project Overview

A full-stack task management application demonstrating production-ready cloud architecture with:

- **3-Tier Architecture** - Presentation, Application, and Data layers
- **Multi-AZ Deployment** - High availability across 2 availability zones
- **Auto-Scaling** - Dynamic instance scaling (2-4 EC2) based on CPU metrics
- **Zero-Downtime Deployments** - Rolling updates with 80% minimum healthy capacity
- **Global CDN** - CloudFront for static and dynamic content delivery
- **Automated CI/CD** - GitLab pipeline from commit to production
- **Infrastructure Monitoring** - CloudWatch dashboards and SNS alerts
- **Security Best Practices** - Private subnets, IAM roles, JWT authentication

---

## ☁️ Cloud Architecture


![Architecture](./report/Architecture.png)

---
### 3-Tier Multi-AZ Design

```
Internet → CloudFront CDN (Edge Cache)
              ↓                    ↓
    ALB Distribution      S3 Distribution (Static)
              ↓
    Application Load Balancer (Cross-AZ)
              ↓
    ┌─────────────────────────────┐
    │  Auto Scaling Group (2-4)   │
    │  ┌──────────┐  ┌──────────┐ │
    │  │ AZ-A     │  │ AZ-B     │ │
    │  │ EC2      │  │ EC2      │ │
    │  │ Docker   │  │ Docker   │ │
    │  └────┬─────┘  └─────┬────┘ │
    └───────┼──────────────┼──────┘
            └──────┬───────┘
                   ↓
         RDS PostgreSQL (Private)
```
## ☁️ Cloud Architecture Breakdown

### AWS Components Overview

| Service | Role | Configuration |
|---------|------|---------------|
| **CloudFront** | CDN | 2 distributions (ALB + S3 origins) |
| **ALB** | Load Balancer | HTTP:80, cross-AZ health checks |
| **ASG** | Auto-Scaling | t3.micro, target 50% CPU |
| **EC2** | Compute | Docker Compose (Flask + React) |
| **ECR** | Container Registry | Private repos (backend/frontend) |
| **RDS** | Database | PostgreSQL db.t3.micro, 20GB |
| **VPC** | Network | 10.0.0.0/16, public + private subnets |
| **NAT Gateway** | Outbound Access | Private subnet internet routing |
| **CloudWatch** | Monitoring | Metrics, logs, alarms |
| **CloudTrail** | Audit Logs | API call tracking to S3 |
---

## 🌍 Edge & Traffic Entry

- **CloudFront** acts as the global entry point, accelerating content delivery by caching static assets from **S3** and forwarding dynamic requests to the application layer.

- The **Application Load Balancer** **(ALB)** receives traffic from **CloudFront**, performs health checks, and distributes requests across healthy instances in multiple Availability Zones.

---

## 🖥️ Compute & Application Layer

- **EC2** instances run Dockerized frontend and backend services, deployed across multiple Availability Zones, providing resilience against instance and AZ failures.

- The **Auto Scaling Group (ASG)** manages compute capacity, automatically scaling between *2 and 4 instances based on load*. Implementing **rolling deployments** with **ALB** health checks ensure zero-downtime application releases.

---

## 🐳 Container & Image Management

- **Amazon Elastic Container Registry (ECR)** stores versioned Docker images for both frontend and backend services. **GitLab CI** builds and pushes new images to **ECR** on every commit.

- **EC2 instances** automatically pull updated images during scale-out events or **ASG instance refresh**.

---

## 🗄️ Data & Storage Layer

### **Amazon RDS (PostgreSQL)** serves as the primary system of record.

- The database is hosted in **private subnets** with no public exposure.

- Managed backups, monitoring, and patching reduce operational overhead while ensuring transactional consistency.

### Object Storage: 
**Amazon S3** stores user-uploaded images and static assets.

- **Storage** is fully decoupled from compute resources, allowing independent scaling.

- **CloudFront** caches **S3** content globally to improve performance and reduce backend load.

---

## 🌐 Networking & Security

The architecture runs inside a **Virtual Private Cloud (VPC)** with clear network segmentation into 2 different AZs which each one have:

- **Public subnets** host the Application Load Balancer and NAT Gateway.

- **Private subnets** host EC2 application instances and Amazon RDS.

---

## Security Layers

### Security Groups (Firewall):
- ALB-SG:  0.0.0.0/0 → HTTP:80
-  EC2-SG:  ALB-SG → HTTP:80, Flask:5000
-  RDS-SG:  EC2-SG → PostgreSQL:5432

### Network Isolation:
-  Public:   ALB, NAT Gateway
-  Private:  EC2, RDS (no direct internet)

### Application Security:
- IAM least-privilege roles
---

## 📊 Monitoring, Logging & Auditing

**Amazon CloudWatch** collects metrics from ALB, ASG, EC2, and RDS.

- **Dashboards** provide real-time visibility into system health and performance.

- **Alerts** notify administrators when thresholds are breached.

**AWS CloudTrail** logs all AWS API activity and stores audit records in Amazon S3 for compliance and traceability.

---
## ⚙️ Setup Instructions

### 1. GitLab CI/CD Variables

Configure in **Settings → CI/CD → Variables**:

| Variable | Example |
|----------|---------|
| `AWS_REGION` | `ap-southeast-2` | 
| `ECR_REPO` | `123456789.dkr.ecr.ap-southeast-2.amazonaws.com` | 
| `ECR_BACKEND` | `${ECR_REPO}/todoapp-backend` | 
| `ECR_FRONTEND` | `${ECR_REPO}/todoapp-frontend` | 
| `LT_VERSION` | `lt-0abc123def456` | 
| `ASG_NAME` | `todoapp-production-asg` | 
| `DEPLOY_DIR` | `/opt/todo-app` | 
| `SQLALCHEMY_DATABASE_URI` | `postgresql://admin:pass@rds:5432/todoapp` |
| `JWT_SECRET_KEY` | `your-secret-key-min-32-chars` |

### 2. IAM Role for GitLab Runner

Attach to runner EC2 instance:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ecr:GetAuthorizationToken",
      "ecr:BatchGetImage",
      "ecr:PutImage",
      "ec2:DescribeLaunchTemplates",
      "ec2:DescribeLaunchTemplateVersions",
      "ec2:CreateLaunchTemplateVersion",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:StartInstanceRefresh",
      "autoscaling:DescribeInstanceRefreshes"
    ],
    "Resource": "*"
  }]
}
```
---

## 🔄 CI/CD Pipeline

### Pipeline Architecture

```
Developer Push to main branch
         ↓
GitLab Runner (EC2 with IAM role)
         ↓
    ┌────┴────┐
    ↓         ↓
Build Backend  Build Frontend (Parallel)
    ↓         ↓
    └────┬────┘
         ↓
   Push to ECR (with commit SHA tag)
         ↓
   Render User-Data Template
         ↓
   Create New Launch Template Version
         ↓
   Trigger ASG Instance Refresh
         ↓
   Rolling Update (Zero Downtime)
```

### Stage 1: Build Stage

**Purpose:** Build Docker images and push to Amazon ECR with unique commit SHA tags.

```yaml
backend_build:
  stage: build
  tags: [bastion-runner]  # Uses GitLab runner on EC2
  script:
    # Step 1: Authenticate with ECR using AWS CLI
    - aws ecr get-login-password --region $AWS_REGION | 
      docker login --username AWS --password-stdin $ECR_REPO
    
    # Step 2: Build Docker image with commit SHA as tag (e.g., abc1234)
    - docker build -t $ECR_BACKEND:$CI_COMMIT_SHORT_SHA -f flask/Dockerfile flask/
    
    # Step 3: Push image to ECR repository
    - docker push $ECR_BACKEND:$CI_COMMIT_SHORT_SHA
```
> **Same configuration for frontend.**

**What happens:**
- Both backend and frontend builds run in **parallel** to save time
- Each image is tagged with `$CI_COMMIT_SHORT_SHA` (e.g., `abc1234`) for version tracking
- Images are pushed to ECR by the EC2 Runner.

---
### Stage 2: Deploy Stage (Detailed Explanation)

**Step 1:** Update ASG Launch template with the new user_data with templates using new images from ECR.

```yaml
deploy_staging:
  stage: deploy
  rules:
    - if: '$CI_COMMIT_REF_NAME == "main"'
  before_script:
    - export IMAGE_TAG="$IMAGE_TAG"
    - export DEPLOY_DIR="$DEPLOY_DIR"
    - export AWS_DEFAULT_REGION="$AWS_REGION"
    - export ECR_BACKEND="$ECR_BACKEND"
    - export ECR_FRONTEND="$ECR_FRONTEND"
    - export SQLALCHEMY_DATABASE_URI="$SQLALCHEMY_DATABASE_URI"
    - export JWT_SECRET_KEY="$JWT_SECRET_KEY"
    - export LT_VERSION="$LT_VERSION"
    - export ASG_NAME="$ASG_NAME"
  script:
  - |
    # Render template
    cat ./user_data.sh.tmpl \
      | sed "s|{{IMAGE_TAG}}|$IMAGE_TAG|g" \
      | sed "s|{{ECR_REPO}}|$ECR_REPO|g" \
      | sed "s|{{DEPLOY_DIR}}|$DEPLOY_DIR|g" \
      | sed "s|{{ECR_BACKEND}}|$ECR_BACKEND|g" \
      | sed "s|{{ECR_FRONTEND}}|$ECR_FRONTEND|g" \
      | sed "s|{{SQLALCHEMY_DATABASE_URI}}|$SQLALCHEMY_DATABASE_URI|g" \
      | sed "s|{{JWT_SECRET_KEY}}|$JWT_SECRET_KEY|g" \
      > user-data.sh

      # Base64 encode
      USER_DATA_B64=$(base64 < user-data.sh | tr -d '\n')

      # Get the golden launch template data
      LT_DATA=$(aws ec2 describe-launch-template-versions \
        --launch-template-id "$LT_VERSION" \
        --versions 34 \
        --query 'LaunchTemplateVersions[0].LaunchTemplateData' \
        --output json)

      # Add new UserData to LaunchTemplateData
      LT_DATA_WITH_UD=$(
        echo "$LT_DATA" \
        | jq --arg ud "$USER_DATA_B64" '.UserData = $ud'
      )
      
      # Create new launch template version
      NEW_VERSION=$(aws ec2 create-launch-template-version \
        --launch-template-id "$LT_VERSION" \
        --launch-template-data "$LT_DATA_WITH_UD" \
        --query 'LaunchTemplateVersion.VersionNumber' \
        --output text)
      
      echo "Created launch template version $NEW_VERSION"

```
**Step 2:** Update the ASG:
```yaml
      echo "ASG after update:"
      aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-names "$ASG_NAME" \
        --query 'AutoScalingGroups[0].{LT:LaunchTemplate,IR:NewInstancesProtectedFromScaleIn}' \
        --output json

      echo "Checking existing instance refreshes..."
      aws autoscaling describe-instance-refreshes \
        --auto-scaling-group-name "$ASG_NAME" \
        --max-records 5

      echo "Starting instance refresh..."
      aws autoscaling start-instance-refresh \
        --auto-scaling-group-name "$ASG_NAME" \
        --preferences '{"MinHealthyPercentage":80}' \
        --strategy Rolling

      echo "Instance refresh started"
```
> With the Rolling update strategy, the ASG wait for the new instances to be healthy, then it terminate the old ones
---

### User-Data Template Explained
This use for the ASG to automatically used this predefined script to launch new instances, so I implemented the way to modify the user data to have the latest image pulled from ECR, run the application with docker compose; then I put it in the latest Launch template

**user_data.sh.tmpl**

```bash
#!/bin/bash
set -e

# This script runs when EC2 instance launches

# ============================================
# STEP 1: Authenticate with ECR
# ============================================
aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin {{ECR_REPO}}

# Navigate to deployment directory
cd {{DEPLOY_DIR}}

# ============================================
# STEP 2: Generate docker-compose.yml
# ============================================
cat > docker-compose.yml <<'EOF'
version: "3.8"
services:
  flaskapp:
    image: {{ECR_BACKEND}}:{{IMAGE_TAG}}
    container_name: todoapp-backend
    ports:
      - "5000:5000"
    environment:
      - SQLALCHEMY_DATABASE_URI={{SQLALCHEMY_DATABASE_URI}}
      - JWT_SECRET_KEY={{JWT_SECRET_KEY}}
    restart: unless-stopped

  frontend:
    image: {{ECR_FRONTEND}}:{{IMAGE_TAG}}
    container_name: todoapp-frontend
    ports:
      - "80:80"
    depends_on:
      - flaskapp
    restart: unless-stopped
EOF

# ============================================
# STEP 3: Pull Images and Start Containers
# ============================================
docker-compose pull  # Download images from ECR
docker-compose up -d # Start containers in detached mode
```

**After CI/CD renders it** (example with commit `abc1234`):

```bash
#!/bin/bash
set -e

aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.ap-southeast-2.amazonaws.com

cd /opt/todo-app

cat > docker-compose.yml <<'EOF'
version: "3.8"
services:
  flaskapp:
    image: 123456789.dkr.ecr.ap-southeast-2.amazonaws.com/todoapp-backend:abc1234
    ports: ["5000:5000"]
    environment:
      - SQLALCHEMY_DATABASE_URI=postgresql://admin:pass@rds-endpoint/todoapp
      - JWT_SECRET_KEY=actual-secret-key-here
    restart: unless-stopped

  frontend:
    image: 123456789.dkr.ecr.ap-southeast-2.amazonaws.com/todoapp-frontend:abc1234
    ports: ["80:80"]
    depends_on: [flaskapp]
    restart: unless-stopped
EOF

docker-compose pull && docker-compose up -d
```
---
## Zero-Downtime Updates
1. ASG launches **new instances** with updated Launch Template
2. New instances pull latest Docker images from ECR
3. ALB health checks validate new instances
4. Old instances terminate after new ones are healthy
5. **No traffic interruption** during entire process


---

## 📊 Monitoring & Observability

### CloudWatch Dashboard

```yaml
Metrics Tracked:
  - ASG CPU Utilization (Target: 50%)
  - ALB Response Time (<500ms threshold)
  - Healthy/Unhealthy Host Count
  - RDS CPU, Storage, Connections
  - ECR Pull Requests

Alarms Configured:
  - High_CPU: >70% for 2 minutes → SNS Email
  - Unhealthy_Hosts: >0 for 1 minute → Auto scale-out
  - Low_RDS_Storage: <2GB → Alert team
```

### CloudTrail Audit Logs

- All AWS API calls logged to S3
- Tracks deployments, scaling events, security changes
- Compliance-ready logging (SOC2, PCI-DSS)

---


## 💰 Cost Estimate

**Monthly Total:** ~$151 (ap-southeast-2 region)

| Service | Monthly Cost |
|---------|--------------|
| EC2 (t3.micro × 2-4) + ALB | $42.73 |
| NAT Gateway | $43.36 |
| RDS (db.t3.micro) | $23.20 |
| CloudWatch + CloudTrail | $15.15 |
| CloudFront + S3 + ECR | $26.73 |

---


## 🚀 Project Key Features

- **Zero-Downtime Deployments**:  ASG rolling updates via CI/CD (80% minimum healthy instances)

- **Auto Scaling**:  CPU-based scaling (50% target utilization, 2–4 instances)

- **Global Performance**:  CloudFront CDN caching static content from S3

- **High Availability**:  Multi-AZ deployment behind Application Load Balancer

- **Security by Design**:  Private subnets, IAM roles, ALB ingress, JWT authentication

- **GitOps CI/CD**: Commit → AMI → Launch Template → ASG (≈11 minutes to production)

---

## 🤔 Why Not EKS?

- No Kubernetes control-plane cost  
- Simpler operations and debugging  
- Right-sized for stateless services  
- No deep knowledge to maintain and develop

> **Same reliability. Lower cost. Less complexity.**

---

## 📖 Documentation

**Full Report:** [Project Documentation](./report/report.docx) including:

- Phase 0-4: Complete infrastructure setup
- Detailed architecture diagrams
- Detailed cloud configurations
- Test case validations

**Demo video:** [Project Demo](https://drive.google.com/drive/folders/1SIvacyW3zlPwAyajSgJMdCI0vx-T7AIE?usp=drive_link), containing:
- Local docker-compose 
- CI/CD Pipeline Running demo
- Cloud services walkthrough

