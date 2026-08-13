from paper_worker.schemas import ItemType
from paper_worker.urls import identify_url, normalize_url


def test_arxiv_versions_and_pdf_normalize_to_one_identity():
    first = identify_url("https://arxiv.org/pdf/2410.24164v2.pdf")
    second = identify_url("http://www.arxiv.org/abs/2410.24164?utm_source=x")
    assert first.normalized_url == second.normalized_url == "https://arxiv.org/abs/2410.24164"
    assert first.arxiv_id == "2410.24164"
    assert first.item_type == ItemType.PAPER


def test_github_repository_discards_subpaths_and_tracking():
    identity = identify_url("https://github.com/NVlabs/GRAIL/tree/main?utm_campaign=test")
    assert identity.normalized_url == "https://github.com/NVlabs/GRAIL"
    assert identity.github_repo == "nvlabs/grail"
    assert identity.item_type == ItemType.REPOSITORY


def test_tracking_parameters_are_removed_but_meaningful_query_is_stable():
    assert normalize_url("http://www.example.com/a/?b=2&utm_source=x&a=1#part") == "https://example.com/a?a=1&b=2"
