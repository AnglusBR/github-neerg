from __future__ import annotations

import json
from urllib.request import Request, urlopen


MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"


def review_with_github_models(report: str, token: str, model: str = "openai/gpt-4.1-mini") -> str:
    """Gera recomendações; a resposta nunca é executada como código."""
    prompt = (
        "Analise o relatório de atividade GitHub abaixo. Produza em português até cinco "
        "recomendações técnicas concretas e verificáveis. Não invente trabalho, métricas, "
        "falhas ou repositórios. Dê prioridade a testes, documentação, segurança e CI.\n\n"
        + report
    )
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "Você é um revisor de engenharia conservador e factual."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }).encode("utf-8")
    request = Request(
        MODELS_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-neerg/1.0",
        },
    )
    with urlopen(request, timeout=60) as response:
        payload = json.load(response)
    return payload["choices"][0]["message"]["content"].strip() + "\n"

