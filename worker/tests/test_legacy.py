from pathlib import Path

from paper_worker.legacy import scan_legacy


def test_legacy_scan_accounts_for_every_discovered_url(tmp_path: Path):
    (tmp_path / "topics").mkdir()
    (tmp_path / "README.md").write_text("- [Paper](https://arxiv.org/pdf/2410.24164.pdf)\n")
    (tmp_path / "topics" / "robotics.md").write_text(
        "- [Project](https://example.com/project) https://example.com/blog\n"
    )
    report = scan_legacy(tmp_path)
    assert report.discovered_urls == report.accounted_urls == 3
    assert report.unique_normalized_urls == 3


def test_duplicate_url_occurrences_on_one_line_remain_auditable(tmp_path: Path):
    (tmp_path / "topics").mkdir()
    (tmp_path / "README.md").write_text(
        "[one](https://example.com/x) [two](https://example.com/x)\n"
    )
    report = scan_legacy(tmp_path)
    assert report.discovered_urls == report.accounted_urls == 2
    assert [record.occurrence_index for record in report.records] == [0, 1]
