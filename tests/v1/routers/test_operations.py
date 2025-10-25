from unittest.mock import MagicMock, patch

import pytest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture
def mock_matcher() -> MagicMock:
    with patch("app.v1.routers.operations.matcher") as mock:
        annotater = MagicMock()
        mock.qMatcherAnnotater.return_value = annotater
        yield annotater


def test_operations_both_tasks(mock_matcher):
    """Test when both detect and annotate tasks are requested."""
    # Setup mock responses
    mock_matcher.match_and_annotate.return_value = (
        'قال تعالى:"قُلْ هُوَ اللَّهُ أَحَدٌ"(الإخلاص:1)',
        [{
            'aya_name': 'الإخلاص',
            'verses': ['قل هو الله احد'],
            'errors': [[]],
            'startInText': 2,
            'endInText': 6,
            'aya_start': 1,
            'aya_end': 1
        }]
    )

    # Test request
    response = client.post("/api/v1/operations", json={
        "text": "قل هو الله احد",
        "tasks": ["detect", "annotate"],
        "find_errors": True,
        "find_missing": True,
        "allowed_error_percentage": 0.25,
        "min_match": 3,
        "return_json": False
    })

    assert response.status_code == 200
    result = response.json()

    assert result["annotated_text"] == 'قال تعالى:"قُلْ هُوَ اللَّهُ أَحَدٌ"(الإخلاص:1)'
    assert len(result["matches"]) == 1
    match = result["matches"][0]
    assert match["surah_name"] == "الإخلاص"
    assert match["ayah_start"] == 1
    assert match["ayah_end"] == 1
    assert match["start_index"] == 2
    assert match["end_index"] == 6

def test_operations_detect_only(mock_matcher):
    """Test when only detect task is requested."""
    # Setup mock response
    mock_matcher.matchAll.return_value = [{
        'aya_name': 'الإخلاص',
        'verses': ['قل هو الله احد'],
        'errors': [[]],
        'startInText': 0,
        'endInText': 4,
        'aya_start': 1,
        'aya_end': 1
    }]

    # Test request
    response = client.post("/api/v1/operations", json={
        "text": "قل هو الله احد",
        "tasks": ["detect"],
        "find_errors": True,
        "find_missing": True,
        "allowed_error_percentage": 0.25,
        "min_match": 3,
        "return_json": False
    })

    assert response.status_code == 200
    result = response.json()

    assert result["annotated_text"] is None
    assert len(result["matches"]) == 1
    match = result["matches"][0]
    assert match["surah_name"] == "الإخلاص"
    assert match["ayah_start"] == 1
    assert match["ayah_end"] == 1
    assert match["start_index"] == 0
    assert match["end_index"] == 4


def test_operations_annotate_only(mock_matcher):
    """Test when only annotate task is requested."""
    # Setup mock response
    mock_matcher.annotateTxt.return_value = 'قال تعالى:"قُلْ هُوَ اللَّهُ أَحَدٌ"(الإخلاص:1)'

    # Test request
    response = client.post("/api/v1/operations", json={
        "text": "قل هو الله احد",
        "tasks": ["annotate"],
        "find_errors": True,
        "find_missing": True,
        "allowed_error_percentage": 0.25,
        "min_match": 3,
        "return_json": False
    })

    assert response.status_code == 200
    result = response.json()

    assert result["annotated_text"] == 'قال تعالى:"قُلْ هُوَ اللَّهُ أَحَدٌ"(الإخلاص:1)'
    assert result["matches"] is None


def test_operations_custom_delimiters(mock_matcher):
    """Test operations with custom delimiters configuration."""
    mock_matcher.match_and_annotate.return_value = (
        'قال تعالى:"قُلْ هُوَ اللَّهُ أَحَدٌ"(الإخلاص:1)',
        []
    )

    # Test request with custom delimiters
    response = client.post("/api/v1/operations", json={
        "text": "قل هو الله احد",
        "tasks": ["detect", "annotate"],
        "find_errors": True,
        "find_missing": True,
        "allowed_error_percentage": 0.25,
        "min_match": 3,
        "return_json": False,
        "delimiters": r"[،؛\n]"
    })

    assert response.status_code == 200

def test_operations_no_tasks(mock_matcher):
    """Test when no tasks are provided."""
    response = client.post("/api/v1/operations", json={
        "text": "قل هو الله احد",
        "tasks": [],
        "find_errors": True,
        "find_missing": True,
        "allowed_error_percentage": 0.25,
        "min_match": 3,
        "return_json": False
    })

    assert response.status_code == 200
    result = response.json()

    assert result["annotated_text"] is None
    assert result["matches"] is None


def test_operations_no_matches(mock_matcher):
    """Test when no matches are found."""
    # Setup mock response with no matches
    mock_matcher.matchAll.return_value = []

    # Test request
    response = client.post("/api/v1/operations", json={
        "text": "no quran text here",
        "tasks": ["detect"],
        "find_errors": True,
        "find_missing": True,
        "allowed_error_percentage": 0.25,
        "min_match": 3,
        "return_json": False
    })

    assert response.status_code == 200
    result = response.json()

    assert result["matches"] is None
