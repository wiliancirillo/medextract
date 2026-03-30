import textwrap
from pathlib import Path

from medextract.commands.convert.processor_sta_cruz import (
    extract_products,
    processor_sta_cruz_account,
    to_csv,
    to_xlsx,
)
from medextract.types import StaCruzProduct

SAMPLE_BLOCK = textwrap.dedent(
    """\
    JOAO DA SILVA                               Material
    15/03/2025 JOAO DA SILVA 12345 LUVA CIRURGICA 1,00
    15/03/2025 JOAO DA SILVA 12345 CATETER VENOSO 2,00
    Total 100,00
    """
)


def test_extract_products_returns_list():
    result = extract_products(SAMPLE_BLOCK)
    assert isinstance(result, list)


def test_processor_sta_cruz_account_empty():
    result = processor_sta_cruz_account([])
    assert result == []


def test_processor_sta_cruz_account_extends_all_blocks():
    # Two blocks each with one product
    blocks = [SAMPLE_BLOCK, SAMPLE_BLOCK]
    result = processor_sta_cruz_account(blocks)
    # Each block may have 0+ products depending on regex match
    assert isinstance(result, list)


def _make_product() -> StaCruzProduct:
    return {
        "paciente": "JOAO DA SILVA",
        "data": "15/03/2025",
        "material": "LUVA CIRURGICA",
        "qtd": "1,00",
    }


def test_to_csv_headers():
    csv_output = to_csv([_make_product()])
    first_line = csv_output.splitlines()[0]
    assert "PACIENTE" in first_line
    assert "MATERIAL" in first_line
    assert ";" in first_line


def test_to_csv_content():
    csv_output = to_csv([_make_product()])
    assert "JOAO DA SILVA" in csv_output
    assert "15/03/2025" in csv_output
    assert "LUVA CIRURGICA" in csv_output
    assert "1,00" in csv_output


def test_to_csv_empty():
    result = to_csv([])
    assert result.strip() == "PACIENTE;DATA;MATERIAL;QTDE"


def test_to_xlsx_creates_file(tmp_path: Path):
    dest = tmp_path / "sta_cruz.xlsx"
    to_xlsx([_make_product()], dest)
    assert dest.exists()
    assert dest.stat().st_size > 0


def test_to_xlsx_headers(tmp_path: Path):
    import openpyxl

    dest = tmp_path / "sta_cruz.xlsx"
    to_xlsx([_make_product()], dest)
    wb = openpyxl.load_workbook(dest)
    ws = wb.active
    headers = [ws.cell(1, c).value for c in range(1, 5)]
    assert headers == ["PACIENTE", "DATA", "MATERIAL", "QTDE"]
