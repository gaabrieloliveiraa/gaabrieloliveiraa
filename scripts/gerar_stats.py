#!/usr/bin/env python3
"""Gera stats.svg com os numeros reais da conta (inclui repositorios privados).

Uso: gh auth login (conta dona do perfil) e depois: python3 scripts/gerar_stats.py
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def gql(consulta):
    saida = subprocess.check_output(["gh", "api", "graphql", "-f", "query=" + consulta])
    return json.loads(saida)["data"]["viewer"]


def coletar():
    v = gql(
        "{viewer{login name createdAt pullRequests{totalCount} issues{totalCount}"
        " repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){totalCount}"
        " repositories(first:100,ownerAffiliations:OWNER){nodes{stargazerCount}}}}"
    )
    commits = 0
    for ano in range(int(v["createdAt"][:4]), datetime.now(timezone.utc).year + 1):
        c = gql(
            '{viewer{contributionsCollection(from:"%d-01-01T00:00:00Z",to:"%d-12-31T23:59:59Z")'
            "{totalCommitContributions restrictedContributionsCount}}}" % (ano, ano)
        )["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    return {
        "nome": v["name"] or v["login"],
        "Estrelas recebidas": sum(r["stargazerCount"] for r in v["repositories"]["nodes"]),
        "Commits": commits,
        "Pull requests": v["pullRequests"]["totalCount"],
        "Issues": v["issues"]["totalCount"],
        "Repositorios contribuidos": v["repositoriesContributedTo"]["totalCount"],
    }


def svg(d):
    linhas = [k for k in d if k != "nome"]
    altura = 70 + 26 * len(linhas)
    corpo = "".join(
        f'<text x="25" y="{70 + 26 * i}" fill="#8ec07c" font-size="14">{k}:</text>'
        f'<text x="300" y="{70 + 26 * i}" fill="#ebdbb2" font-size="14" font-weight="600" text-anchor="end">{d[k]}</text>'
        for i, k in enumerate(linhas)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="{altura}" viewBox="0 0 360 {altura}" '
        'font-family="Segoe UI, Ubuntu, sans-serif">'
        f'<rect x="0.5" y="0.5" rx="4.5" width="359" height="{altura - 1}" fill="#282828" stroke="#3c3836"/>'
        f'<text x="25" y="35" fill="#fabd2f" font-size="18" font-weight="600">Estatisticas de {d["nome"]}</text>'
        f"{corpo}</svg>\n"
    )


if __name__ == "__main__":
    Path(__file__).resolve().parent.parent.joinpath("stats.svg").write_text(svg(coletar()), encoding="utf-8")
