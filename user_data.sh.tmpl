#!/bin/bash
set -e
su ec2-user
cd /home/ec2-user
echo IMAGE_TAG={{IMAGE_TAG}} > /etc/default/fullstack
source /etc/default/fullstack
mkdir -p "{{DEPLOY_DIR}}"
cd "{{DEPLOY_DIR}}"
cat > docker-compose.yml <<EOF
version: "3.8"
services:
  flaskapp:
    image: {{ECR_BACKEND}}:{{IMAGE_TAG}}
    ports:
      - "5000:5000"
    environment:
      - SQLALCHEMY_DATABASE_URI={{SQLALCHEMY_DATABASE_URI}}
      - JWT_SECRET_KEY={{JWT_SECRET_KEY}}
  frontend:
    image: {{ECR_FRONTEND}}:{{IMAGE_TAG}}
    ports:
      - "80:80"
EOF
# Login to ECR and pull images
echo "Logging into ECR..." >> /tmp/user-data.log
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin "{{ECR_REPO}}"

docker-compose pull
docker-compose up -d 
