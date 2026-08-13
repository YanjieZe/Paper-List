from paper_worker.documents import _split_text


def test_extracted_text_removes_postgres_forbidden_nul_bytes():
    assert _split_text("robot\x00 learning") == ["robot learning"]
