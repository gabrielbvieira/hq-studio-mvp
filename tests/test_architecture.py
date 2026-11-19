"""Protege a direção das dependências e o isolamento da composição."""

import ast
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    "layer, forbidden",
    [
        ("domain", {"application", "infra", "presentation", "main", "app", "fastapi", "pydantic"}),
        (
            "application",
            {"infra", "presentation", "main", "app", "fastapi", "sqlite3", "subprocess", "PIL", "fpdf"},
        ),
        ("presentation", {"infra", "main", "app", "sqlite3"}),
    ],
)
def test_dependencies_point_inward(layer, forbidden):
    for path in (ROOT / layer).rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            )
            for name in names:
                top = name.split(".")[0]
                assert top not in forbidden, f"{path.relative_to(ROOT)} importa {name}"
                if layer == "domain":
                    assert top in sys.stdlib_module_names or top == "domain"


def test_factory_isolates_data_and_serves_existing_interface(tmp_path, monkeypatch):
    monkeypatch.setenv('HQ_HOME', str(tmp_path / 'default'))
    from fastapi.testclient import TestClient
    from main.application import create_app

    first = create_app(tmp_path / "first")
    second = create_app(tmp_path / "second")
    with TestClient(first) as a, TestClient(second) as b:
        assert a.post("/api/projects", json={"name": "Primeiro"}).status_code == 201
        assert a.get("/api/projects").json()[0]["name"] == "Primeiro"
        assert b.get("/api/projects").json() == []
        for client in (a, b):
            assert client.get("/").status_code == 200
            assert client.get("/static/app.js").status_code == 200
            assert client.get("/static/style.css").status_code == 200
