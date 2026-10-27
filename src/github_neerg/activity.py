from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.request import Request, urlopen


API_VERSION = "2022-11-28"


def fetch_public_events(username: str, days: int, token: str | None = None) -> list[dict[str, Any]]:
    """Busca e normaliza eventos públicos recentes do usuário."""
    url = f"https://api.github.com/users/{username}/events/public?per_page=100"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-neerg/1.0",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        raw_events = json.load(response)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    normalized = []
    for event in raw_events:
        created_at = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
        if created_at < cutoff:
            continue
        normalized.append(normalize_event(event))

    return sorted(normalized, key=lambda item: (item["created_at"], item["id"]))


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    """Mantém apenas dados estáveis e úteis para auditoria e relatório."""
    payload = event.get("payload") or {}
    result: dict[str, Any] = {
        "id": str(event["id"]),
        "type": event.get("type", "UnknownEvent"),
        "repo": (event.get("repo") or {}).get("name", "unknown"),
        "created_at": event["created_at"],
    }

    for key in ("action", "ref", "ref_type", "size"):
        value = payload.get(key)
        if value not in (None, ""):
            result[key] = value

    pull_request = payload.get("pull_request") or {}
    issue = payload.get("issue") or {}
    if pull_request.get("number"):
        result["number"] = pull_request["number"]
    elif issue.get("number"):
        result["number"] = issue["number"]

    return result

