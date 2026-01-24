import sqlite3

def add_remaining_comprehensive_blogs():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Jenkins blog with complete setup
    jenkins_blog = {
        "title": "Jenkins Complete Setup Guide: CI/CD Pipeline Installation and Configuration",
        "content": """Jenkins is the leading open-source automation server for building, testing, and deploying software. This guide provides complete installation and configuration instructions for production-ready CI/CD pipelines.

## Installation Instructions

### Ubuntu/Debian
```bash
# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Java (required)
sudo apt update
sudo apt install openjdk-11-jdk

# Install Jenkins
sudo apt install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Docker Installation
```bash
# Run Jenkins in Docker
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins/jenkins:lts

# Get initial password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
        - containerPort: 8080
        - containerPort: 50000
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-home
        persistentVolumeClaim:
          claimName: jenkins-pvc
```

## Essential Plugins Installation
```bash
# Install via Jenkins CLI
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin git
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin pipeline-stage-view
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin docker-workflow
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin kubernetes
```

## Pipeline Configuration

### Declarative Pipeline Example
```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'myapp'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/user/repo.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'test-results.xml'
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    def image = docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}")
                    docker.withRegistry('https://' + DOCKER_REGISTRY, 'docker-registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'kubectl apply -f k8s/'
                sh "kubectl set image deployment/myapp myapp=${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext (
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

## Security Configuration
```bash
# Enable security
# Navigate to Manage Jenkins > Configure Global Security

# Authentication: Jenkins' own user database
# Authorization: Matrix-based security

# Create users and assign roles
# Admin: Overall/Administer
# Developer: Job/Build, Job/Read
# Viewer: Overall/Read
```

## Backup and Disaster Recovery
```bash
# Backup Jenkins home
sudo tar -czf jenkins-backup-$(date +%Y%m%d).tar.gz /var/lib/jenkins/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/jenkins"
JENKINS_HOME="/var/lib/jenkins"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
sudo tar -czf $BACKUP_DIR/jenkins-$DATE.tar.gz $JENKINS_HOME
find $BACKUP_DIR -name "jenkins-*.tar.gz" -mtime +7 -delete
```

## Performance Optimization
```bash
# Increase Java heap size
sudo systemctl edit jenkins
# Add:
[Service]
Environment="JAVA_OPTS=-Xmx2048m -XX:MaxPermSize=512m"

# Configure executors
# Manage Jenkins > Configure System > # of executors: 4
```

## Decision Framework
- **Team Size**: 5+ developers → Jenkins recommended
- **Complexity**: Multi-stage pipelines → Jenkins excellent
- **Budget**: Open source → Jenkins perfect
- **Cloud Native**: Kubernetes → Consider Tekton/ArgoCD
- **Simplicity**: Small projects → GitHub Actions might be better

Jenkins provides unmatched flexibility and plugin ecosystem for complex CI/CD requirements.""",
        "author": "DevOps Engineering Team"
    }
    
    # Prometheus blog
    prometheus_blog = {
        "title": "Prometheus Monitoring: Complete Installation and Configuration Guide",
        "content": """Prometheus is a powerful open-source monitoring and alerting toolkit designed for reliability and scalability. This comprehensive guide covers installation, configuration, and best practices for production monitoring.

## Installation Instructions

### Binary Installation (Linux)
```bash
# Create prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus

# Create directories
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus

# Download Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz

# Install binaries
sudo cp prometheus-2.40.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.40.0.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool

# Copy configuration
sudo cp -r prometheus-2.40.0.linux-amd64/consoles /etc/prometheus
sudo cp -r prometheus-2.40.0.linux-amd64/console_libraries /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

### Docker Installation
```bash
# Run Prometheus in Docker
docker run -d \\
  --name prometheus \\
  -p 9090:9090 \\
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \\
  prom/prometheus

# With persistent storage
docker run -d \\
  --name prometheus \\
  -p 9090:9090 \\
  -v prometheus-data:/prometheus \\
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \\
  prom/prometheus --storage.tsdb.path=/prometheus --web.console.libraries=/etc/prometheus/console_libraries --web.console.templates=/etc/prometheus/consoles
```

### Kubernetes Installation
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--web.console.libraries=/etc/prometheus/console_libraries'
          - '--web.console.templates=/etc/prometheus/consoles'
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        persistentVolumeClaim:
          claimName: prometheus-pvc
```

## Configuration

### Basic prometheus.yml
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'application'
    static_configs:
      - targets: ['app1:8080', 'app2:8080']
    metrics_path: /metrics
    scrape_interval: 30s
```

### Service Discovery
```yaml
# Kubernetes service discovery
- job_name: 'kubernetes-pods'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
    action: replace
    target_label: __metrics_path__
    regex: (.+)
```

## Essential Exporters

### Node Exporter (System Metrics)
```bash
# Install Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
tar xvf node_exporter-1.5.0.linux-amd64.tar.gz
sudo cp node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

### Application Metrics
```python
# Python application with Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('app_request_duration_seconds', 'Request latency')

@REQUEST_LATENCY.time()
def process_request():
    REQUEST_COUNT.labels(method='GET', endpoint='/api/users').inc()
    # Your application logic here
    time.sleep(0.1)

# Metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()
```

## Alerting Rules
```yaml
# rules/alerts.yml
groups:
- name: example
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
```

## Grafana Integration
```bash
# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Access: http://localhost:3000 (admin/admin)
```

## Production Best Practices
- **Retention**: Configure appropriate data retention periods
- **Security**: Enable authentication and HTTPS
- **High Availability**: Run multiple Prometheus instances
- **Federation**: Aggregate metrics from multiple Prometheus servers
- **Backup**: Regular backup of Prometheus data directory

Prometheus provides comprehensive monitoring capabilities essential for maintaining reliable, scalable applications in production environments.""",
        "author": "Site Reliability Engineering Team"
    }
    
    cursor.execute('''
        INSERT INTO blogs (title, content, author)
        VALUES (?, ?, ?)
    ''', (jenkins_blog['title'], jenkins_blog['content'], jenkins_blog['author']))
    
    cursor.execute('''
        INSERT INTO blogs (title, content, author)
        VALUES (?, ?, ?)
    ''', (prometheus_blog['title'], prometheus_blog['content'], prometheus_blog['author']))
    
    conn.commit()
    conn.close()
    print("Successfully added Jenkins and Prometheus comprehensive blogs!")

if __name__ == "__main__":
    add_remaining_comprehensive_blogs()
