from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any


EVENT_LABELS = {
    "PushEvent": "push",
    "PullRequestEvent": "pull request",
    "PullRequestReviewEvent": "revisão",
    "IssuesEvent": "issue",
    "IssueCommentEvent": "comentário",
    "CreateEvent": "criação",
    "ReleaseEvent": "release",
    "ForkEvent": "fork",
    "WatchEvent": "star",
}


def render_report(username: str, events: list[dict[str, Any]], period: str, date_key: str) -> str:
    counts = Counter(event["type"] for event in events)
    repos = Counter(event["repo"] for event in events)
    title = "Relatório diário" if period == "daily" else "Relatório semanal"

    lines = [
        f"# {title} — {date_key}",
        "",
        f"Usuário monitorado: [{username}](https://github.com/{username})",
        f"Eventos públicos encontrados: **{len(events)}**",
        "",
    ]

    if not events:
        lines.extend([
            "Nenhum evento público novo foi encontrado no período.",
            "",
            "> A API pública do GitHub pode apresentar atraso. O monitor tentará novamente na próxima execução.",
            "",
        ])
        return "\n".join(lines)

    lines.extend(["## Resumo por tipo", ""])
    for event_type, count in sorted(counts.items()):
        label = EVENT_LABELS.get(event_type, event_type)
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Repositórios ativos", ""])
    for repo, count in repos.most_common():
        lines.append(f"- [{repo}](https://github.com/{repo}): {count} evento(s)")

    lines.extend(["", "## Linha do tempo", ""])
    for event in reversed(events):
        timestamp = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
        label = EVENT_LABELS.get(event["type"], event["type"])
        detail = event.get("action") or event.get("ref_type") or event.get("ref") or "atividade"
        number = f" #{event['number']}" if event.get("number") else ""
        lines.append(
            f"- `{timestamp:%Y-%m-%d %H:%M UTC}` — **{label}**{number} em "
            f"[{event['repo']}](https://github.com/{event['repo']}) — {detail}"
        )

    lines.extend([
        "",
        "---",
        "",
        "Fonte: API pública de eventos do GitHub. Este arquivo é gerado automaticamente a partir de eventos verificáveis.",
        "",
    ])
    return "\n".join(lines)


def fallback_review(events: list[dict[str, Any]]) -> str:
    repos = Counter(event["repo"] for event in events)
    lines = ["## Próximos passos determinísticos", ""]
    if not events:
        lines.append("- Nenhuma recomendação: não houve atividade pública no período.")
    else:
        top_repo = repos.most_common(1)[0][0]
        lines.extend([
            f"- Revisar testes e documentação do repositório `{top_repo}`.",
            "- Conferir falhas recentes de CI e dependências desatualizadas.",
            "- Transformar itens relevantes em issues pequenas e verificáveis.",
        ])
    return "\n".join(lines) + "\n"

