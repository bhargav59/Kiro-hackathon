import os
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

# OAuth Configuration
config = Config('.env')

oauth = OAuth(config)

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

def get_oauth_providers():
    """Get available OAuth providers"""
    providers = []
    
    if os.getenv('GOOGLE_CLIENT_ID'):
        providers.append({
            'name': 'google',
            'display_name': 'Google',
            'icon': '🔍',
            'color': 'bg-red-500 hover:bg-red-600'
        })
    
    if os.getenv('GITHUB_CLIENT_ID'):
        providers.append({
            'name': 'github',
            'display_name': 'GitHub',
            'icon': '🐙',
            'color': 'bg-gray-800 hover:bg-gray-900'
        })
    
    return providers
