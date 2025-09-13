from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import base64

mcp = FastMCP("github")

# constants
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = "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"
DEFAULT_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-agent/1.0"
}

async def github_api_request(method: str, url: str, json: Any = None) -> dict[str,Any] | None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=DEFAULT_HEADERS, json=json, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            None

@mcp.tool()
async def push_file(owner: str, repo: str, path: str, content: str, commit_message: str) -> str:
    """
    Push (create/update) a file to a Githun Repo.
    Args:
        owner: owner of the repo
        repo: repository in the owner's github
        path: filepath inside repo
        content: base64-encoded file content or raw text
        commit_meesage: message for commit
    """

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"

    # check if file exists
    file_data = await github_api_request("GET", url)
    payload = {
        "message": commit_message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
    }


    if file_data and "sha" in file_data:
        payload["sha"] = file_data["sha"]
    result = await github_api_request("PUT", url, json=payload)

    if result is None:
        return f"Push Failed for url: {url}"
    return f"File {path} pushed with commit {commit_message}"