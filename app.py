from flask import Flask, jsonify, request, abort
import requests

app = Flask(__name__)

GITHUB_API = "https://api.github.com"

def fetch_gists_for_user(username):
    """
    Fetch public gists for a GitHub user using the REST API.
    Returns a list of gist summaries (id, html_url, description, files).
    Raises requests.HTTPError on non-200 responses.
    """
    url = f"{GITHUB_API}/users/{username}/gists"
    resp = requests.get(url, headers={"Accept": "application/vnd.github.v3+json"}, timeout=10)
    resp.raise_for_status()
    gists = resp.json()
    # Normalize/return a compact structure
    result = []
    for g in gists:
        files = list(g.get("files", {}).keys())
        result.append({
            "id": g.get("id"),
            "html_url": g.get("html_url"),
            "description": g.get("description"),
            "files": files,
            "public": g.get("public", True),
            "created_at": g.get("created_at"),
        })
    return result

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Gists API. Use /<username> to fetch public gists."})

@app.route("/<username>", methods=["GET"])
def get_user_gists(username):
    if not username:
        abort(400, "username required")
    try:
        gists = fetch_gists_for_user(username)
    except requests.HTTPError as e:
        # If not found, return 404 to the client
        status = e.response.status_code if e.response is not None else 500
        if status == 404:
            abort(404, description=f"user {username} not found")
        abort(status, description=str(e))
    except requests.RequestException as e:
        abort(502, description="error contacting GitHub API")
    return jsonify({"user": username, "gists": gists})

if __name__ == "__main__":
    # For local development only. Docker uses gunicorn.
    app.run(host="0.0.0.0", port=8080)
