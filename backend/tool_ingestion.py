"""
Tool Ingestion Pipeline for CloudEngineered Platform

Automated ingestion of 100+ DevOps tools from GitHub API.
Fetches repository metadata, generates descriptions, and upserts into the database.
"""

import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Comprehensive DevOps tool registry with GitHub repos
# Format: {"github": "owner/repo", "name": "Display Name", "category": "Category", "pricing_model": "free|freemium|paid|open_source"}
DEVOPS_TOOLS: List[Dict[str, str]] = [
    # ===== CONTAINERS =====
    {"github": "moby/moby", "name": "Docker", "category": "Containers", "pricing_model": "freemium"},
    {"github": "containers/podman", "name": "Podman", "category": "Containers", "pricing_model": "open_source"},
    {"github": "containerd/containerd", "name": "containerd", "category": "Containers", "pricing_model": "open_source"},
    {"github": "cri-o/cri-o", "name": "CRI-O", "category": "Containers", "pricing_model": "open_source"},
    {"github": "containers/buildah", "name": "Buildah", "category": "Containers", "pricing_model": "open_source"},
    {"github": "GoogleContainerTools/kaniko", "name": "Kaniko", "category": "Containers", "pricing_model": "open_source"},
    {"github": "containers/skopeo", "name": "Skopeo", "category": "Containers", "pricing_model": "open_source"},
    {"github": "GoogleContainerTools/distroless", "name": "Distroless", "category": "Containers", "pricing_model": "open_source"},

    # ===== CONTAINER ORCHESTRATION =====
    {"github": "kubernetes/kubernetes", "name": "Kubernetes", "category": "Orchestration", "pricing_model": "open_source"},
    {"github": "k3s-io/k3s", "name": "k3s", "category": "Orchestration", "pricing_model": "open_source"},
    {"github": "k0sproject/k0s", "name": "k0s", "category": "Orchestration", "pricing_model": "open_source"},
    {"github": "canonical/microk8s", "name": "MicroK8s", "category": "Orchestration", "pricing_model": "open_source"},
    {"github": "rancher/rancher", "name": "Rancher", "category": "Orchestration", "pricing_model": "freemium"},
    {"github": "hashicorp/nomad", "name": "Nomad", "category": "Orchestration", "pricing_model": "freemium"},
    {"github": "docker/compose", "name": "Docker Compose", "category": "Orchestration", "pricing_model": "open_source"},

    # ===== CI/CD =====
    {"github": "jenkinsci/jenkins", "name": "Jenkins", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "actions/runner", "name": "GitHub Actions", "category": "CI/CD", "pricing_model": "freemium"},
    {"github": "gitlabhq/gitlabhq", "name": "GitLab CI/CD", "category": "CI/CD", "pricing_model": "freemium"},
    {"github": "argoproj/argo-cd", "name": "ArgoCD", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "fluxcd/flux2", "name": "Flux", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "tektoncd/pipeline", "name": "Tekton", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "harness/drone", "name": "Drone CI", "category": "CI/CD", "pricing_model": "freemium"},
    {"github": "spinnaker/spinnaker", "name": "Spinnaker", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "gocd/gocd", "name": "GoCD", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "woodpecker-ci/woodpecker", "name": "Woodpecker CI", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "concourse/concourse", "name": "Concourse CI", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "dagger/dagger", "name": "Dagger", "category": "CI/CD", "pricing_model": "open_source"},
    {"github": "earthly/earthly", "name": "Earthly", "category": "CI/CD", "pricing_model": "freemium"},

    # ===== INFRASTRUCTURE AS CODE =====
    {"github": "hashicorp/terraform", "name": "Terraform", "category": "Infrastructure as Code", "pricing_model": "freemium"},
    {"github": "opentofu/opentofu", "name": "OpenTofu", "category": "Infrastructure as Code", "pricing_model": "open_source"},
    {"github": "pulumi/pulumi", "name": "Pulumi", "category": "Infrastructure as Code", "pricing_model": "freemium"},
    {"github": "ansible/ansible", "name": "Ansible", "category": "Infrastructure as Code", "pricing_model": "open_source"},
    {"github": "chef/chef", "name": "Chef", "category": "Infrastructure as Code", "pricing_model": "freemium"},
    {"github": "puppetlabs/puppet", "name": "Puppet", "category": "Infrastructure as Code", "pricing_model": "freemium"},
    {"github": "saltstack/salt", "name": "SaltStack", "category": "Infrastructure as Code", "pricing_model": "open_source"},
    {"github": "crossplane/crossplane", "name": "Crossplane", "category": "Infrastructure as Code", "pricing_model": "open_source"},
    {"github": "gruntwork-io/terragrunt", "name": "Terragrunt", "category": "Infrastructure as Code", "pricing_model": "open_source"},
    {"github": "cdktf/cdktf-cli", "name": "CDK for Terraform", "category": "Infrastructure as Code", "pricing_model": "open_source"},

    # ===== MONITORING & OBSERVABILITY =====
    {"github": "prometheus/prometheus", "name": "Prometheus", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "grafana/grafana", "name": "Grafana", "category": "Monitoring", "pricing_model": "freemium"},
    {"github": "zabbix/zabbix", "name": "Zabbix", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "netdata/netdata", "name": "Netdata", "category": "Monitoring", "pricing_model": "freemium"},
    {"github": "influxdata/telegraf", "name": "Telegraf", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "influxdata/influxdb", "name": "InfluxDB", "category": "Monitoring", "pricing_model": "freemium"},
    {"github": "VictoriaMetrics/VictoriaMetrics", "name": "VictoriaMetrics", "category": "Monitoring", "pricing_model": "freemium"},
    {"github": "open-telemetry/opentelemetry-collector", "name": "OpenTelemetry", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "jaegertracing/jaeger", "name": "Jaeger", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "grafana/tempo", "name": "Grafana Tempo", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "uptrace/uptrace", "name": "Uptrace", "category": "Monitoring", "pricing_model": "freemium"},
    {"github": "SigNoz/signoz", "name": "SigNoz", "category": "Monitoring", "pricing_model": "freemium"},
    {"github": "thanos-io/thanos", "name": "Thanos", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "cortexproject/cortex", "name": "Cortex", "category": "Monitoring", "pricing_model": "open_source"},
    {"github": "grafana/mimir", "name": "Grafana Mimir", "category": "Monitoring", "pricing_model": "open_source"},

    # ===== LOGGING =====
    {"github": "elastic/elasticsearch", "name": "Elasticsearch", "category": "Logging", "pricing_model": "freemium"},
    {"github": "elastic/logstash", "name": "Logstash", "category": "Logging", "pricing_model": "freemium"},
    {"github": "elastic/kibana", "name": "Kibana", "category": "Logging", "pricing_model": "freemium"},
    {"github": "fluent/fluentd", "name": "Fluentd", "category": "Logging", "pricing_model": "open_source"},
    {"github": "fluent/fluent-bit", "name": "Fluent Bit", "category": "Logging", "pricing_model": "open_source"},
    {"github": "grafana/loki", "name": "Loki", "category": "Logging", "pricing_model": "open_source"},
    {"github": "vectordotdev/vector", "name": "Vector", "category": "Logging", "pricing_model": "open_source"},
    {"github": "Graylog2/graylog2-server", "name": "Graylog", "category": "Logging", "pricing_model": "freemium"},

    # ===== SERVICE MESH & NETWORKING =====
    {"github": "istio/istio", "name": "Istio", "category": "Service Mesh", "pricing_model": "open_source"},
    {"github": "linkerd/linkerd2", "name": "Linkerd", "category": "Service Mesh", "pricing_model": "open_source"},
    {"github": "hashicorp/consul", "name": "Consul", "category": "Service Mesh", "pricing_model": "freemium"},
    {"github": "traefik/traefik", "name": "Traefik", "category": "Service Mesh", "pricing_model": "freemium"},
    {"github": "envoyproxy/envoy", "name": "Envoy Proxy", "category": "Service Mesh", "pricing_model": "open_source"},
    {"github": "nginx/nginx", "name": "NGINX", "category": "Service Mesh", "pricing_model": "freemium"},
    {"github": "haproxy/haproxy", "name": "HAProxy", "category": "Service Mesh", "pricing_model": "freemium"},
    {"github": "caddyserver/caddy", "name": "Caddy", "category": "Service Mesh", "pricing_model": "open_source"},
    {"github": "cilium/cilium", "name": "Cilium", "category": "Service Mesh", "pricing_model": "open_source"},
    {"github": "coredns/coredns", "name": "CoreDNS", "category": "Service Mesh", "pricing_model": "open_source"},

    # ===== SECURITY =====
    {"github": "hashicorp/vault", "name": "Vault", "category": "Security", "pricing_model": "freemium"},
    {"github": "falcosecurity/falco", "name": "Falco", "category": "Security", "pricing_model": "open_source"},
    {"github": "aquasecurity/trivy", "name": "Trivy", "category": "Security", "pricing_model": "open_source"},
    {"github": "open-policy-agent/opa", "name": "Open Policy Agent", "category": "Security", "pricing_model": "open_source"},
    {"github": "kyverno/kyverno", "name": "Kyverno", "category": "Security", "pricing_model": "open_source"},
    {"github": "cert-manager/cert-manager", "name": "cert-manager", "category": "Security", "pricing_model": "open_source"},
    {"github": "goharbor/harbor", "name": "Harbor", "category": "Security", "pricing_model": "open_source"},
    {"github": "anchore/grype", "name": "Grype", "category": "Security", "pricing_model": "open_source"},
    {"github": "aquasecurity/tfsec", "name": "tfsec", "category": "Security", "pricing_model": "open_source"},
    {"github": "bridgecrewio/checkov", "name": "Checkov", "category": "Security", "pricing_model": "freemium"},
    {"github": "tenable/terrascan", "name": "Terrascan", "category": "Security", "pricing_model": "open_source"},

    # ===== PACKAGE MANAGEMENT & GITOPS =====
    {"github": "helm/helm", "name": "Helm", "category": "Package Management", "pricing_model": "open_source"},
    {"github": "kubernetes-sigs/kustomize", "name": "Kustomize", "category": "Package Management", "pricing_model": "open_source"},
    {"github": "helmfile/helmfile", "name": "Helmfile", "category": "Package Management", "pricing_model": "open_source"},

    # ===== DATABASES =====
    {"github": "postgres/postgres", "name": "PostgreSQL", "category": "Databases", "pricing_model": "open_source"},
    {"github": "mysql/mysql-server", "name": "MySQL", "category": "Databases", "pricing_model": "open_source"},
    {"github": "mongodb/mongo", "name": "MongoDB", "category": "Databases", "pricing_model": "freemium"},
    {"github": "redis/redis", "name": "Redis", "category": "Databases", "pricing_model": "open_source"},
    {"github": "etcd-io/etcd", "name": "etcd", "category": "Databases", "pricing_model": "open_source"},
    {"github": "cockroachdb/cockroach", "name": "CockroachDB", "category": "Databases", "pricing_model": "freemium"},
    {"github": "tikv/tikv", "name": "TiKV", "category": "Databases", "pricing_model": "open_source"},
    {"github": "vitessio/vitess", "name": "Vitess", "category": "Databases", "pricing_model": "open_source"},
    {"github": "dgraph-io/dgraph", "name": "Dgraph", "category": "Databases", "pricing_model": "freemium"},

    # ===== CLOUD NATIVE STORAGE =====
    {"github": "minio/minio", "name": "MinIO", "category": "Cloud Native Storage", "pricing_model": "freemium"},
    {"github": "rook/rook", "name": "Rook", "category": "Cloud Native Storage", "pricing_model": "open_source"},
    {"github": "openebs/openebs", "name": "OpenEBS", "category": "Cloud Native Storage", "pricing_model": "open_source"},
    {"github": "longhorn/longhorn", "name": "Longhorn", "category": "Cloud Native Storage", "pricing_model": "open_source"},

    # ===== SERVERLESS =====
    {"github": "openfaas/faas", "name": "OpenFaaS", "category": "Serverless", "pricing_model": "freemium"},
    {"github": "knative/serving", "name": "Knative", "category": "Serverless", "pricing_model": "open_source"},
    {"github": "nuclio/nuclio", "name": "Nuclio", "category": "Serverless", "pricing_model": "open_source"},

    # ===== TESTING & CHAOS ENGINEERING =====
    {"github": "grafana/k6", "name": "k6", "category": "Testing", "pricing_model": "freemium"},
    {"github": "locustio/locust", "name": "Locust", "category": "Testing", "pricing_model": "open_source"},
    {"github": "apache/jmeter", "name": "JMeter", "category": "Testing", "pricing_model": "open_source"},
    {"github": "litmuschaos/litmus", "name": "Litmus Chaos", "category": "Testing", "pricing_model": "open_source"},
    {"github": "chaos-mesh/chaos-mesh", "name": "Chaos Mesh", "category": "Testing", "pricing_model": "open_source"},
    {"github": "steadybit/steadybit", "name": "Steadybit", "category": "Testing", "pricing_model": "freemium"},

    # ===== API GATEWAY =====
    {"github": "Kong/kong", "name": "Kong", "category": "API Gateway", "pricing_model": "freemium"},
    {"github": "apache/apisix", "name": "APISIX", "category": "API Gateway", "pricing_model": "open_source"},
    {"github": "TykTechnologies/tyk", "name": "Tyk", "category": "API Gateway", "pricing_model": "freemium"},
    {"github": "luraproject/lura", "name": "KrakenD", "category": "API Gateway", "pricing_model": "freemium"},

    # ===== DEVELOPER TOOLS =====
    {"github": "derailed/k9s", "name": "k9s", "category": "Developer Tools", "pricing_model": "open_source"},
    {"github": "ahmetb/kubectx", "name": "kubectx", "category": "Developer Tools", "pricing_model": "open_source"},
    {"github": "stern/stern", "name": "Stern", "category": "Developer Tools", "pricing_model": "open_source"},
    {"github": "vmware-tanzu/velero", "name": "Velero", "category": "Developer Tools", "pricing_model": "open_source"},
    {"github": "kubernetes/minikube", "name": "Minikube", "category": "Developer Tools", "pricing_model": "open_source"},
    {"github": "tilt-dev/tilt", "name": "Tilt", "category": "Developer Tools", "pricing_model": "freemium"},
    {"github": "telepresenceio/telepresence", "name": "Telepresence", "category": "Developer Tools", "pricing_model": "freemium"},
    {"github": "lensapp/lens", "name": "Lens", "category": "Developer Tools", "pricing_model": "freemium"},
    {"github": "argoproj/argo-workflows", "name": "Argo Workflows", "category": "Developer Tools", "pricing_model": "open_source"},

    # ===== MESSAGE QUEUES =====
    {"github": "apache/kafka", "name": "Apache Kafka", "category": "Message Queue", "pricing_model": "open_source"},
    {"github": "rabbitmq/rabbitmq-server", "name": "RabbitMQ", "category": "Message Queue", "pricing_model": "open_source"},
    {"github": "nats-io/nats-server", "name": "NATS", "category": "Message Queue", "pricing_model": "open_source"},

    # ===== POLICY & GOVERNANCE =====
    {"github": "aquasecurity/trivy-operator", "name": "Trivy Operator", "category": "Security", "pricing_model": "open_source"},
    {"github": "datreeio/datree", "name": "Datree", "category": "Security", "pricing_model": "freemium"},
    {"github": "stackrox/stackrox", "name": "StackRox", "category": "Security", "pricing_model": "freemium"},
]


def _create_slug(name: str) -> str:
    """Generate URL-friendly slug from tool name."""
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-").replace("_", "-")


class ToolIngestionService:
    """Service for ingesting DevOps tools from GitHub API."""

    def __init__(self):
        self.github_token = GITHUB_TOKEN
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    async def fetch_repo_data(self, session: aiohttp.ClientSession, github_path: str) -> Optional[Dict[str, Any]]:
        """Fetch repository data from GitHub API."""
        url = f"{GITHUB_API_BASE}/repos/{github_path}"
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    logger.warning(f"GitHub API rate limited for {github_path}")
                    return None
                elif response.status == 404:
                    logger.warning(f"Repository not found: {github_path}")
                    return None
                else:
                    logger.error(f"GitHub API error {response.status} for {github_path}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {github_path}: {e}")
            return None

    def _generate_summary(self, name: str, category: str, description: str, stars: int, language: str) -> str:
        """Generate an AI summary fallback for a tool."""
        star_text = f"{stars:,}" if stars else "many"
        desc = description[:200] if description else f"A popular {category.lower()} tool"
        return (
            f"{name} is a {category.lower()} tool with {star_text} GitHub stars. "
            f"{desc}. It is widely used in DevOps and cloud engineering workflows"
            f"{f', primarily built with {language}' if language else ''}."
        )

    async def ingest_single_tool(
        self,
        session: aiohttp.ClientSession,
        tool_def: Dict[str, str],
        db_session
    ) -> Optional[Dict[str, Any]]:
        """Ingest a single tool from GitHub."""
        from main import Tool

        github_path = tool_def["github"]
        name = tool_def["name"]
        category = tool_def["category"]
        pricing_model = tool_def.get("pricing_model", "open_source")

        repo_data = await self.fetch_repo_data(session, github_path)

        if repo_data:
            description = repo_data.get("description", "") or f"A {category.lower()} tool for DevOps engineers"
            stars = repo_data.get("stargazers_count", 0)
            forks = repo_data.get("forks_count", 0)
            license_info = repo_data.get("license")
            license_name = license_info.get("spdx_id", "Unknown") if license_info else "Unknown"
            homepage = repo_data.get("homepage", "")
            language = repo_data.get("language", "")
            pushed_at = repo_data.get("pushed_at")
            github_url = repo_data.get("html_url", f"https://github.com/{github_path}")
        else:
            # Use fallback data
            description = f"A {category.lower()} tool for DevOps engineers"
            stars = 0
            forks = 0
            license_name = "Unknown"
            homepage = ""
            language = ""
            pushed_at = None
            github_url = f"https://github.com/{github_path}"

        slug = _create_slug(name)
        ai_summary = self._generate_summary(name, category, description, stars, language)

        # Parse last commit date
        last_commit = None
        if pushed_at:
            try:
                last_commit = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Upsert: update if exists, insert if new
        existing = db_session.query(Tool).filter(Tool.slug == slug).first()
        if existing:
            existing.description = description
            existing.github_stars = stars
            existing.github_forks = forks
            existing.github_url = github_url
            existing.homepage_url = homepage or existing.homepage_url
            existing.license = license_name
            existing.pricing_model = pricing_model
            existing.last_commit_date = last_commit
            existing.ai_summary = ai_summary
            existing.category = category
            existing.updated_at = datetime.utcnow()
            return {"name": name, "action": "updated", "stars": stars}
        else:
            new_tool = Tool(
                name=name,
                slug=slug,
                description=description,
                homepage_url=homepage,
                github_url=github_url,
                category=category,
                license=license_name,
                pricing_model=pricing_model,
                github_stars=stars,
                github_forks=forks,
                last_commit_date=last_commit,
                ai_summary=ai_summary,
            )
            db_session.add(new_tool)
            return {"name": name, "action": "created", "stars": stars}

    async def ingest_all(self, db_session) -> Dict[str, Any]:
        """
        Ingest all tools from the DEVOPS_TOOLS registry.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            Summary dict with count, created, updated, errors
        """
        results = {"count": 0, "created": 0, "updated": 0, "errors": [], "tools": []}
        batch_size = 10  # Process in batches to avoid rate limits

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(DEVOPS_TOOLS), batch_size):
                batch = DEVOPS_TOOLS[i:i + batch_size]
                tasks = [
                    self.ingest_single_tool(session, tool_def, db_session)
                    for tool_def in batch
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        error_msg = f"Error ingesting {batch[j]['name']}: {str(result)}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                    elif result:
                        results["count"] += 1
                        results["tools"].append(result)
                        if result["action"] == "created":
                            results["created"] += 1
                        else:
                            results["updated"] += 1

                # Commit after each batch
                try:
                    db_session.commit()
                except Exception as e:
                    db_session.rollback()
                    logger.error(f"Database commit error for batch {i}: {e}")
                    results["errors"].append(f"Batch {i} commit error: {str(e)}")

                # Small delay between batches to be respectful of rate limits
                if i + batch_size < len(DEVOPS_TOOLS):
                    await asyncio.sleep(1)

        logger.info(
            f"Ingestion complete: {results['count']} tools "
            f"({results['created']} created, {results['updated']} updated, "
            f"{len(results['errors'])} errors)"
        )
        return results


# Singleton instance
tool_ingestion_service = ToolIngestionService()
