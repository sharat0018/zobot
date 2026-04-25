import sys
import os

# Add the backend directory to sys.path so app imports work
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.append(backend_path)

from app.main import app
