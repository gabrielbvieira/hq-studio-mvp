"""Compatibilidade com o comando existente: uvicorn app.main:app."""

from main.application import BASE, MEDIA, app, create_app, providers, repo, service

__all__ = ["app", "create_app", "BASE", "MEDIA", "repo", "providers", "service"]
