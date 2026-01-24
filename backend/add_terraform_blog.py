import sqlite3

def add_terraform_blog():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    terraform_blog = {
        "title": "Terraform Complete Guide: Infrastructure as Code Installation and Best Practices",
        "content": """Terraform is HashiCorp's infrastructure as code tool that enables you to safely and predictably create, change, and improve infrastructure. This comprehensive guide covers everything needed for successful Terraform adoption.

## What is Terraform?

Terraform is an open-source infrastructure as code software tool that provides a consistent CLI workflow to manage hundreds of cloud services. It codifies cloud APIs into declarative configuration files.

**Key Benefits:**
- **Infrastructure as Code**: Version-controlled infrastructure
- **Multi-Cloud**: Works with AWS, Azure, GCP, and 100+ providers
- **State Management**: Tracks resource state and dependencies
- **Plan and Apply**: Preview changes before execution
- **Collaboration**: Team-friendly with remote state

## Installation Instructions

### Linux (Ubuntu/Debian)
```bash
# Add HashiCorp GPG key
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -

# Add HashiCorp repository
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

# Install Terraform
sudo apt update && sudo apt install terraform

# Verify installation
terraform --version
```

### CentOS/RHEL
```bash
# Add HashiCorp repository
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo

# Install Terraform
sudo yum -y install terraform

# Verify installation
terraform --version
```

### macOS
```bash
# Using Homebrew
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Or download binary
curl -O https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_darwin_amd64.zip
unzip terraform_1.6.0_darwin_amd64.zip
sudo mv terraform /usr/local/bin/
```

### Windows
```powershell
# Using Chocolatey
choco install terraform

# Or using Scoop
scoop install terraform

# Manual installation
# Download from https://www.terraform.io/downloads.html
# Extract to C:\\terraform
# Add to PATH environment variable
```

## Essential Terraform Commands

### Basic Workflow
```bash
# Initialize working directory
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy
```

### Advanced Commands
```bash
# Format configuration files
terraform fmt

# Show current state
terraform show

# List resources in state
terraform state list

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0

# Refresh state
terraform refresh
```

## Basic Configuration Example

### AWS EC2 Instance
```hcl
# Configure the AWS Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# Data sources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

# Resources
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  tags = {
    Name        = "WebServer"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

# Outputs
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.web.public_ip
}
```

## Project Structure Best Practices

```
terraform-project/
├── main.tf              # Main configuration
├── variables.tf         # Input variables
├── outputs.tf          # Output values
├── versions.tf         # Provider versions
├── terraform.tfvars   # Variable values
├── modules/            # Reusable modules
│   ├── vpc/
│   ├── ec2/
│   └── rds/
└── environments/       # Environment-specific configs
    ├── dev/
    ├── staging/
    └── prod/
```

## Remote State Configuration

### AWS S3 Backend
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### Create S3 Backend Resources
```bash
# Create S3 bucket for state
aws s3 mb s3://my-terraform-state

# Enable versioning
aws s3api put-bucket-versioning \\
  --bucket my-terraform-state \\
  --versioning-configuration Status=Enabled

# Create DynamoDB table for locking
aws dynamodb create-table \\
  --table-name terraform-locks \\
  --attribute-definitions AttributeName=LockID,AttributeType=S \\
  --key-schema AttributeName=LockID,KeyType=HASH \\
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## Advanced Features

### Modules
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = var.name
  }
}

# Using the module
module "vpc" {
  source = "./modules/vpc"
  
  name       = "production-vpc"
  cidr_block = "10.0.0.0/16"
}
```

### Workspaces
```bash
# Create workspace
terraform workspace new production

# List workspaces
terraform workspace list

# Switch workspace
terraform workspace select production

# Show current workspace
terraform workspace show
```

## Security Best Practices

### Sensitive Variables
```hcl
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Use in resource
resource "aws_db_instance" "example" {
  password = var.db_password
  # ... other configuration
}
```

### Provider Authentication
```bash
# Environment variables (recommended)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Or use AWS CLI profiles
aws configure --profile terraform
export AWS_PROFILE=terraform
```

## Testing and Validation

### Terraform Validate
```bash
# Check syntax and configuration
terraform validate

# Format code
terraform fmt -recursive

# Security scanning with tfsec
tfsec .

# Policy checking with OPA
opa test policies/
```

### Testing Framework
```bash
# Install Terratest (Go required)
go mod init terraform-test
go get github.com/gruntwork-io/terratest/modules/terraform

# Example test file (test/terraform_test.go)
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
)

func TestTerraformExample(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../",
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)
}
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Terraform
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.6.0
    
    - name: Terraform Init
      run: terraform init
    
    - name: Terraform Plan
      run: terraform plan
    
    - name: Terraform Apply
      if: github.ref == 'refs/heads/main'
      run: terraform apply -auto-approve
```

## Cost Optimization

### Resource Tagging
```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}

resource "aws_instance" "example" {
  # ... configuration
  tags = local.common_tags
}
```

### Cost Estimation
```bash
# Install Infracost
curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh

# Generate cost estimate
infracost breakdown --path .

# Compare costs
infracost diff --path .
```

## Troubleshooting Common Issues

### State Lock Issues
```bash
# Force unlock (use carefully)
terraform force-unlock LOCK_ID

# Check state
terraform state list
terraform state show aws_instance.example
```

### Import Existing Resources
```bash
# Import EC2 instance
terraform import aws_instance.example i-1234567890abcdef0

# Generate configuration from import
terraform show -no-color > imported.tf
```

### Debugging
```bash
# Enable debug logging
export TF_LOG=DEBUG
export TF_LOG_PATH=./terraform.log

# Trace provider calls
export TF_LOG_PROVIDER=TRACE
```

## Migration Strategies

### From Manual Infrastructure
1. **Inventory**: Document existing resources
2. **Import**: Use terraform import for critical resources
3. **Recreate**: For non-critical resources, recreate with Terraform
4. **Validate**: Ensure imported resources match actual state

### From Other IaC Tools
1. **Parallel Deployment**: Run both tools temporarily
2. **Gradual Migration**: Move resources incrementally
3. **State Migration**: Use terraform import extensively
4. **Validation**: Compare outputs and configurations

## Decision Matrix

| Use Case | Terraform Fit | Alternative |
|----------|---------------|-------------|
| Multi-cloud | ✅ Excellent | Cloud-specific tools |
| AWS Only | ✅ Good | CloudFormation |
| Simple Infrastructure | ⚠️ Moderate | Manual setup |
| Complex Dependencies | ✅ Excellent | Pulumi |
| Team Collaboration | ✅ Excellent | Manual processes |

Terraform revolutionizes infrastructure management through code, providing consistency, version control, and collaboration capabilities essential for modern cloud operations.""",
        "author": "Infrastructure Engineering Team"
    }
    
    cursor.execute('''
        INSERT INTO blogs (title, content, author)
        VALUES (?, ?, ?)
    ''', (terraform_blog['title'], terraform_blog['content'], terraform_blog['author']))
    
    conn.commit()
    conn.close()
    print("Successfully added Terraform comprehensive blog!")

if __name__ == "__main__":
    add_terraform_blog()
