"""Tests for core API endpoints: health, auth, tools, reviews, AI, stats."""
import pytest


class TestHealthAndRoot:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "CloudEngineered API"
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


class TestRegistration:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "Str0ng@Pass!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_weak_password_too_short(self, client):
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "short"
        })
        assert response.status_code == 400
        assert "8 characters" in response.json()["detail"]

    def test_register_weak_password_no_uppercase(self, client):
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "nouppercase1!"
        })
        assert response.status_code == 400
        assert "uppercase" in response.json()["detail"]

    def test_register_weak_password_no_special(self, client):
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "NoSpecial123"
        })
        assert response.status_code == 400
        assert "special" in response.json()["detail"]

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "username": "user1",
            "password": "Test@1234"
        })
        response = client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "username": "user2",
            "password": "Test@1234"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client):
        client.post("/api/auth/register", json={
            "email": "first@example.com",
            "username": "sameuser",
            "password": "Test@1234"
        })
        response = client.post("/api/auth/register", json={
            "email": "second@example.com",
            "username": "sameuser",
            "password": "Test@1234"
        })
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "username": "testuser",
            "password": "Test@1234"
        })
        assert response.status_code == 422  # Pydantic validation


class TestLogin:
    def _register(self, client):
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "Test@1234"
        })

    def test_login_success(self, client):
        self._register(client)
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "Test@1234"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        self._register(client)
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "WrongPass1!"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "Test@1234"
        })
        assert response.status_code == 401


class TestTools:
    def test_get_tools_empty(self, client):
        response = client.get("/api/tools")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tools_with_search(self, client):
        response = client.get("/api/tools?search=docker")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_tools_with_category(self, client):
        response = client.get("/api/tools?category=Container")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_tool_not_found(self, client):
        response = client.get("/api/tools/nonexistent-tool")
        assert response.status_code == 404

    def test_create_tool_unauthenticated(self, client):
        response = client.post("/api/tools", json={
            "name": "TestTool",
            "description": "A test tool",
            "category": "Container",
            "pricing_model": "free"
        })
        assert response.status_code == 401  # No auth header

    def test_create_tool_authenticated(self, client, auth_headers):
        response = client.post("/api/tools", json={
            "name": "TestTool",
            "description": "A test tool",
            "category": "Container",
            "pricing_model": "free"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TestTool"
        assert data["slug"] == "testtool"

    def test_create_duplicate_tool(self, client, auth_headers):
        client.post("/api/tools", json={
            "name": "DupTool",
            "description": "First",
            "category": "CI/CD",
            "pricing_model": "free"
        }, headers=auth_headers)
        response = client.post("/api/tools", json={
            "name": "DupTool",
            "description": "Duplicate",
            "category": "CI/CD",
            "pricing_model": "free"
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestReviews:
    def _create_tool(self, client, auth_headers):
        resp = client.post("/api/tools", json={
            "name": "ReviewableTool",
            "description": "Tool for review testing",
            "category": "Monitoring",
            "pricing_model": "free"
        }, headers=auth_headers)
        return resp.json()["id"]

    def test_create_review_unauthenticated(self, client):
        response = client.post("/api/tools/1/reviews", json={
            "rating": 5,
            "content": "Great tool!"
        })
        assert response.status_code == 401

    def test_create_review_authenticated(self, client, auth_headers):
        tool_id = self._create_tool(client, auth_headers)
        response = client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": 4,
            "content": "Solid tool for monitoring"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 4
        assert data["content"] == "Solid tool for monitoring"

    def test_review_rating_validation_too_high(self, client, auth_headers):
        tool_id = self._create_tool(client, auth_headers)
        response = client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": 999,
            "content": "Invalid rating"
        }, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation

    def test_review_rating_validation_too_low(self, client, auth_headers):
        tool_id = self._create_tool(client, auth_headers)
        response = client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": 0,
            "content": "Invalid rating"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_review_rating_validation_negative(self, client, auth_headers):
        tool_id = self._create_tool(client, auth_headers)
        response = client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": -1,
            "content": "Negative rating"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_duplicate_review(self, client, auth_headers):
        tool_id = self._create_tool(client, auth_headers)
        client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": 4,
            "content": "First review"
        }, headers=auth_headers)
        response = client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": 5,
            "content": "Second review"
        }, headers=auth_headers)
        assert response.status_code == 400
        assert "already reviewed" in response.json()["detail"]

    def test_get_reviews_for_tool(self, client, auth_headers):
        tool_id = self._create_tool(client, auth_headers)
        client.post(f"/api/tools/{tool_id}/reviews", json={
            "rating": 5,
            "content": "Excellent!"
        }, headers=auth_headers)
        response = client.get(f"/api/tools/{tool_id}/reviews")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["rating"] == 5


class TestAI:
    def test_natural_query(self, client):
        response = client.post("/api/ai/natural-query", json={
            "query": "monitoring tools for kubernetes"
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert "suggestions" in data

    def test_compare_tools_too_few(self, client):
        response = client.post("/api/ai/compare", json={
            "tool_ids": [1]
        })
        assert response.status_code == 400
        assert "At least 2" in response.json()["detail"]

    def test_moderate_content_clean(self, client, auth_headers):
        response = client.post("/api/ai/moderate", json={
            "text": "Docker is a fantastic containerization tool for modern apps"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_approved"] is True
        assert data["is_spam"] is False
        assert data["is_inappropriate"] is False

    def test_moderate_content_spam(self, client, auth_headers):
        response = client.post("/api/ai/moderate", json={
            "text": "Buy now and click here for scam deals!"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_approved"] is False
        assert data["is_spam"] is True


class TestStats:
    def test_platform_stats(self, client):
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_tools" in data
        assert "total_users" in data
        assert "total_reviews" in data
        assert "categories" in data

    def test_advanced_analytics(self, client):
        response = client.get("/api/stats/advanced")
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "growth_trends" in data
        assert "insights" in data


class TestAdminEndpoints:
    def test_admin_enhance_tools_unauthenticated(self, client):
        response = client.post("/api/admin/enhance-tools")
        assert response.status_code == 401

    def test_admin_enhance_single_tool_unauthenticated(self, client):
        response = client.post("/api/admin/enhance-tool/1")
        assert response.status_code == 401


class TestUserProfile:
    def test_get_profile_unauthenticated(self, client):
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_get_profile_authenticated(self, client, auth_headers):
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "auth@example.com"
        assert data["username"] == "authuser"


class TestUserStack:
    def test_get_stack_unauthenticated(self, client):
        response = client.get("/api/users/me/stack")
        assert response.status_code == 401

    def test_add_nonexistent_tool_to_stack(self, client, auth_headers):
        response = client.post("/api/users/me/stack/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_add_and_get_stack(self, client, auth_headers):
        # Create a tool first
        tool_resp = client.post("/api/tools", json={
            "name": "StackTool",
            "description": "Tool for stack testing",
            "category": "Infrastructure",
            "pricing_model": "free"
        }, headers=auth_headers)
        tool_id = tool_resp.json()["id"]

        # Add to stack
        response = client.post(f"/api/users/me/stack/{tool_id}", headers=auth_headers)
        assert response.status_code == 200

        # Get stack
        response = client.get("/api/users/me/stack", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_add_duplicate_to_stack(self, client, auth_headers):
        tool_resp = client.post("/api/tools", json={
            "name": "DupStackTool",
            "description": "A tool",
            "category": "CI/CD",
            "pricing_model": "free"
        }, headers=auth_headers)
        tool_id = tool_resp.json()["id"]
        client.post(f"/api/users/me/stack/{tool_id}", headers=auth_headers)
        response = client.post(f"/api/users/me/stack/{tool_id}", headers=auth_headers)
        assert response.status_code == 400
        assert "already in stack" in response.json()["detail"]

    def test_remove_from_stack(self, client, auth_headers):
        tool_resp = client.post("/api/tools", json={
            "name": "RemovableTool",
            "description": "A tool",
            "category": "Container",
            "pricing_model": "free"
        }, headers=auth_headers)
        tool_id = tool_resp.json()["id"]
        client.post(f"/api/users/me/stack/{tool_id}", headers=auth_headers)
        response = client.delete(f"/api/users/me/stack/{tool_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "removed" in response.json()["message"]
