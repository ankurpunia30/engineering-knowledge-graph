"""
Vercel serverless function entry point for FastAPI app.
"""
from chat.app import app

# Vercel uses this as the entry point
handler = app
