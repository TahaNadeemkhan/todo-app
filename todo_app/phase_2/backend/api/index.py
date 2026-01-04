"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add the backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from todo_app.main import app

# Vercel expects 'app' for ASGI frameworks like FastAPI
app = app
