import json
import requests
from unittest.mock import patch
from app import app

sample_gists = [
    {
        "id": "1",
        "html_url": "https://gist.github.com/1",
        "description": "Example gist 1",
        "files": {"file1.txt": {}},
        "public": True,
        "created_at": "2020-01-01T00:00:00Z"
    },
    {
        "id": "2",
        "html_url": "https://gist.github.com/2",
        "description": None,
        "files": {"code.py": {}},
        "public": True,
        "created_at": "2020-02-02T00:00:00Z"
    }
]

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data) if json_data is not None else ""

    def json(self):
        return self._json

    def raise_for_status(self):
        # Raise requests.HTTPError (with .response) to mimic requests' real behaviour
        if not (200 <= self.status_code < 300):
            http_err = requests.HTTPError(f"{self.status_code} Error")
            http_err.response = self
            raise http_err

@patch("app.requests.get")
def test_get_user_gists_success(mock_get):
    mock_get.return_value = DummyResponse(sample_gists, 200)

    client = app.test_client()
    res = client.get("/octocat")
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"] == "octocat"
    assert isinstance(data["gists"], list)
    assert len(data["gists"]) == 2
    # check normalized fields
    first = data["gists"][0]
    assert first["id"] == "1"
    assert "file1.txt" in first["files"]

@patch("app.requests.get")
def test_get_user_gists_not_found(mock_get):
    mock_get.return_value = DummyResponse({"message":"Not Found"}, 404)

    client = app.test_client()
    res = client.get("/nonexistentuser12345")
    assert res.status_code == 404

@patch("app.requests.get")
def test_github_api_error(mock_get):
    # Simulate network error using requests.RequestException so app's except clause catches it
    mock_get.side_effect = requests.RequestException("network error")

    client = app.test_client()
    res = client.get("/octocat")
    # our code maps request exceptions to 502
    assert res.status_code == 502