import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path


FONTES = [
    {
        "nome": "TecMundo",
        "url": "https://rss.tecmundo.com.br/feed/",
    },
    {
        "nome": "Canaltech",
        "url": "https://canaltech.com.br/rss/",
    },
    {
        "nome": "Tecnoblog",
        "url": "https://tecnoblog.net/feed/",
    },
    {
        "nome": "Hardware.com.br",
        "url": "https://www.hardware.com.br/feed/",
    },
]


LIMITE_POR_FONTE = 8
LIMITE_TOTAL = 30


def limpar_html(texto):
    if not texto:
        return ""

    texto = unescape(texto)
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def encontrar_texto(elemento, nomes):
    for nome in nomes:
        encontrado = elemento.find(nome)

        if encontrado is not None and encontrado.text:
            return encontrado.text.strip()

    return ""


def encontrar_link(elemento):
    # RSS tradicional
    link = elemento.find("link")

    if link is not None and link.text:
        return link.text.strip()

    # Atom
    for link in elemento.findall("{http://www.w3.org/2005/Atom}link"):
        href = link.attrib.get("href")

        if href:
            return href

    # Caso venha como dc:link ou outro namespace
    for filho in elemento:
        if filho.tag.lower().endswith("link"):
            if filho.text:
                return filho.text.strip()

            href = filho.attrib.get("href")

            if href:
                return href

    return ""


def encontrar_data(elemento):
    possibilidades = [
        "pubDate",
        "published",
        "updated",
        "date",
        "{http://purl.org/dc/elements/1.1/}date",
        "{http://www.w3.org/2005/Atom}published",
        "{http://www.w3.org/2005/Atom}updated",
    ]

    for nome in possibilidades:
        encontrado = elemento.find(nome)

        if encontrado is not None and encontrado.text:
            return encontrado.text.strip()

    # Procura qualquer campo relacionado à data
    for filho in elemento:
        nome = filho.tag.lower()

        if any(palavra in nome for palavra in ["date", "published", "updated"]):
            if filho.text:
                return filho.text.strip()

    return ""


def converter_data(data_texto):
    if not data_texto:
        return None

    # RSS normalmente usa RFC 2822
    try:
        data = parsedate_to_datetime(data_texto)

        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)

        return data.astimezone(timezone.utc)
    except Exception:
        pass

    # Tenta ISO 8601
    try:
        data = datetime.fromisoformat(
            data_texto.replace("Z", "+00:00")
        )

        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)

        return data.astimezone(timezone.utc)
    except Exception:
        return None


def buscar_feed(fonte):
    requisicao = urllib.request.Request(
        fonte["url"],
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; CPG-News/1.0; +https://github.com/)"
            )
        },
    )

    try:
        with urllib.request.urlopen(
            requisicao,
            timeout=20
        ) as resposta:

            conteudo = resposta.read()

        raiz = ET.fromstring(conteudo)

    except Exception as erro:
        print(
            f"[AVISO] Não foi possível acessar "
            f"{fonte['nome']}: {erro}"
        )

        return []

    itens = []

    # RSS
    itens_rss = raiz.findall(".//item")

    # Atom
    if not itens_rss:
        itens_rss = raiz.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )

    for item in itens_rss[:LIMITE_POR_FONTE]:

        titulo = encontrar_texto(
            item,
            [
                "title",
                "{http://www.w3.org/2005/Atom}title",
            ],
        )

        link = encontrar_link(item)

        data_texto = encontrar_data(item)

        data = converter_data(data_texto)

        if not titulo or not link:
            continue

        titulo = limpar_html(titulo)

        itens.append(
            {
                "titulo": titulo,
                "fonte": fonte["nome"],
                "link": link,
                "data": (
                    data.isoformat()
                    if data
                    else None
                ),
            }
        )

    return itens


def principal():

    noticias = []

    for fonte in FONTES:

        print(
            f"Buscando notícias de {fonte['nome']}..."
        )

        noticias_fonte = buscar_feed(fonte)

        print(
            f"  Encontradas: {len(noticias_fonte)}"
        )

        noticias.extend(noticias_fonte)

    # Remove duplicadas pelo link
    noticias_unicas = {}

    for noticia in noticias:
        noticias_unicas[noticia["link"]] = noticia

    noticias = list(noticias_unicas.values())

    # Ordena pelas mais recentes
    noticias.sort(
        key=lambda noticia: noticia["data"] or "",
        reverse=True
    )

    noticias = noticias[:LIMITE_TOTAL]

    resultado = {
        "atualizado_em": datetime.now(
            timezone.utc
        ).isoformat(),

        "noticias": noticias
    }

    caminho = Path(__file__).resolve().parent.parent

    arquivo_saida = caminho / "noticias.json"

    with open(
        arquivo_saida,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resultado,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    print()
    print(
        f"OK! {len(noticias)} notícias salvas em:"
    )
    print(arquivo_saida)


if __name__ == "__main__":
    principal()