import sqlite3

def create_comprehensive_blogs():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Clear existing blogs
    cursor.execute("DELETE FROM blogs")
    
    comprehensive_blogs = [
        {
            "title": "Docker Complete Guide: Installation, Setup, and Production Best Practices",
            "content": """Docker has revolutionized software deployment through containerization technology. This comprehensive guide covers everything engineers need to make informed decisions about Docker adoption.

## What is Docker?

Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers. Unlike virtual machines, containers share the host OS kernel, making them more efficient and faster to start.

**Key Benefits:**
- **Consistency**: "Works on my machine" becomes "works everywhere"
- **Efficiency**: 10x faster startup than VMs, minimal resource overhead
- **Scalability**: Easy horizontal scaling with orchestration tools
- **Isolation**: Applications run in isolated environments
- **Portability**: Run anywhere - development, testing, production

## Installation Instructions

### Ubuntu/Debian
```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### CentOS/RHEL
```bash
# Install required packages
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

### macOS
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop from:
# https://desktop.docker.com/mac/main/amd64/Docker.dmg

# Verify installation
docker --version
```

### Windows
```powershell
# Using Chocolatey
choco install docker-desktop

# Or download Docker Desktop from:
# https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

# Enable WSL 2 backend for better performance
wsl --install
```

## Essential Docker Commands

### Container Management
```bash
# Run a container
docker run -d --name myapp -p 8080:80 nginx

# List running containers
docker ps

# List all containers
docker ps -a

# Stop a container
docker stop myapp

# Remove a container
docker rm myapp

# Execute commands in running container
docker exec -it myapp bash
```

### Image Management
```bash
# Pull an image
docker pull ubuntu:20.04

# List images
docker images

# Build an image
docker build -t myapp:v1.0 .

# Remove an image
docker rmi myapp:v1.0

# Tag an image
docker tag myapp:v1.0 registry.com/myapp:v1.0
```

## Creating Your First Dockerfile

```dockerfile
# Use official Node.js runtime as base image
FROM node:16-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

# Start application
CMD ["npm", "start"]
```

## Docker Compose for Multi-Container Applications

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Production Best Practices

### Security
```bash
# Use non-root users
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Scan for vulnerabilities
docker scan myapp:latest

# Use minimal base images
FROM alpine:3.14
FROM scratch  # For static binaries
```

### Performance Optimization
```dockerfile
# Multi-stage builds
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:16-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### Resource Management
```bash
# Limit memory and CPU
docker run -m 512m --cpus="1.5" myapp

# Set restart policies
docker run --restart=unless-stopped myapp
```

## Monitoring and Logging

```bash
# View container logs
docker logs -f myapp

# Monitor resource usage
docker stats

# Export container filesystem changes
docker diff myapp

# Inspect container details
docker inspect myapp
```

## Decision Matrix: When to Use Docker

| Use Case | Docker Fit | Alternative |
|----------|------------|-------------|
| Microservices | ✅ Excellent | Kubernetes |
| CI/CD Pipelines | ✅ Excellent | Native runners |
| Development Environment | ✅ Excellent | Vagrant |
| Legacy Monoliths | ⚠️ Moderate | VM migration |
| High-Performance Computing | ❌ Poor | Bare metal |

## Common Issues and Solutions

### Issue: Container exits immediately
```bash
# Debug with interactive mode
docker run -it myapp sh

# Check logs
docker logs myapp
```

### Issue: Permission denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/files

# Or run with user mapping
docker run -u $(id -u):$(id -g) myapp
```

### Issue: Out of disk space
```bash
# Clean up unused resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

## Cost Analysis

**Development Environment:**
- Time saved: 60-80% faster environment setup
- Consistency: 95% reduction in "works on my machine" issues
- Resource usage: 50% less than VMs

**Production Deployment:**
- Infrastructure costs: 30-50% reduction vs VMs
- Deployment speed: 10x faster than traditional methods
- Scaling efficiency: Near-instant horizontal scaling

## Migration Strategy

1. **Assessment Phase** (Week 1-2)
   - Inventory existing applications
   - Identify containerization candidates
   - Plan resource requirements

2. **Pilot Project** (Week 3-4)
   - Containerize one non-critical application
   - Establish CI/CD pipeline
   - Train development team

3. **Gradual Migration** (Month 2-6)
   - Containerize applications by priority
   - Implement monitoring and logging
   - Optimize for production

4. **Full Adoption** (Month 6+)
   - All new applications containerized
   - Legacy applications migrated
   - Advanced orchestration with Kubernetes

Docker transforms how we build, ship, and run applications. With proper implementation, it delivers significant improvements in development velocity, deployment consistency, and operational efficiency.""",
            "author": "DevOps Engineering Team"
        },
        
        {
            "title": "Kubernetes Production Setup: Complete Installation and Configuration Guide",
            "content": """Kubernetes has become the de facto standard for container orchestration. This comprehensive guide provides everything needed to make informed decisions about Kubernetes adoption and successful implementation.

## Understanding Kubernetes

Kubernetes (K8s) is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications across clusters of machines.

**Core Benefits:**
- **Auto-scaling**: Horizontal and vertical pod autoscaling
- **Self-healing**: Automatic restart, replacement, and rescheduling
- **Service discovery**: Built-in load balancing and DNS
- **Rolling updates**: Zero-downtime deployments
- **Resource optimization**: Efficient resource utilization

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   Master Node   │    │   Worker Node   │
│                 │    │                 │
│ • API Server    │◄──►│ • Kubelet       │
│ • etcd          │    │ • Kube-proxy    │
│ • Scheduler     │    │ • Container     │
│ • Controller    │    │   Runtime       │
└─────────────────┘    └─────────────────┘
```

## Installation Options

### 1. Production-Ready Cluster (kubeadm)

#### Prerequisites
```bash
# All nodes: Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Install container runtime (containerd)
sudo apt update
sudo apt install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd
```

#### Install Kubernetes Components
```bash
# Add Kubernetes repository
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install kubelet, kubeadm, kubectl
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Enable kubelet
sudo systemctl enable kubelet
```

#### Initialize Master Node
```bash
# Initialize cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Configure kubectl for regular user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install network plugin (Flannel)
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

#### Join Worker Nodes
```bash
# On master, get join command
kubeadm token create --print-join-command

# On worker nodes, run the join command
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

### 2. Development Environment (minikube)

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start cluster
minikube start --driver=docker --memory=4096 --cpus=2

# Enable addons
minikube addons enable dashboard
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3. Cloud-Managed Solutions

#### AWS EKS
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster --name my-cluster --region us-west-2 --nodegroup-name workers --node-type m5.large --nodes 3

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name my-cluster
```

#### Google GKE
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Create cluster
gcloud container clusters create my-cluster --zone us-central1-a --num-nodes 3

# Get credentials
gcloud container clusters get-credentials my-cluster --zone us-central1-a
```

## Essential Kubernetes Resources

### 1. Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

### 2. Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

### 3. ConfigMap and Secret
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgresql://localhost:5432/mydb"
  debug: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=  # base64 encoded
```

### 4. Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
```

## Essential kubectl Commands

### Cluster Management
```bash
# Cluster information
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# Namespace management
kubectl create namespace production
kubectl get namespaces
kubectl config set-context --current --namespace=production
```

### Application Management
```bash
# Deploy applications
kubectl apply -f deployment.yaml
kubectl create deployment nginx --image=nginx

# Scale applications
kubectl scale deployment nginx --replicas=5
kubectl autoscale deployment nginx --cpu-percent=50 --min=1 --max=10

# Update applications
kubectl set image deployment/nginx nginx=nginx:1.22
kubectl rollout status deployment/nginx
kubectl rollout undo deployment/nginx
```

### Debugging and Troubleshooting
```bash
# Get resource information
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f

# Execute commands in pods
kubectl exec -it <pod-name> -- bash
kubectl port-forward <pod-name> 8080:80

# Debug networking
kubectl get services
kubectl get endpoints
kubectl describe ingress
```

## Production Configuration

### 1. Resource Management
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "1000m"
    requests.memory: 200Gi
    limits.cpu: "2000m"
    limits.memory: 400Gi
    persistentvolumeclaims: "10"
```

### 2. Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 3. Pod Security Standards
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

## Monitoring and Observability

### Install Prometheus and Grafana
```bash
# Add Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80
```

### Essential Metrics to Monitor
- **Cluster Health**: Node status, resource utilization
- **Application Performance**: Response time, error rates
- **Resource Usage**: CPU, memory, storage consumption
- **Network**: Ingress/egress traffic, latency

## Backup and Disaster Recovery

### etcd Backup
```bash
# Create etcd snapshot
ETCDCTL_API=3 etcdctl snapshot save backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Restore from snapshot
ETCDCTL_API=3 etcdctl snapshot restore backup.db
```

### Application Data Backup
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command:
            - /bin/bash
            - -c
            - pg_dump $DATABASE_URL > /backup/backup-$(date +%Y%m%d).sql
```

## Cost Optimization Strategies

### 1. Right-sizing Resources
```bash
# Analyze resource usage
kubectl top nodes
kubectl top pods

# Use Vertical Pod Autoscaler
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/latest/download/vpa-v1-crd-gen.yaml
```

### 2. Cluster Autoscaling
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
spec:
  template:
    spec:
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        name: cluster-autoscaler
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
```

## Migration Checklist

### Pre-Migration Assessment
- [ ] Application containerization readiness
- [ ] Network architecture planning
- [ ] Storage requirements analysis
- [ ] Security and compliance requirements
- [ ] Team training and skill assessment

### Migration Phases
1. **Preparation** (2-4 weeks)
   - Set up development/staging clusters
   - Containerize applications
   - Create CI/CD pipelines

2. **Pilot Migration** (2-3 weeks)
   - Migrate non-critical applications
   - Establish monitoring and alerting
   - Document procedures

3. **Production Migration** (4-8 weeks)
   - Migrate critical applications
   - Implement backup and disaster recovery
   - Performance optimization

4. **Optimization** (Ongoing)
   - Cost optimization
   - Security hardening
   - Advanced features implementation

## Decision Framework

| Requirement | Kubernetes Fit | Considerations |
|-------------|----------------|----------------|
| Microservices | ✅ Excellent | Native support |
| Monolithic Apps | ⚠️ Moderate | Requires containerization |
| Stateful Apps | ✅ Good | Use StatefulSets |
| Batch Jobs | ✅ Excellent | Jobs and CronJobs |
| Small Teams | ❌ Overkill | Consider simpler solutions |
| Enterprise Scale | ✅ Excellent | Built for scale |

Kubernetes provides unmatched container orchestration capabilities but requires significant investment in learning and operational overhead. Success depends on proper planning, team training, and gradual adoption.""",
            "author": "Cloud Architecture Team"
        }
    ]
    
    # Insert the first 2 comprehensive blogs
    for blog in comprehensive_blogs:
        cursor.execute('''
            INSERT INTO blogs (title, content, author)
            VALUES (?, ?, ?)
        ''', (blog['title'], blog['content'], blog['author']))
    
    conn.commit()
    conn.close()
    print("Successfully created 2 comprehensive blog posts with installation guides!")

if __name__ == "__main__":
    create_comprehensive_blogs()
