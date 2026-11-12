"""Processamento em lote e gravação do relatório."""

import json
from uuid import uuid4

from src.classificador import classificar
from src.duplicidade import chave_id
from src.validador import validar


def processar(registros, origem):
    validos = []
    invalidos = []
    duplicados = []
    primeira_posicao = {}

    for posicao, registro in enumerate(registros, start=1):
        erros = validar(registro)
        item = {"posicao": posicao, "registro": registro}
        if erros:
            invalidos.append({**item, "motivos": erros})
            continue

        chave = chave_id(registro["id"])
        if chave in primeira_posicao:
            duplicados.append({
                **item,
                "motivo": "Mesmo ID de um registro válido anterior.",
                "posicao_original": primeira_posicao[chave],
            })
        else:
            primeira_posicao[chave] = posicao
            validos.append({**item, "prioridade": classificar(registro["tipo"])})

    return {
        "origem": origem,
        "resumo": {
            "total": len(registros),
            "validos": len(validos),
            "invalidos": len(invalidos),
            "duplicados": len(duplicados),
        },
        "validos": validos,
        "invalidos": invalidos,
        "duplicados": duplicados,
    }


def gravar_relatorio(relatorio, pasta):
    conteudo = json.dumps(relatorio, ensure_ascii=False, allow_nan=False, indent=2)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"resultado_{uuid4().hex}.json"
    arquivo = caminho.open("x", encoding="utf-8", errors="backslashreplace")
    try:
        with arquivo:
            arquivo.write(conteudo + "\n")
    except OSError:
        caminho.unlink(missing_ok=True)
        raise
    return caminho
