# GitHub Neerg

Monitor de engenharia que transforma eventos públicos reais do GitHub em relatórios diários e semanais verificáveis.

## O que ele faz

- coleta eventos públicos recentes de um usuário usando a API oficial do GitHub;
- resume pushes, pull requests, issues, revisões e releases por repositório;
- executa testes antes de publicar qualquer relatório;
- usa GitHub Models, quando disponível, para sugerir próximos passos técnicos;
- grava uma nova versão somente quando os dados de entrada realmente mudam;
- identifica toda alteração automática como `github-actions[bot]`.

O projeto não cria commits vazios, não falsifica autoria e não inventa atividade. A API de eventos pode apresentar atraso de até algumas horas, portanto os relatórios são atualizados várias vezes ao dia e permanecem idempotentes quando não há eventos novos.

## Execução local

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m github_neerg.cli --username AnglusBR --period daily --output .
```

Para habilitar a análise por IA fora do GitHub Actions:

```bash
python -m github_neerg.cli \
  --username AnglusBR \
  --period daily \
  --output . \
  --ai-token "$GITHUB_TOKEN"
```

## Automação

O workflow `engineering-monitor.yml` roda cinco vezes por dia, todos os dias. Aos domingos também produz um relatório semanal. Relatórios e snapshots só são enviados quando o conteúdo mudou.

Os commits automáticos usam a identidade oficial do bot do GitHub e não são apresentados como trabalho manual do proprietário.

