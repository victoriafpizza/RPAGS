# ROTA LIVRE — Robotic Process Automation

FIAP Global Solution 2026.2 · Etapa 1 — Implementação Python e Resiliência  
Victoria Franceschini Pizza · RM 550609

O robô lê um lote de relatos de obstáculos urbanos e gera um relatório JSON com registros válidos, inválidos e duplicados. A implementação segue o enunciado da Etapa 1. O PDD e o contrato da API do ROTA LIVRE estavam indisponíveis no workspace.

## Execução no PowerShell do VS Code

Com Python 3.10 ou posterior disponível no terminal, execute:

```powershell
Set-Location -LiteralPath 'C:\RPAGS'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe .\main.py --arquivo .\dados\obstaculos_exemplo.json
```

O projeto usa a biblioteca padrão. O comando de instalação verifica o arquivo de dependências, que está vazio de pacotes externos. O exemplo gera seis itens, com quatro válidos, um inválido e um duplicado.

```powershell
.\.venv\Scripts\python.exe .\main.py --help
$LASTEXITCODE
```

O código de saída é `0` quando o relatório é gravado, inclusive se o lote contiver itens inválidos. Falhas de leitura ou escrita retornam `1` e erros nos argumentos retornam `2`.

## Origem dos dados

- **Arquivo local.** Use `--arquivo` com um JSON UTF-8 cuja raiz seja uma lista. Sem origem configurada, o robô usa o arquivo de exemplo.
- **API.** Use `--api-url` com a URL de consulta GET. A resposta deve ser uma lista JSON ou um objeto com a lista sob a chave de primeiro nível indicada por `--chave-lista`. Por exemplo, use `--chave-lista obstaculos` para uma resposta como `{"obstaculos": [...]}`.
- **Contingência.** Use `--contingencia` com um arquivo JSON local. O robô só lê esse arquivo após uma falha da API e identifica os dados como `contingencia` no relatório e no log.

Para consultar uma API com uma URL já definida na variável de ambiente `ROTA_API_URL`:

```powershell
.\.venv\Scripts\python.exe .\main.py --api-url $env:ROTA_API_URL --timeout 5 --tentativas 3 --intervalo 1
```

As variáveis em [.env.example](.env.example) podem ser definidas na sessão PowerShell com `$env:NOME = 'valor'`. O arquivo serve como referência de configuração. Argumentos explícitos têm precedência sobre as variáveis de ambiente.

## Regras de processamento

| Campo | Validação |
| --- | --- |
| `id` | Inteiro ou texto não vazio |
| `tipo`, `descricao`, `status` | Texto não vazio |
| `latitude` | Número entre −90 e 90, inclusive |
| `longitude` | Número entre −180 e 180, inclusive |

O robô valida todos os itens da lista e informa os motivos dos erros por registro. A primeira ocorrência válida de um ID recebe prioridade. As próximas ocorrências válidas do mesmo ID entram em `duplicados` com o motivo e a posição da primeira ocorrência válida. Na comparação, `101`, `"101"` e `" 101 "` representam o mesmo ID. O texto `"0101"` representa um ID distinto. A comparação usa apenas o ID e preserva os campos originais no relatório.

A prioridade é `alta` para rampa bloqueada ou travessia perigosa, `media` para calçada danificada e `baixa` para os demais tipos válidos. A classificação desconsidera diferenças de maiúsculas, acentos e espaços no tipo.

## Falhas e relatório

Uma entrada sem conteúdo, com sintaxe JSON inválida ou com estrutura incompatível gera uma mensagem de erro. Uma lista vazia é um lote válido com contagens zeradas. Respostas vazias ou inválidas da API, timeout, falhas de conexão e HTTP 408, 429 e 5xx permitem nova tentativa dentro do limite configurado. Outros erros HTTP encerram as tentativas. O log da API registra a causa sem imprimir URL, cabeçalhos ou corpo da resposta.

Cada execução bem-sucedida cria um novo arquivo `dados/saida/resultado_<id>.json` com a origem efetiva, as contagens e os itens de cada categoria. A posição dos registros começa em 1. Os arquivos de entrada permanecem disponíveis para conferência.
