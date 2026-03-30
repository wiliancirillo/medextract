# medextract [![Tests](https://github.com/wiliancirillo/medextract/actions/workflows/tests.yml/badge.svg)](https://github.com/wiliancirillo/medextract/actions/workflows/tests.yml)

Ferramenta Python para extrair dados de PDFs hospitalares e gerar relatórios em **CSV** ou **XLSX**.

Suporta dois formatos de PDF:

- **Padrão** (`convert to-csv`) — PDFs com estrutura de internação e lista de produtos por lote
- **Hospital Santa Cruz** (`convert st-cruz`) — PDFs com materiais por paciente e data

---

## Requisitos

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes/ambientes)

## Instalação

```bash
git clone https://github.com/wiliancirillo/medextract.git
cd medextract

uv sync          # instala dependências de produção
uv sync --dev    # inclui pytest, ruff e mypy
```

---

## Uso rápido

```bash
# PDF único → CSV (salvo em output/)
uv run medextract convert to-csv data/input.pdf

# PDF único → XLSX formatado
uv run medextract convert to-csv data/input.pdf --format xlsx

# Múltiplos PDFs via glob ou diretório
uv run medextract convert to-csv "data/*.pdf"
uv run medextract convert to-csv data/

# Especificar destino
uv run medextract convert to-csv data/input.pdf --output relatorio.xlsx --format xlsx

# PDF Hospital Santa Cruz
uv run medextract convert st-cruz data/sta_cruz.pdf
uv run medextract convert st-cruz data/sta_cruz.pdf --format xlsx

# Consolidar CSVs da pasta output/ em um único XLSX (uma aba por arquivo)
uv run medextract report generate
uv run medextract report generate output/input.csv --output consolidado.xlsx
```

---

## Referência de comandos

### `convert to-csv <pdf_path>`

Extrai contas de um PDF padrão.

```text
medextract convert to-csv [OPTIONS] PDF_PATH

Argumentos:
  PDF_PATH    Caminho do PDF, glob ("data/*.pdf") ou diretório

Opções:
  -f, --format [csv|xlsx]   Formato de saída  [padrão: csv]
  -o, --output PATH         Arquivo de saída  [padrão: output/<nome>.csv]
```

**Colunas geradas:**

| Coluna        | Descrição                                   |
|---------------|---------------------------------------------|
| `PACIENTE`    | Nome do paciente                            |
| `DATA DE USO` | Data da cirurgia (dd/mm/aaaa)               |
| `CONVENIO`    | Convênio (palavras genéricas omitidas)      |
| `MEDICO`      | Médico executante                           |
| `LOTE`        | Número do lote (zeros à esquerda removidos) |
| `QT LOTE`     | Quantidade total do lote (agregada)         |

---

### `convert st-cruz <pdf_path>`

Extrai materiais de um PDF do Hospital Santa Cruz.

```text
medextract convert st-cruz [OPTIONS] PDF_PATH

Argumentos:
  PDF_PATH    Caminho do PDF, glob ("data/*.pdf") ou diretório

Opções:
  -f, --format [csv|xlsx]   Formato de saída  [padrão: csv]
  -o, --output PATH         Arquivo de saída  [padrão: output/<nome>_sta_cruz.csv]
```

**Colunas geradas:**

| Coluna     | Descrição                      |
|------------|--------------------------------|
| `PACIENTE` | Nome do paciente               |
| `DATA`     | Data de uso (dd/mm/aaaa)       |
| `MATERIAL` | Descrição do material          |
| `QTDE`     | Quantidade (formato: `1,00`)   |

---

### `report generate [source]`

Consolida um ou mais CSVs em um único XLSX com uma aba por arquivo.

```text
medextract report generate [OPTIONS] [SOURCE]

Argumentos:
  SOURCE    CSV ou diretório com CSVs  [padrão: output/]

Opções:
  -o, --output PATH   Caminho do XLSX gerado  [padrão: output/relatorio.xlsx]
```

---

## Fluxo de trabalho típico

```bash
# 1. Converter todos os PDFs da semana
uv run medextract convert to-csv "data/*.pdf"

# 2. Converter PDF do Santa Cruz
uv run medextract convert st-cruz data/sta_cruz.pdf

# 3. Gerar relatório consolidado com todos os CSVs gerados
uv run medextract report generate
# → output/relatorio.xlsx (uma aba por CSV)
```

---

## XLSX — formatação

Os arquivos XLSX gerados por `--format xlsx` e `report generate` incluem:

- Cabeçalho em **negrito** com fundo azul (`#4472C4`) e texto branco
- Largura das colunas ajustada automaticamente ao conteúdo

---

## Desenvolvimento

```bash
# Testes
uv run python -m pytest -v

# Lint
uv run ruff check .

# Formatação
uv run ruff format .

# Verificação de tipos
uv run mypy src/
```

---

## Estrutura do projeto

```text
medextract/
├── pyproject.toml
├── src/medextract/
│   ├── __main__.py              # Entry point e CLI (Typer)
│   ├── types.py                 # TypedDicts: Account, ProductInfo, StaCruzProduct
│   └── commands/
│       ├── convert_command.py   # Roteamento: convert to-csv / st-cruz
│       ├── report_command.py    # Comando: report generate
│       └── convert/
│           ├── extract_account.py     # Leitura e segmentação do PDF padrão
│           ├── extract_sta_cruz.py    # Leitura e segmentação do PDF Santa Cruz
│           ├── processor_account.py   # Parsing, agregação, to_csv / to_xlsx
│           └── processor_sta_cruz.py  # Parsing, to_csv / to_xlsx
└── tests/
    ├── fixtures/                # PDF e CSV de referência para testes
    ├── test_cli.py              # Testes de integração da CLI
    ├── test_processor_account.py
    └── test_processor_sta_cruz.py
```
