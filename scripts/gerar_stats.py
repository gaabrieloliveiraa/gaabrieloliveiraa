#!/usr/bin/env python3
"""Gera estatisticas.svg (cartoes de estatisticas) com os numeros reais da conta, inclusive repositorios privados.

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
        " repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){totalCount}"
        " repositories(first:100,ownerAffiliations:OWNER){nodes{stargazerCount}}}}"
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
    estrelas = sum(r["stargazerCount"] for r in v["repositories"]["nodes"])
    return [
        ("Commits", commits, "#fabd2f"),
        ("Pull requests", v["pullRequests"]["totalCount"], "#8ec07c"),
        ("Issues", v["issues"]["totalCount"], "#fe8019"),
        ("Repositórios contribuídos", v["repositoriesContributedTo"]["totalCount"], "#83a598"),
        ("Estrelas recebidas", estrelas, "#d79921"),
        ("Anos de GitHub", anos, "#d3869b"),
    ]


def formatar(n):
    return f"{n:,}".replace(",", ".")


def svg(cartoes, colunas=3):
    largura_card, altura_card, espaco = 260, 88, 14
    linhas = -(-len(cartoes) // colunas)
    largura = colunas * largura_card + (colunas - 1) * espaco
    altura = linhas * altura_card + (linhas - 1) * espaco
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}" font-family="Segoe UI, Ubuntu, Helvetica, Arial, sans-serif" '
        'role="img" aria-label="Estatísticas do GitHub">'
    ]
    for i, (rotulo, valor, cor) in enumerate(cartoes):
        x = (i % colunas) * (largura_card + espaco)
        y = (i // colunas) * (altura_card + espaco)
        partes.append(
            f'<g transform="translate({x},{y})">'
            f'<rect width="{largura_card}" height="{altura_card}" rx="14" fill="#1d2021"/>'
            f'<rect x="0" y="0" width="6" height="{altura_card}" rx="3" fill="{cor}"/>'
            f'<text x="26" y="40" fill="{cor}" font-size="28" font-weight="700">{formatar(valor)}</text>'
            f'<text x="26" y="66" fill="#a89984" font-size="12.5" letter-spacing=".4">{rotulo.upper()}</text>'
            "</g>"
        )
    partes.append("</svg>\n")
    return "".join(partes)


if __name__ == "__main__":
    Path(__file__).resolve().parent.parent.joinpath("estatisticas.svg").write_text(svg(coletar()), encoding="utf-8")
