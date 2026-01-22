from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/tools")
def get_tools():
    return [
        {
            "id": 1,
            "name": "Docker",
            "slug": "docker",
            "description": "Container platform for building, shipping, and running applications",
            "homepage_url": "https://www.docker.com",
            "github_url": "https://github.com/moby/moby",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "logo_url": None,
            "github_stars": 68000,
            "github_forks": 18500,
            "last_commit_date": "2024-01-01T00:00:00",
            "ai_summary": "Docker revolutionized software deployment through containerization",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        },
        {
            "id": 2,
            "name": "Kubernetes",
            "slug": "kubernetes",
            "description": "Container orchestration platform for automating deployment and scaling",
            "homepage_url": "https://kubernetes.io",
            "github_url": "https://github.com/kubernetes/kubernetes",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "logo_url": None,
            "github_stars": 105000,
            "github_forks": 38000,
            "last_commit_date": "2024-01-01T00:00:00",
            "ai_summary": "Kubernetes is the de facto standard for container orchestration",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    ]

@app.post("/api/ai/enhanced-compare")
def enhanced_compare_tools(request: dict):
    """Simple tool comparison fallback"""
    tool1 = request.get('tool1', '').strip()
    tool2 = request.get('tool2', '').strip()
    
    if not tool1 or not tool2:
        raise HTTPException(status_code=400, detail="Both tool names are required")
    
    return {
        "tool1": tool1,
        "tool2": tool2,
        "detailed_analysis": {
            "overview": f"Comparison between {tool1} and {tool2} - both are popular DevOps tools with different strengths",
            "technical_comparison": {
                "architecture": f"{tool1}: Modern architecture. {tool2}: Robust design",
                "performance": f"{tool1}: High performance. {tool2}: Optimized performance",
                "scalability": f"{tool1}: Highly scalable. {tool2}: Enterprise scalable",
                "security": f"{tool1}: Security focused. {tool2}: Enterprise security"
            },
            "business_analysis": {
                "cost_analysis": f"{tool1}: Varies by usage. {tool2}: Competitive pricing",
                "market_position": f"{tool1}: Market leader. {tool2}: Strong competitor",
                "adoption_rate": f"{tool1}: Widely adopted. {tool2}: Growing adoption"
            },
            "use_case_scenarios": {
                "startup": f"{tool1}: Great for startups. {tool2}: Also startup-friendly",
                "enterprise": f"{tool1}: Enterprise ready. {tool2}: Enterprise capable",
                "specific_industries": f"{tool1}: Multi-industry. {tool2}: Industry specific"
            },
            "pros_cons": {
                "tool1_pros": [f"Mature ecosystem", f"Large community", f"Extensive documentation"],
                "tool2_pros": [f"Modern approach", f"Growing community", f"Active development"],
                "tool1_cons": [f"Learning curve", f"Resource usage"],
                "tool2_cons": [f"Smaller ecosystem", f"Less documentation"]
            },
            "decision_matrix": [
                {"criteria": "Ease of Use", "tool1_score": 8, "tool2_score": 7, "analysis": f"{tool1} is more user-friendly"},
                {"criteria": "Performance", "tool1_score": 9, "tool2_score": 8, "analysis": f"{tool1} has better performance"},
                {"criteria": "Community", "tool1_score": 9, "tool2_score": 6, "analysis": f"{tool1} has larger community"},
                {"criteria": "Documentation", "tool1_score": 8, "tool2_score": 7, "analysis": f"{tool1} has better docs"}
            ]
        },
        "quantitative_metrics": {
            "github_stars": f"{tool1}: High. {tool2}: Growing",
            "community_size": f"{tool1}: Large. {tool2}: Active",
            "release_frequency": f"{tool1}: Regular. {tool2}: Consistent"
        },
        "recommendation": {
            "use_case_fit": f"Choose {tool1} for: General use cases. Choose {tool2} for: Specific needs",
            "decision_factors": ["Team expertise", "Infrastructure requirements", "Budget constraints"],
            "migration_path": f"Migration from {tool1} to {tool2} or vice versa is possible with planning"
        }
    }

@app.get("/api/users/me")
def get_current_user():
    return {
        "id": 1,
        "username": "demo",
        "email": "demo@cloudengineered.com",
        "created_at": "2024-01-01T00:00:00"
    }

@app.get("/api/analytics/overview")
def get_analytics():
    return {
        "total_tools": 8,
        "total_users": 150,
        "total_reviews": 45,
        "categories": {
            "Container": 2,
            "Infrastructure": 2,
            "CI/CD": 2,
            "Monitoring": 2
        },
        "top_categories": [
            ["Container", 2],
            ["Infrastructure", 2],
            ["CI/CD", 2],
            ["Monitoring", 2]
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
