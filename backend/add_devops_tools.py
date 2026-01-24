import sqlite3

def add_comprehensive_devops_tools():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Create tools table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT,
            homepage_url TEXT,
            github_url TEXT,
            category TEXT,
            license TEXT,
            pricing_model TEXT,
            logo_url TEXT,
            github_stars INTEGER DEFAULT 0,
            github_forks INTEGER DEFAULT 0,
            last_commit_date TEXT,
            ai_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Comprehensive DevOps tools collection
    tools = [
        # Container & Orchestration
        {
            "name": "Docker",
            "slug": "docker",
            "description": "Platform for developing, shipping, and running applications in containers. Revolutionized software deployment through containerization technology.",
            "homepage_url": "https://www.docker.com",
            "github_url": "https://github.com/moby/moby",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "github_stars": 68000,
            "github_forks": 18500,
            "ai_summary": "Industry-standard containerization platform enabling consistent deployments across environments"
        },
        {
            "name": "Kubernetes",
            "slug": "kubernetes",
            "description": "Production-grade container orchestration system for automating deployment, scaling, and management of containerized applications.",
            "homepage_url": "https://kubernetes.io",
            "github_url": "https://github.com/kubernetes/kubernetes",
            "category": "Container Orchestration",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 105000,
            "github_forks": 38000,
            "ai_summary": "De facto standard for container orchestration in production environments"
        },
        {
            "name": "Podman",
            "slug": "podman",
            "description": "Daemonless container engine for developing, managing, and running OCI Containers. Drop-in replacement for Docker with enhanced security.",
            "homepage_url": "https://podman.io",
            "github_url": "https://github.com/containers/podman",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 22000,
            "github_forks": 2300,
            "ai_summary": "Secure, rootless container engine with Docker compatibility"
        },
        
        # CI/CD & Automation
        {
            "name": "Jenkins",
            "slug": "jenkins",
            "description": "Leading open-source automation server for building, testing, and deploying software with extensive plugin ecosystem.",
            "homepage_url": "https://www.jenkins.io",
            "github_url": "https://github.com/jenkinsci/jenkins",
            "category": "CI/CD",
            "license": "MIT",
            "pricing_model": "free",
            "github_stars": 22000,
            "github_forks": 8500,
            "ai_summary": "Most popular CI/CD platform with 1800+ plugins for comprehensive automation"
        },
        {
            "name": "GitLab CI/CD",
            "slug": "gitlab-ci",
            "description": "Integrated CI/CD platform with built-in Git repository management, issue tracking, and deployment pipelines.",
            "homepage_url": "https://about.gitlab.com",
            "github_url": "https://github.com/gitlabhq/gitlabhq",
            "category": "CI/CD",
            "license": "MIT",
            "pricing_model": "freemium",
            "github_stars": 23500,
            "github_forks": 5800,
            "ai_summary": "Complete DevOps platform with integrated CI/CD, security scanning, and monitoring"
        },
        {
            "name": "GitHub Actions",
            "slug": "github-actions",
            "description": "Native CI/CD and automation platform integrated with GitHub repositories for seamless workflow automation.",
            "homepage_url": "https://github.com/features/actions",
            "github_url": "https://github.com/actions",
            "category": "CI/CD",
            "license": "MIT",
            "pricing_model": "freemium",
            "github_stars": 8500,
            "github_forks": 2100,
            "ai_summary": "GitHub-native automation platform with marketplace of reusable actions"
        },
        {
            "name": "CircleCI",
            "slug": "circleci",
            "description": "Cloud-native CI/CD platform with advanced caching, parallelism, and deployment strategies for fast, reliable builds.",
            "homepage_url": "https://circleci.com",
            "github_url": "https://github.com/circleci",
            "category": "CI/CD",
            "license": "Proprietary",
            "pricing_model": "freemium",
            "github_stars": 1200,
            "github_forks": 450,
            "ai_summary": "High-performance CI/CD with intelligent caching and parallel execution"
        },
        {
            "name": "Tekton",
            "slug": "tekton",
            "description": "Kubernetes-native CI/CD framework providing building blocks for creating flexible, powerful automation systems.",
            "homepage_url": "https://tekton.dev",
            "github_url": "https://github.com/tektoncd/pipeline",
            "category": "CI/CD",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 8200,
            "github_forks": 1700,
            "ai_summary": "Cloud-native CI/CD framework built for Kubernetes environments"
        },
        
        # Infrastructure as Code
        {
            "name": "Terraform",
            "slug": "terraform",
            "description": "Infrastructure as Code tool for building, changing, and versioning infrastructure safely and efficiently across providers.",
            "homepage_url": "https://www.terraform.io",
            "github_url": "https://github.com/hashicorp/terraform",
            "category": "Infrastructure as Code",
            "license": "MPL-2.0",
            "pricing_model": "freemium",
            "github_stars": 41000,
            "github_forks": 9400,
            "ai_summary": "Leading IaC tool supporting 3000+ providers for multi-cloud infrastructure management"
        },
        {
            "name": "Pulumi",
            "slug": "pulumi",
            "description": "Modern Infrastructure as Code using familiar programming languages like Python, TypeScript, Go, and C#.",
            "homepage_url": "https://www.pulumi.com",
            "github_url": "https://github.com/pulumi/pulumi",
            "category": "Infrastructure as Code",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "github_stars": 19000,
            "github_forks": 1100,
            "ai_summary": "Next-generation IaC platform using real programming languages instead of DSLs"
        },
        {
            "name": "Ansible",
            "slug": "ansible",
            "description": "Agentless automation platform for configuration management, application deployment, and orchestration.",
            "homepage_url": "https://www.ansible.com",
            "github_url": "https://github.com/ansible/ansible",
            "category": "Configuration Management",
            "license": "GPL-3.0",
            "pricing_model": "freemium",
            "github_stars": 60000,
            "github_forks": 23500,
            "ai_summary": "Simple, agentless automation tool using YAML playbooks for infrastructure management"
        },
        {
            "name": "Chef",
            "slug": "chef",
            "description": "Configuration management tool that transforms infrastructure into code for automated, testable, and repeatable deployments.",
            "homepage_url": "https://www.chef.io",
            "github_url": "https://github.com/chef/chef",
            "category": "Configuration Management",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "github_stars": 7200,
            "github_forks": 2500,
            "ai_summary": "Ruby-based configuration management with test-driven infrastructure development"
        },
        
        # Monitoring & Observability
        {
            "name": "Prometheus",
            "slug": "prometheus",
            "description": "Open-source monitoring and alerting toolkit with dimensional data model and powerful query language.",
            "homepage_url": "https://prometheus.io",
            "github_url": "https://github.com/prometheus/prometheus",
            "category": "Monitoring",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 52000,
            "github_forks": 8900,
            "ai_summary": "Industry-standard monitoring solution with time-series database and PromQL"
        },
        {
            "name": "Grafana",
            "slug": "grafana",
            "description": "Multi-platform analytics and interactive visualization web application for monitoring and observability.",
            "homepage_url": "https://grafana.com",
            "github_url": "https://github.com/grafana/grafana",
            "category": "Monitoring",
            "license": "AGPL-3.0",
            "pricing_model": "freemium",
            "github_stars": 60000,
            "github_forks": 11800,
            "ai_summary": "Leading visualization platform for metrics, logs, and traces with 150+ data sources"
        },
        {
            "name": "Jaeger",
            "slug": "jaeger",
            "description": "Distributed tracing platform for monitoring and troubleshooting microservices-based distributed systems.",
            "homepage_url": "https://www.jaegertracing.io",
            "github_url": "https://github.com/jaegertracing/jaeger",
            "category": "Observability",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 19000,
            "github_forks": 2300,
            "ai_summary": "CNCF distributed tracing system for microservices observability"
        },
        {
            "name": "Elastic Stack",
            "slug": "elastic-stack",
            "description": "Elasticsearch, Logstash, and Kibana (ELK) stack for search, logging, and analytics at scale.",
            "homepage_url": "https://www.elastic.co",
            "github_url": "https://github.com/elastic/elasticsearch",
            "category": "Logging",
            "license": "Elastic License",
            "pricing_model": "freemium",
            "github_stars": 67000,
            "github_forks": 24000,
            "ai_summary": "Comprehensive search and analytics platform for logs, metrics, and security data"
        },
        {
            "name": "Datadog",
            "slug": "datadog",
            "description": "Cloud-scale monitoring and analytics platform for infrastructure, applications, and logs with AI-powered insights.",
            "homepage_url": "https://www.datadoghq.com",
            "github_url": "https://github.com/DataDog",
            "category": "Monitoring",
            "license": "Proprietary",
            "pricing_model": "paid",
            "github_stars": 2500,
            "github_forks": 800,
            "ai_summary": "Enterprise monitoring platform with machine learning and comprehensive integrations"
        },
        
        # Service Mesh & Networking
        {
            "name": "Istio",
            "slug": "istio",
            "description": "Service mesh platform providing traffic management, security, and observability for microservices architectures.",
            "homepage_url": "https://istio.io",
            "github_url": "https://github.com/istio/istio",
            "category": "Service Mesh",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 34000,
            "github_forks": 7100,
            "ai_summary": "Leading service mesh with advanced traffic management and security policies"
        },
        {
            "name": "Linkerd",
            "slug": "linkerd",
            "description": "Ultralight service mesh for Kubernetes providing reliability, security, and observability without complexity.",
            "homepage_url": "https://linkerd.io",
            "github_url": "https://github.com/linkerd/linkerd2",
            "category": "Service Mesh",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 10000,
            "github_forks": 1300,
            "ai_summary": "Lightweight, security-focused service mesh with minimal operational overhead"
        },
        {
            "name": "Consul",
            "slug": "consul",
            "description": "Service networking solution providing service discovery, configuration, and segmentation across dynamic infrastructure.",
            "homepage_url": "https://www.consul.io",
            "github_url": "https://github.com/hashicorp/consul",
            "category": "Service Discovery",
            "license": "MPL-2.0",
            "pricing_model": "freemium",
            "github_stars": 27000,
            "github_forks": 4400,
            "ai_summary": "Multi-cloud service networking with service discovery and configuration management"
        },
        
        # Security & Compliance
        {
            "name": "Vault",
            "slug": "vault",
            "description": "Secrets management tool for securing, storing, and tightly controlling access to tokens, passwords, and certificates.",
            "homepage_url": "https://www.vaultproject.io",
            "github_url": "https://github.com/hashicorp/vault",
            "category": "Security",
            "license": "MPL-2.0",
            "pricing_model": "freemium",
            "github_stars": 29000,
            "github_forks": 4000,
            "ai_summary": "Enterprise-grade secrets management with dynamic secrets and encryption as a service"
        },
        {
            "name": "Falco",
            "slug": "falco",
            "description": "Runtime security monitoring tool that detects unexpected behavior and security threats in cloud-native environments.",
            "homepage_url": "https://falco.org",
            "github_url": "https://github.com/falcosecurity/falco",
            "category": "Security",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 6500,
            "github_forks": 850,
            "ai_summary": "CNCF runtime security tool for threat detection in Kubernetes and containers"
        },
        {
            "name": "Trivy",
            "slug": "trivy",
            "description": "Comprehensive vulnerability scanner for containers, filesystems, and Git repositories with support for multiple languages.",
            "homepage_url": "https://trivy.dev",
            "github_url": "https://github.com/aquasecurity/trivy",
            "category": "Security",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 21000,
            "github_forks": 2100,
            "ai_summary": "Fast, accurate vulnerability scanner for containers and infrastructure as code"
        },
        
        # GitOps & Deployment
        {
            "name": "ArgoCD",
            "slug": "argocd",
            "description": "Declarative GitOps continuous delivery tool for Kubernetes with automated synchronization and rollback capabilities.",
            "homepage_url": "https://argo-cd.readthedocs.io",
            "github_url": "https://github.com/argoproj/argo-cd",
            "category": "GitOps",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 16000,
            "github_forks": 4800,
            "ai_summary": "Leading GitOps tool for Kubernetes with declarative configuration management"
        },
        {
            "name": "Flux",
            "slug": "flux",
            "description": "GitOps toolkit for keeping Kubernetes clusters in sync with configuration sources and automating updates.",
            "homepage_url": "https://fluxcd.io",
            "github_url": "https://github.com/fluxcd/flux2",
            "category": "GitOps",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 5800,
            "github_forks": 570,
            "ai_summary": "CNCF GitOps toolkit with progressive delivery and multi-tenancy support"
        },
        {
            "name": "Helm",
            "slug": "helm",
            "description": "Package manager for Kubernetes that helps define, install, and upgrade complex Kubernetes applications.",
            "homepage_url": "https://helm.sh",
            "github_url": "https://github.com/helm/helm",
            "category": "Package Management",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 25000,
            "github_forks": 6900,
            "ai_summary": "De facto package manager for Kubernetes with templating and dependency management"
        },
        
        # Cloud Native Storage
        {
            "name": "Rook",
            "slug": "rook",
            "description": "Cloud-native storage orchestrator providing file, block, and object storage services for Kubernetes.",
            "homepage_url": "https://rook.io",
            "github_url": "https://github.com/rook/rook",
            "category": "Storage",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 11000,
            "github_forks": 2600,
            "ai_summary": "CNCF storage orchestrator bringing Ceph, EdgeFS, and Cassandra to Kubernetes"
        },
        {
            "name": "Longhorn",
            "slug": "longhorn",
            "description": "Lightweight, reliable distributed block storage system for Kubernetes with backup, snapshot, and disaster recovery.",
            "homepage_url": "https://longhorn.io",
            "github_url": "https://github.com/longhorn/longhorn",
            "category": "Storage",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 5500,
            "github_forks": 650,
            "ai_summary": "Cloud-native distributed storage with enterprise features for Kubernetes"
        },
        
        # API Gateway & Load Balancing
        {
            "name": "Kong",
            "slug": "kong",
            "description": "Cloud-native API gateway and service mesh built on Nginx with plugins for authentication, rate limiting, and more.",
            "homepage_url": "https://konghq.com",
            "github_url": "https://github.com/Kong/kong",
            "category": "API Gateway",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "github_stars": 37000,
            "github_forks": 4700,
            "ai_summary": "High-performance API gateway with extensive plugin ecosystem"
        },
        {
            "name": "Traefik",
            "slug": "traefik",
            "description": "Modern HTTP reverse proxy and load balancer with automatic service discovery and Let's Encrypt integration.",
            "homepage_url": "https://traefik.io",
            "github_url": "https://github.com/traefik/traefik",
            "category": "Load Balancer",
            "license": "MIT",
            "pricing_model": "freemium",
            "github_stars": 47000,
            "github_forks": 5000,
            "ai_summary": "Cloud-native edge router with automatic HTTPS and dynamic configuration"
        },
        {
            "name": "Envoy",
            "slug": "envoy",
            "description": "High-performance C++ distributed proxy designed for single services and applications, and communication bus.",
            "homepage_url": "https://www.envoyproxy.io",
            "github_url": "https://github.com/envoyproxy/envoy",
            "category": "Proxy",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 23000,
            "github_forks": 4600,
            "ai_summary": "CNCF L7 proxy and communication bus with advanced load balancing"
        }
    ]
    
    # Insert tools
    for tool in tools:
        cursor.execute('''
            INSERT OR REPLACE INTO tools 
            (name, slug, description, homepage_url, github_url, category, license, 
             pricing_model, github_stars, github_forks, ai_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tool['name'], tool['slug'], tool['description'], tool['homepage_url'],
            tool['github_url'], tool['category'], tool['license'], tool['pricing_model'],
            tool['github_stars'], tool['github_forks'], tool['ai_summary']
        ))
    
    conn.commit()
    conn.close()
    print(f"Successfully added {len(tools)} comprehensive DevOps tools!")

if __name__ == "__main__":
    add_comprehensive_devops_tools()
