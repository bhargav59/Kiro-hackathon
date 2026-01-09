import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from main import app, Base, engine
from seed_data import seed_sample_tools

# Create tables and seed data (only if needed for PostgreSQL)
try:
    Base.metadata.create_all(bind=engine)
    seed_sample_tools()
except Exception as e:
    print(f"Database setup error: {e}")
