"""
Vercel Serverless Function Entry Point
"""
from src.todo_app.main import app

# Vercel expects the app to be named 'app' or 'handler'
handler = app
