"""Ponto de entrada da automação ROTA LIVRE."""

import logging

from config import PASTA_SAIDA, ler_configuracao
from src.leitor import ErroLeitura, carregar_registros
from src.robo import gravar_relatorio, processar


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = ler_configuracao()

    try:
        registros, origem = carregar_registros(config)
    except ErroLeitura as erro:
        logging.error("Falha na entrada. %s", erro)
        return 1

    relatorio = processar(registros, origem)
    try:
        caminho = gravar_relatorio(relatorio, PASTA_SAIDA)
    except (OSError, ValueError, RecursionError):
        logging.error("Não foi possível gerar o relatório JSON.")
        return 1
    logging.info("Origem dos dados: %s. Relatório: %s", origem, caminho)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
