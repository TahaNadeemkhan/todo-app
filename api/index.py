"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add the backend src to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'todo_app', 'phase_2', 'backend', 'src')
sys.path.insert(0, backend_path)

from todo_app.main import app

# Vercel expects 'app' for ASGI frameworks like FastAPI
app = app
