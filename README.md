# medextract [![Tests](https://github.com/wiliancirillo/medextract/actions/workflows/tests.yml/badge.svg)](https://github.com/wiliancirillo/medextract/actions/workflows/tests.yml)

Ferramenta em Python para extrair dados de PDFs hospitalares e gerar relatórios em CSV ou XLSX.

## Instalação

```bash
git clone https://github.com/wiliancirillo/medextract.git
cd medextract

uv venv
source .venv/bin/activate.fish   # ou source .venv/bin/activate

uv pip install -e .
uv sync --dev   # inclui dependências de desenvolvimento (pytest, ruff, mypy)
```

## Uso

```bash
# Ajuda geral
uv run medextract --help

# Converter PDF padrão para CSV
uv run medextract convert to-csv data/input.pdf

# Converter PDF padrão para XLSX
uv run medextract convert to-csv data/input.pdf --format xlsx

# Converter múltiplos PDFs de uma vez (glob ou diretório)
uv run medextract convert to-csv "data/*.pdf"
uv run medextract convert to-csv data/

# Especificar arquivo de saída
uv run medextract convert to-csv data/input.pdf --output relatorio.xlsx --format xlsx

# Converter PDF do Hospital Santa Cruz
uv run medextract convert st-cruz data/sta_cruz.pdf
uv run medextract convert st-cruz data/sta_cruz.pdf --format xlsx

# Gerar relatório XLSX consolidado a partir de CSVs
uv run medextract report generate output/
uv run medextract report generate output/input.csv --output consolidado.xlsx
```

## Comandos

| Comando                    | Descrição                                                          |
|----------------------------|--------------------------------------------------------------------|
| `convert to-csv <pdf>`     | Extrai contas de PDF padrão → CSV ou XLSX                          |
| `convert st-cruz <pdf>`    | Extrai materiais do Hospital Santa Cruz → CSV ou XLSX              |
| `report generate [source]` | Consolida CSVs da pasta `output/` em um XLSX com abas por arquivo  |

### Opções comuns

| Opção                | Descrição                        |
|----------------------|----------------------------------|
| `--format csv\|xlsx` | Formato de saída (padrão: `csv`) |
| `--output <path>`    | Caminho do arquivo gerado        |

## Desenvolvimento

```bash
# Rodar testes
uv run python -m pytest -v

# Lint e formatação
uv run ruff check .
uv run ruff format .

# Verificação de tipos
uv run mypy src/
```

## Estrutura

```text
src/medextract/
├── __main__.py               # Entry point e CLI (Typer)
├── types.py                  # TypedDicts: Account, ProductInfo, StaCruzProduct
└── commands/
    ├── convert_command.py    # Comandos: convert to-csv / st-cruz
    ├── report_command.py     # Comando: report generate
    └── convert/
        ├── extract_account.py      # Extração de texto do PDF padrão
        ├── extract_sta_cruz.py     # Extração de texto do PDF Santa Cruz
        ├── processor_account.py    # Processamento + to_csv / to_xlsx
        └── processor_sta_cruz.py   # Processamento + to_csv / to_xlsx
```
