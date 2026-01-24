"""
OAuth Service for GitHub and Google Authentication

Provides:
- OAuth authorization URL generation
- Token exchange with OAuth providers
- User profile fetching from providers
- Account linking and creation
"""

import os
import secrets
import urllib.parse
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import aiohttp


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    user_info_url: str
    scopes: list
    redirect_uri: str


class OAuthService:
    """Handles OAuth authentication flows for multiple providers."""
    
    def __init__(self):
        # GitHub OAuth configuration
        self.github = OAuthConfig(
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user",
            scopes=["read:user", "user:email"],
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/callback/github")
        )
        
        # Google OAuth configuration
        self.google = OAuthConfig(
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
            scopes=["openid", "email", "profile"],
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google")
        )
        
        # State storage (in production, use Redis or database)
        self._states: Dict[str, str] = {}
    
    def get_available_providers(self) -> list:
        """Get list of configured OAuth providers."""
        providers = []
        
        if self.github.client_id:
            providers.append({
                "name": "github",
                "display_name": "GitHub",
                "icon": "github",
                "color": "#333"
            })
        
        if self.google.client_id:
            providers.append({
                "name": "google",
                "display_name": "Google",
                "icon": "chrome",
                "color": "#4285F4"
            })
        
        # Always show providers for demo (even without credentials)
        if not providers:
            providers = [
                {
                    "name": "github",
                    "display_name": "GitHub",
                    "icon": "github",
                    "color": "#333",
                    "demo": True
                },
                {
                    "name": "google",
                    "display_name": "Google",
                    "icon": "chrome",
                    "color": "#4285F4",
                    "demo": True
                }
            ]
        
        return providers
    
    def generate_state(self, provider: str) -> str:
        """Generate and store a secure state parameter."""
        state = secrets.token_urlsafe(32)
        self._states[state] = provider
        return state
    
    def validate_state(self, state: str) -> Optional[str]:
        """Validate state and return the provider name."""
        provider = self._states.pop(state, None)
        return provider
    
    def get_authorization_url(self, provider: str) -> Tuple[str, str]:
        """
        Get the OAuth authorization URL for a provider.
        
        Returns:
            Tuple of (authorization_url, state)
        """
        config = self._get_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        
        state = self.generate_state(provider)
        
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scopes),
            "state": state,
            "response_type": "code"
        }
        
        # Google requires additional parameters
        if provider == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        
        auth_url = f"{config.authorize_url}?{urllib.parse.urlencode(params)}"
        return auth_url, state
    
    async def exchange_code_for_token(self, provider: str, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        config = self._get_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": config.redirect_uri,
        }
        
        if provider == "github":
            data["accept"] = "json"
        elif provider == "google":
            data["grant_type"] = "authorization_code"
        
        headers = {"Accept": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(config.token_url, data=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Token exchange failed: {error_text}")
                
                return await response.json()
    
    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Fetch user information from the OAuth provider."""
        config = self._get_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        if provider == "github":
            headers["Accept"] = "application/vnd.github.v3+json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(config.user_info_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to fetch user info: {error_text}")
                
                user_data = await response.json()
                
                # Normalize user data across providers
                return self._normalize_user_data(provider, user_data)
    
    async def get_github_email(self, access_token: str) -> Optional[str]:
        """Fetch primary email from GitHub (requires email scope)."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.github.com/user/emails", headers=headers) as response:
                if response.status == 200:
                    emails = await response.json()
                    for email in emails:
                        if email.get("primary") and email.get("verified"):
                            return email.get("email")
        return None
    
    def _get_config(self, provider: str) -> Optional[OAuthConfig]:
        """Get configuration for a provider."""
        if provider == "github":
            return self.github
        elif provider == "google":
            return self.google
        return None
    
    def _normalize_user_data(self, provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user data from different providers to a common format."""
        if provider == "github":
            return {
                "provider": "github",
                "provider_id": str(data.get("id")),
                "email": data.get("email"),
                "username": data.get("login"),
                "name": data.get("name") or data.get("login"),
                "avatar_url": data.get("avatar_url"),
                "bio": data.get("bio"),
                "profile_url": data.get("html_url")
            }
        elif provider == "google":
            return {
                "provider": "google",
                "provider_id": data.get("id"),
                "email": data.get("email"),
                "username": data.get("email", "").split("@")[0],
                "name": data.get("name"),
                "avatar_url": data.get("picture"),
                "bio": None,
                "profile_url": None
            }
        return data


# Singleton instance
oauth_service = OAuthService()
