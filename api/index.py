"""Vercel Serverless Function entry point for FastAPI backend."""
import sys
import os

# Ensure backend package can be discovered from repo root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import app

# Export ASGI app instance for Vercel Serverless
app_instance = app
