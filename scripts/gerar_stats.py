#!/usr/bin/env python3
"""Gera stats.svg (cartoes de estatisticas) com os numeros reais da conta, inclusive repositorios privados.

Uso: gh auth login (conta dona do perfil) e depois: python3 scripts/gerar_stats.py
Na automacao (GitHub Action) o gh le o token da variavel GH_TOKEN.
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
        " repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){totalCount}}}"
    )
    agora = datetime.now(timezone.utc)
    commits = 0
    for ano in range(int(v["createdAt"][:4]), agora.year + 1):
        c = gql(
            '{viewer{contributionsCollection(from:"%d-01-01T00:00:00Z",to:"%d-12-31T23:59:59Z")'
            "{totalCommitContributions restrictedContributionsCount}}}" % (ano, ano)
        )["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    anos = agora.year - int(v["createdAt"][:4])
    return [
        ("Commits", commits, "#fabd2f"),
        ("Pull requests", v["pullRequests"]["totalCount"], "#8ec07c"),
        ("Repositórios", v["repositoriesContributedTo"]["totalCount"], "#83a598"),
        ("Anos de GitHub", anos, "#d3869b"),
    ]


def formatar(n):
    return f"{n:,}".replace(",", ".")


def svg(cartoes):
    largura_card, altura_card, espaco = 190, 96, 16
    largura = len(cartoes) * largura_card + (len(cartoes) - 1) * espaco
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura_card}" '
        f'viewBox="0 0 {largura} {altura_card}" font-family="Segoe UI, Ubuntu, Helvetica, Arial, sans-serif" '
        'role="img" aria-label="Estatísticas do GitHub">'
    ]
    for i, (rotulo, valor, cor) in enumerate(cartoes):
        x = i * (largura_card + espaco)
        partes.append(
            f'<g transform="translate({x},0)">'
            f'<rect width="{largura_card}" height="{altura_card}" rx="14" fill="#1d2021"/>'
            f'<rect x="0" y="0" width="6" height="{altura_card}" rx="3" fill="{cor}"/>'
            f'<text x="26" y="44" fill="{cor}" font-size="30" font-weight="700">{formatar(valor)}</text>'
            f'<text x="26" y="72" fill="#a89984" font-size="13" letter-spacing=".4">{rotulo.upper()}</text>'
            "</g>"
        )
    partes.append("</svg>\n")
    return "".join(partes)


if __name__ == "__main__":
    Path(__file__).resolve().parent.parent.joinpath("stats.svg").write_text(svg(coletar()), encoding="utf-8")
