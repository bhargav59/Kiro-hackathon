import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from main import app
from seed_data import seed_sample_tools

# Seed data on startup if no tools exist
try:
    seed_sample_tools()
except Exception as e:
    print(f"Seeding error (may be normal if already seeded): {e}")
