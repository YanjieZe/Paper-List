from paper_worker.agents import build_agent_registry
from paper_worker.config import Settings


def test_named_agent_registry_has_all_v1_specialists(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/paper")
    registry = build_agent_registry(Settings())
    assert set(registry) == {
        "ingestion",
        "catalog",
        "reader",
        "critic",
        "linker",
        "roadmap",
        "tutor",
        "librarian",
    }
