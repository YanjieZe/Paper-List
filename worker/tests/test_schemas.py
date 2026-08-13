from uuid import uuid4

import pytest
from pydantic import ValidationError

from paper_worker.schemas import Claim, ClaimKind, EvidenceRef


def test_factual_claim_requires_evidence():
    with pytest.raises(ValidationError):
        Claim(text="Success improves by 10%", kind=ClaimKind.FACT)


def test_document_evidence_requires_locator():
    with pytest.raises(ValidationError):
        EvidenceRef(document_version_id=uuid4())


def test_external_evidence_can_use_url():
    evidence = EvidenceRef(url="https://example.com/source", source_title="Source")
    assert str(evidence.url) == "https://example.com/source"
