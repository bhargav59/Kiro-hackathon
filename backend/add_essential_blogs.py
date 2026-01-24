import sqlite3

def add_essential_blogs():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # AWS blog
    aws_content = """Amazon Web Services (AWS) is the world's most comprehensive cloud platform. This guide provides complete setup instructions and best practices for production AWS deployments.

## Getting Started

### AWS Account Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format
```

### Essential Services Overview

#### EC2 (Elastic Compute Cloud)
```bash
# Launch EC2 instance
aws ec2 run-instances \\
    --image-id ami-0abcdef1234567890 \\
    --count 1 \\
    --instance-type t3.micro \\
    --key-name MyKeyPair \\
    --security-group-ids sg-903004f8 \\
    --subnet-id subnet-6e7f829e

# List instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]'
```

#### S3 (Simple Storage Service)
```bash
# Create bucket
aws s3 mb s3://my-unique-bucket-name

# Upload file
aws s3 cp file.txt s3://my-bucket/

# Sync directory
aws s3 sync ./local-folder s3://my-bucket/remote-folder/

# Set bucket policy
aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json
```

#### RDS (Relational Database Service)
```bash
# Create MySQL database
aws rds create-db-instance \\
    --db-instance-identifier mydb \\
    --db-instance-class db.t3.micro \\
    --engine mysql \\
    --master-username admin \\
    --master-user-password mypassword \\
    --allocated-storage 20

# Create snapshot
aws rds create-db-snapshot \\
    --db-instance-identifier mydb \\
    --db-snapshot-identifier mydb-snapshot-$(date +%Y%m%d)
```

## Infrastructure as Code

### CloudFormation Template
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Basic web application infrastructure'

Parameters:
  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890
      InstanceType: t3.micro
      KeyName: !Ref KeyName
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup

  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web server
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

Outputs:
  WebServerPublicIP:
    Description: Public IP of the web server
    Value: !GetAtt WebServer.PublicIp
```

## Security Best Practices

### IAM (Identity and Access Management)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:Region": "us-west-2"
        }
      }
    }
  ]
}
```

### Security Groups Configuration
```bash
# Create security group
aws ec2 create-security-group \\
    --group-name web-servers \\
    --description "Security group for web servers"

# Add HTTP rule
aws ec2 authorize-security-group-ingress \\
    --group-name web-servers \\
    --protocol tcp \\
    --port 80 \\
    --cidr 0.0.0.0/0

# Add SSH rule (restricted)
aws ec2 authorize-security-group-ingress \\
    --group-name web-servers \\
    --protocol tcp \\
    --port 22 \\
    --cidr 203.0.113.0/24
```

## Monitoring and Logging

### CloudWatch Setup
```bash
# Create custom metric
aws cloudwatch put-metric-data \\
    --namespace "MyApp/Performance" \\
    --metric-data MetricName=ResponseTime,Value=0.25,Unit=Seconds

# Create alarm
aws cloudwatch put-metric-alarm \\
    --alarm-name "High-CPU-Usage" \\
    --alarm-description "Alarm when CPU exceeds 80%" \\
    --metric-name CPUUtilization \\
    --namespace AWS/EC2 \\
    --statistic Average \\
    --period 300 \\
    --threshold 80 \\
    --comparison-operator GreaterThanThreshold
```

## Cost Optimization

### Resource Tagging Strategy
```bash
# Tag resources for cost tracking
aws ec2 create-tags \\
    --resources i-1234567890abcdef0 \\
    --tags Key=Environment,Value=Production Key=Project,Value=WebApp Key=Owner,Value=TeamA

# Set up billing alerts
aws budgets create-budget \\
    --account-id 123456789012 \\
    --budget file://budget.json
```

### Auto Scaling Configuration
```bash
# Create launch template
aws ec2 create-launch-template \\
    --launch-template-name my-template \\
    --launch-template-data file://template-data.json

# Create auto scaling group
aws autoscaling create-auto-scaling-group \\
    --auto-scaling-group-name my-asg \\
    --launch-template LaunchTemplateName=my-template,Version=1 \\
    --min-size 1 \\
    --max-size 5 \\
    --desired-capacity 2 \\
    --vpc-zone-identifier subnet-12345678,subnet-87654321
```

## Decision Framework
- **Startup**: Limited budget → AWS Free Tier + Reserved Instances
- **Enterprise**: Compliance needs → AWS GovCloud or dedicated regions
- **Global**: Multi-region deployment → CloudFront + Route 53
- **Data-intensive**: Big data processing → EMR, Redshift, or Athena
- **Serverless**: Event-driven architecture → Lambda + API Gateway

AWS provides unmatched scalability, reliability, and service breadth for cloud infrastructure needs."""
    
    # MongoDB blog
    mongodb_content = """MongoDB is a popular NoSQL document database designed for scalability and developer productivity. This guide covers installation, configuration, and production deployment strategies.

## Installation Instructions

### Ubuntu/Debian Installation
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongosh --eval 'db.runCommand({ connectionStatus: 1 })'
```

### Docker Installation
```bash
# Run MongoDB container
docker run -d --name mongodb \\
  -p 27017:27017 \\
  -v mongodb-data:/data/db \\
  -e MONGO_INITDB_ROOT_USERNAME=admin \\
  -e MONGO_INITDB_ROOT_PASSWORD=password \\
  mongo:latest

# Connect to MongoDB
docker exec -it mongodb mongosh -u admin -p password
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:latest
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: admin
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: mongodb-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## Configuration

### Production mongod.conf
```yaml
# Network interfaces
net:
  port: 27017
  bindIp: 127.0.0.1,10.0.0.1

# Storage
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2

# Security
security:
  authorization: enabled
  keyFile: /etc/mongodb/keyfile

# Replication
replication:
  replSetName: rs0

# Sharding
sharding:
  clusterRole: shardsvr

# Logging
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
```

## Database Operations

### Basic CRUD Operations
```javascript
// Connect to MongoDB
use myapp

// Create (Insert)
db.users.insertOne({
  name: "John Doe",
  email: "john@example.com",
  age: 30,
  tags: ["developer", "mongodb"]
})

db.users.insertMany([
  { name: "Alice", email: "alice@example.com", age: 25 },
  { name: "Bob", email: "bob@example.com", age: 35 }
])

// Read (Find)
db.users.find({ age: { $gte: 25 } })
db.users.findOne({ email: "john@example.com" })

// Advanced queries
db.users.find({
  $and: [
    { age: { $gte: 25 } },
    { tags: { $in: ["developer"] } }
  ]
}).sort({ age: -1 }).limit(10)

// Update
db.users.updateOne(
  { email: "john@example.com" },
  { $set: { age: 31 }, $push: { tags: "senior" } }
)

db.users.updateMany(
  { age: { $lt: 30 } },
  { $set: { category: "junior" } }
)

// Delete
db.users.deleteOne({ email: "john@example.com" })
db.users.deleteMany({ age: { $lt: 18 } })
```

### Indexing Strategy
```javascript
// Create indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ age: 1, name: 1 })
db.users.createIndex({ tags: 1 })

// Text search index
db.posts.createIndex({ title: "text", content: "text" })

// Geospatial index
db.locations.createIndex({ coordinates: "2dsphere" })

// Partial index
db.users.createIndex(
  { email: 1 },
  { partialFilterExpression: { email: { $exists: true } } }
)

// Check index usage
db.users.find({ email: "john@example.com" }).explain("executionStats")
```

## Application Integration

### Node.js Integration
```javascript
const { MongoClient } = require('mongodb');

class UserService {
  constructor() {
    this.client = new MongoClient('mongodb://localhost:27017');
    this.db = null;
  }

  async connect() {
    await this.client.connect();
    this.db = this.client.db('myapp');
    console.log('Connected to MongoDB');
  }

  async createUser(userData) {
    const result = await this.db.collection('users').insertOne({
      ...userData,
      createdAt: new Date(),
      updatedAt: new Date()
    });
    return result.insertedId;
  }

  async getUserById(id) {
    return await this.db.collection('users').findOne({ _id: id });
  }

  async updateUser(id, updates) {
    const result = await this.db.collection('users').updateOne(
      { _id: id },
      { 
        $set: { ...updates, updatedAt: new Date() }
      }
    );
    return result.modifiedCount > 0;
  }

  async getUsersByAge(minAge, maxAge) {
    return await this.db.collection('users')
      .find({ age: { $gte: minAge, $lte: maxAge } })
      .sort({ age: 1 })
      .toArray();
  }

  async searchUsers(searchTerm) {
    return await this.db.collection('users')
      .find({ $text: { $search: searchTerm } })
      .toArray();
  }
}
```

### Python Integration (PyMongo)
```python
from pymongo import MongoClient
from datetime import datetime
import logging

class UserRepository:
    def __init__(self, connection_string="mongodb://localhost:27017/"):
        self.client = MongoClient(connection_string)
        self.db = self.client.myapp
        self.users = self.db.users
        
    def create_user(self, user_data):
        user_data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email):
        return self.users.find_one({'email': email})
    
    def update_user(self, user_id, updates):
        updates['updated_at'] = datetime.utcnow()
        result = self.users.update_one(
            {'_id': user_id},
            {'$set': updates}
        )
        return result.modified_count > 0
    
    def get_users_paginated(self, page=1, per_page=10):
        skip = (page - 1) * per_page
        users = list(self.users.find().skip(skip).limit(per_page))
        total = self.users.count_documents({})
        return {
            'users': users,
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def aggregate_users_by_age_group(self):
        pipeline = [
            {
                '$group': {
                    '_id': {
                        '$switch': {
                            'branches': [
                                {'case': {'$lt': ['$age', 25]}, 'then': 'young'},
                                {'case': {'$lt': ['$age', 40]}, 'then': 'adult'},
                            ],
                            'default': 'senior'
                        }
                    },
                    'count': {'$sum': 1},
                    'avg_age': {'$avg': '$age'}
                }
            }
        ]
        return list(self.users.aggregate(pipeline))
```

## Replication Setup

### Replica Set Configuration
```javascript
// Initialize replica set
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb1:27017" },
    { _id: 1, host: "mongodb2:27017" },
    { _id: 2, host: "mongodb3:27017" }
  ]
})

// Check replica set status
rs.status()

// Add new member
rs.add("mongodb4:27017")

// Remove member
rs.remove("mongodb4:27017")

// Step down primary
rs.stepDown()
```

## Sharding Configuration

### Shard Cluster Setup
```bash
# Start config servers
mongod --configsvr --replSet configReplSet --port 27019 --dbpath /data/configdb

# Start shard servers
mongod --shardsvr --replSet shard1ReplSet --port 27018 --dbpath /data/shard1
mongod --shardsvr --replSet shard2ReplSet --port 27020 --dbpath /data/shard2

# Start mongos router
mongos --configdb configReplSet/mongodb1:27019,mongodb2:27019,mongodb3:27019 --port 27017

# Add shards
sh.addShard("shard1ReplSet/mongodb1:27018")
sh.addShard("shard2ReplSet/mongodb2:27020")

# Enable sharding on database
sh.enableSharding("myapp")

# Shard collection
sh.shardCollection("myapp.users", { "user_id": 1 })
```

## Performance Optimization

### Query Optimization
```javascript
// Use explain to analyze queries
db.users.find({ age: { $gte: 25 } }).explain("executionStats")

// Optimize with proper indexing
db.users.createIndex({ age: 1, status: 1 })

// Use projection to limit returned fields
db.users.find({ age: { $gte: 25 } }, { name: 1, email: 1, _id: 0 })

// Aggregation pipeline optimization
db.users.aggregate([
  { $match: { age: { $gte: 25 } } },  // Filter early
  { $sort: { age: 1 } },              // Sort before grouping
  { $group: { _id: "$department", count: { $sum: 1 } } }
])
```

## Backup and Recovery

### Backup Strategies
```bash
# mongodump - logical backup
mongodump --host localhost:27017 --db myapp --out /backup/$(date +%Y%m%d)

# Restore from backup
mongorestore --host localhost:27017 --db myapp /backup/20231201/myapp

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

mongodump --host localhost:27017 --out $BACKUP_DIR/backup-$DATE
tar -czf $BACKUP_DIR/backup-$DATE.tar.gz $BACKUP_DIR/backup-$DATE
rm -rf $BACKUP_DIR/backup-$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup-*.tar.gz" -mtime +7 -delete
```

## Decision Framework
- **Document Structure**: Complex nested data → MongoDB excellent
- **Scalability**: Horizontal scaling needs → MongoDB sharding
- **ACID**: Strong consistency required → Consider PostgreSQL
- **Real-time**: High write throughput → MongoDB with proper indexing
- **Analytics**: Complex queries → Consider MongoDB + aggregation pipeline

MongoDB provides flexible document storage with powerful querying capabilities, ideal for modern applications with evolving data structures."""
    
    cursor.execute('''
        INSERT INTO blogs (title, content, author)
        VALUES (?, ?, ?)
    ''', ("AWS Complete Guide: Cloud Infrastructure Setup and Best Practices", aws_content, "Cloud Architecture Team"))
    
    cursor.execute('''
        INSERT INTO blogs (title, content, author)
        VALUES (?, ?, ?)
    ''', ("MongoDB Complete Guide: NoSQL Database Installation and Production Setup", mongodb_content, "Database Engineering Team"))
    
    conn.commit()
    conn.close()
    print("Successfully added AWS and MongoDB comprehensive blogs!")

if __name__ == "__main__":
    add_essential_blogs()
