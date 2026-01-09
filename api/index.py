import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from main import app, Base, engine
from seed_data import seed_sample_tools

# Ensure tables exist and seed data on every startup (needed for serverless)
Base.metadata.create_all(bind=engine)
seed_sample_tools()
