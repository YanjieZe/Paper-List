from pathlib import Path

from paper_worker.evals import validate_eval_manifest


def test_eval_manifest_meets_v1_size_and_branch_contract():
    root = Path(__file__).resolve().parents[2]
    result = validate_eval_manifest(root)
    assert result["items"] == 30
    assert result["questions"] >= 50
    assert result["branches"] >= 8
