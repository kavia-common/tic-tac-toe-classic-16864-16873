"""
API package initializer for Tic Tac Toe backend.
Provides convenient exports for app factory.
"""

from .app import get_app  # re-export for convenient import paths

__all__ = ["get_app"]
