#!/usr/bin/env python3
"""
Startup seed script: ingests tools, calculates health scores, and generates comparison pages.
Run once after deploying to a fresh database.

Usage:
    python startup_seed.py

Environment variables:
    DATABASE_URL     - Database connection string (default: sqlite:///./cloudengineered.db)
    GITHUB_TOKEN     - GitHub personal access token for higher API rate limits
    GEMINI_API_KEY   - Google Gemini API key for AI-generated content
"""
import os
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Ensure backend directory is on the path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    from main import engine, Base, SessionLocal, Tool
    from tool_ingestion import ToolIngestionService
    from health_scoring import HealthScoringService

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_count = db.query(Tool).count()
        logger.info(f"Existing tools in database: {existing_count}")

        # Step 1: Ingest tools
        if existing_count < 50:
            logger.info("Starting tool ingestion (this may take a few minutes)...")
            ingestion = ToolIngestionService(db)
            result = ingestion.ingest_all()
            logger.info(f"Ingestion complete: {result['ingested']} tools ingested, {result['errors']} errors")
        else:
            logger.info("Sufficient tools already in database, skipping ingestion")

        # Step 2: Calculate health scores for tools that have a github_url
        tools_without_health = db.query(Tool).filter(
            Tool.github_url.isnot(None),
            Tool.health_score == 0
        ).count()

        if tools_without_health > 0:
            logger.info(f"Calculating health scores for {tools_without_health} tools...")
            health_service = HealthScoringService()
            tools = db.query(Tool).filter(
                Tool.github_url.isnot(None),
                Tool.health_score == 0
            ).all()

            scored = 0
            for tool in tools:
                try:
                    result = health_service.calculate_health_score(tool.github_url)
                    if "error" not in result:
                        import json
                        tool.health_score = result["score"]
                        tool.health_data = json.dumps(result)
                        from datetime import datetime
                        tool.last_health_check = datetime.utcnow()
                        db.commit()
                        scored += 1
                    time.sleep(0.5)  # Rate limit
                except Exception as e:
                    logger.warning(f"Health score failed for {tool.name}: {e}")

            logger.info(f"Health scoring complete: {scored} tools scored")
        else:
            logger.info("All tools already have health scores, skipping")

        # Step 3: Generate comparison pages for top tool pairs
        from main import ComparisonPage
        existing_comparisons = db.query(ComparisonPage).count()

        if existing_comparisons < 10:
            logger.info("Generating comparison pages...")
            TOP_PAIRS = [
                ("docker", "podman"),
                ("kubernetes", "docker-swarm"),
                ("terraform", "pulumi"),
                ("terraform", "ansible"),
                ("jenkins", "github-actions"),
                ("jenkins", "gitlab-ci-cd"),
                ("argocd", "flux"),
                ("prometheus", "grafana"),
                ("ansible", "chef"),
                ("ansible", "puppet"),
                ("istio", "linkerd"),
                ("docker", "kubernetes"),
                ("grafana", "kibana"),
                ("jenkins", "circleci"),
                ("vault", "cert-manager"),
            ]

            generated = 0
            for slug_a, slug_b in TOP_PAIRS:
                tool_a = db.query(Tool).filter(Tool.slug == slug_a).first()
                tool_b = db.query(Tool).filter(Tool.slug == slug_b).first()
                if not tool_a or not tool_b:
                    continue

                comp_slug = f"{slug_a}-vs-{slug_b}"
                existing = db.query(ComparisonPage).filter(ComparisonPage.slug == comp_slug).first()
                if existing:
                    continue

                title = f"{tool_a.name} vs {tool_b.name} (2025): Complete Comparison"
                content = _build_comparison_content(tool_a, tool_b)
                meta = f"Compare {tool_a.name} and {tool_b.name}: features, performance, pricing, and use cases."

                from datetime import datetime
                page = ComparisonPage(
                    tool_a_id=tool_a.id,
                    tool_b_id=tool_b.id,
                    slug=comp_slug,
                    title=title,
                    content=content,
                    meta_description=meta,
                    views=0,
                    generated_at=datetime.utcnow(),
                )
                db.add(page)
                db.commit()
                generated += 1

            logger.info(f"Generated {generated} comparison pages")
        else:
            logger.info("Comparison pages already exist, skipping")

        final_tools = db.query(Tool).count()
        final_comparisons = db.query(ComparisonPage).count()
        logger.info(f"Seed complete. Tools: {final_tools}, Comparisons: {final_comparisons}")

    finally:
        db.close()


def _build_comparison_content(tool_a, tool_b) -> str:
    """Generate structured comparison markdown content."""
    return f"""# {tool_a.name} vs {tool_b.name}

## Overview

**{tool_a.name}**: {tool_a.description or tool_a.ai_summary or 'A popular DevOps tool.'}

**{tool_b.name}**: {tool_b.description or tool_b.ai_summary or 'A popular DevOps tool.'}

## GitHub Stats

| Metric | {tool_a.name} | {tool_b.name} |
|--------|--------------|--------------|
| Stars | {(tool_a.github_stars or 0):,} | {(tool_b.github_stars or 0):,} |
| Forks | {(tool_a.github_forks or 0):,} | {(tool_b.github_forks or 0):,} |
| Health Score | {tool_a.health_score or 'N/A'} | {tool_b.health_score or 'N/A'} |
| License | {tool_a.license or 'N/A'} | {tool_b.license or 'N/A'} |
| Category | {tool_a.category} | {tool_b.category} |
| Pricing | {tool_a.pricing_model or 'N/A'} | {tool_b.pricing_model or 'N/A'} |

## Key Differences

{tool_a.name} and {tool_b.name} serve different needs in the DevOps ecosystem. While both are widely used, they differ in architecture, use cases, and community size.

## When to Use {tool_a.name}

{tool_a.name} is a strong choice when you need a mature, battle-tested solution with a large community. With {(tool_a.github_stars or 0):,} GitHub stars, it has proven its value across many organizations.

## When to Use {tool_b.name}

{tool_b.name} excels when you need a modern approach with fresh design decisions. Its {(tool_b.github_stars or 0):,} GitHub stars reflect growing adoption and community trust.

## Conclusion

Both {tool_a.name} and {tool_b.name} are excellent tools. Your choice should depend on your team's specific requirements, existing infrastructure, and long-term goals.
"""


if __name__ == "__main__":
    main()
