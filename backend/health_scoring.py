"""
Health Scoring Engine for CloudEngineered Platform

Calculates composite health scores (0-100) for DevOps tools
based on GitHub signals: commit activity, issue response time,
release cadence, stars growth, contributor count, and more.
"""

import os
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# OSI-approved license identifiers
OSI_LICENSES = {
    "MIT", "Apache-2.0", "GPL-2.0", "GPL-3.0", "BSD-2-Clause", "BSD-3-Clause",
    "ISC", "MPL-2.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0", "Unlicense",
    "CC0-1.0", "Artistic-2.0", "Zlib", "BSL-1.0", "PostgreSQL",
    "GPL-2.0-only", "GPL-3.0-only", "AGPL-3.0-only",
}


def _parse_github_path(github_url: str) -> Optional[tuple]:
    """Extract owner/repo from a GitHub URL."""
    if not github_url:
        return None
    url = github_url.replace("https://github.com/", "").replace("http://github.com/", "")
    parts = url.strip("/").split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None


class HealthScoringService:
    """Calculates composite health scores for tools based on GitHub data."""

    def __init__(self):
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async def _github_get(self, session: aiohttp.ClientSession, url: str, params: dict = None) -> Optional[Any]:
        """Make a GitHub API GET request."""
        try:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    logger.warning(f"GitHub rate limited: {url}")
                return None
        except Exception as e:
            logger.error(f"GitHub API error for {url}: {e}")
            return None

    async def _score_commit_activity(self, session: aiohttp.ClientSession, owner: str, repo: str) -> int:
        """Score based on commit activity in last 30 days. Weight: 20%"""
        since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
        data = await self._github_get(session, url, {"since": since, "per_page": 100})

        if data is None:
            return 50  # Default if API fails

        count = len(data)
        if count >= 50:
            return 100
        elif count >= 10:
            return 80
        elif count >= 1:
            return 50
        return 0

    async def _score_issue_response(self, session: aiohttp.ClientSession, owner: str, repo: str) -> int:
        """Score based on issue response/close time. Weight: 15%"""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
        data = await self._github_get(session, url, {"state": "closed", "per_page": 20, "sort": "updated"})

        if not data:
            return 50

        close_times = []
        for issue in data:
            if issue.get("pull_request"):
                continue  # Skip PRs
            created = issue.get("created_at")
            closed = issue.get("closed_at")
            if created and closed:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    closed_dt = datetime.fromisoformat(closed.replace("Z", "+00:00"))
                    close_times.append((closed_dt - created_dt).total_seconds() / 86400)  # days
                except (ValueError, TypeError):
                    pass

        if not close_times:
            return 50

        avg_days = sum(close_times) / len(close_times)
        if avg_days < 1:
            return 100
        elif avg_days < 7:
            return 80
        elif avg_days < 30:
            return 50
        return 20

    async def _score_release_cadence(self, session: aiohttp.ClientSession, owner: str, repo: str) -> int:
        """Score based on release frequency. Weight: 15%"""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases"
        data = await self._github_get(session, url, {"per_page": 5})

        if not data:
            return 25  # No releases

        latest = data[0]
        published = latest.get("published_at") or latest.get("created_at")
        if not published:
            return 25

        try:
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            days_since = (datetime.now(timezone.utc) - pub_dt).days

            if days_since <= 30:
                return 100
            elif days_since <= 90:
                return 75
            elif days_since <= 180:
                return 50
            return 25
        except (ValueError, TypeError):
            return 25

    def _score_stars_growth(self, current_stars: int, previous_stars: int) -> int:
        """Score based on stars growth trend. Weight: 10%"""
        if previous_stars <= 0:
            return 60  # No previous data, assume stable

        growth_rate = (current_stars - previous_stars) / max(previous_stars, 1)
        if growth_rate > 0.01:  # >1% growth
            return 100
        elif growth_rate > 0:
            return 60
        return 30  # Declining

    def _score_issue_ratio(self, open_issues: int, stars: int) -> int:
        """Score based on open issues to stars ratio. Weight: 10%"""
        if stars <= 0:
            return 50

        ratio = open_issues / stars
        if ratio < 0.01:
            return 100
        elif ratio < 0.05:
            return 70
        elif ratio < 0.1:
            return 40
        return 20

    async def _score_contributors(self, session: aiohttp.ClientSession, owner: str, repo: str) -> int:
        """Score based on contributor count. Weight: 10%"""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors"
        data = await self._github_get(session, url, {"per_page": 1, "anon": "false"})

        if data is None:
            return 50

        # GitHub returns Link header for pagination with last page number
        # As a simpler approach, just check the first page
        # For repos with many contributors, the list will be full
        count = len(data) if isinstance(data, list) else 0

        # Use a secondary request to check total count via search
        url2 = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        repo_data = await self._github_get(session, url2)
        # contributors_count isn't directly available, use subscribers as proxy
        if repo_data:
            # Use network count and watchers as quality signals
            watchers = repo_data.get("subscribers_count", 0)
            if watchers > 1000:
                return 100
            elif watchers > 200:
                return 80
            elif watchers > 50:
                return 60
            elif watchers > 10:
                return 40
            return 20

        return 50

    def _score_documentation(self, has_wiki: bool, has_pages: bool, description: str) -> int:
        """Score based on documentation presence. Weight: 10%"""
        score = 0
        if description and len(description) > 20:
            score += 40
        if has_wiki:
            score += 30
        if has_pages:
            score += 30
        # Most repos at least have a README, give base score
        if score == 0:
            score = 30
        return min(score, 100)

    def _score_license(self, license_spdx: str) -> int:
        """Score based on license clarity. Weight: 10%"""
        if not license_spdx or license_spdx == "NOASSERTION" or license_spdx == "Unknown":
            return 0
        if license_spdx in OSI_LICENSES:
            return 100
        return 50

    def _calculate_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        return "F"

    async def calculate_health_score(self, github_url: str, previous_stars: int = 0) -> Dict[str, Any]:
        """
        Calculate composite health score for a tool.

        Args:
            github_url: GitHub repository URL
            previous_stars: Star count from last check (for growth calculation)

        Returns:
            Dict with score, grade, and breakdown
        """
        parsed = _parse_github_path(github_url)
        if not parsed:
            return {"score": 0, "grade": "F", "breakdown": {}, "error": "Invalid GitHub URL"}

        owner, repo = parsed

        async with aiohttp.ClientSession() as session:
            # Fetch repo data first
            repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
            repo_data = await self._github_get(session, repo_url)

            if not repo_data:
                return {"score": 0, "grade": "F", "breakdown": {}, "error": "Repository not found"}

            current_stars = repo_data.get("stargazers_count", 0)
            open_issues = repo_data.get("open_issues_count", 0)
            has_wiki = repo_data.get("has_wiki", False)
            has_pages = repo_data.get("has_pages", False)
            description = repo_data.get("description", "")
            license_info = repo_data.get("license")
            license_spdx = license_info.get("spdx_id", "Unknown") if license_info else "Unknown"

            # Calculate all sub-scores in parallel
            commit_score, issue_score, release_score, contrib_score = await asyncio.gather(
                self._score_commit_activity(session, owner, repo),
                self._score_issue_response(session, owner, repo),
                self._score_release_cadence(session, owner, repo),
                self._score_contributors(session, owner, repo),
            )

            stars_score = self._score_stars_growth(current_stars, previous_stars)
            issue_ratio_score = self._score_issue_ratio(open_issues, current_stars)
            doc_score = self._score_documentation(has_wiki, has_pages, description)
            license_score = self._score_license(license_spdx)

        # Weighted composite score
        breakdown = {
            "commit_activity": {"score": commit_score, "weight": 0.20},
            "issue_response": {"score": issue_score, "weight": 0.15},
            "release_cadence": {"score": release_score, "weight": 0.15},
            "stars_growth": {"score": stars_score, "weight": 0.10},
            "issue_ratio": {"score": issue_ratio_score, "weight": 0.10},
            "contributors": {"score": contrib_score, "weight": 0.10},
            "documentation": {"score": doc_score, "weight": 0.10},
            "license": {"score": license_score, "weight": 0.10},
        }

        composite = sum(
            item["score"] * item["weight"]
            for item in breakdown.values()
        )
        composite = round(composite)

        return {
            "score": composite,
            "grade": self._calculate_grade(composite),
            "breakdown": breakdown,
            "stars": current_stars,
            "open_issues": open_issues,
            "calculated_at": datetime.utcnow().isoformat(),
        }

    async def score_all_tools(self, db_session) -> Dict[str, Any]:
        """
        Calculate health scores for all tools in the database.

        Args:
            db_session: SQLAlchemy session

        Returns:
            Summary of scoring results
        """
        from main import Tool

        tools = db_session.query(Tool).filter(Tool.github_url.isnot(None)).all()
        results = {"scored": 0, "errors": [], "tools": []}

        for tool in tools:
            try:
                previous_stars = tool.github_stars or 0
                health = await self.calculate_health_score(tool.github_url, previous_stars)

                if "error" not in health:
                    tool.health_score = health["score"]
                    tool.health_data = json.dumps(health)
                    tool.last_health_check = datetime.utcnow()

                    # Also update stars/forks from fresh data
                    if health.get("stars"):
                        tool.github_stars = health["stars"]

                    results["scored"] += 1
                    results["tools"].append({
                        "name": tool.name,
                        "score": health["score"],
                        "grade": health["grade"],
                    })
                else:
                    results["errors"].append(f"{tool.name}: {health['error']}")

            except Exception as e:
                logger.error(f"Error scoring {tool.name}: {e}")
                results["errors"].append(f"{tool.name}: {str(e)}")

            # Respect rate limits
            await asyncio.sleep(2)

        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to commit health scores: {e}")
            results["errors"].append(f"Commit error: {str(e)}")

        logger.info(f"Health scoring complete: {results['scored']} tools scored, {len(results['errors'])} errors")
        return results


# Singleton instance
health_scoring_service = HealthScoringService()
