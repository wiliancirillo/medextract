import textwrap
from pathlib import Path

import pytest

from medextract.commands.convert.processor_account import (
    aggregate_lotes,
    clean_convenio,
    clean_qtde,
    extract_account_details,
    extract_field,
    processor_account,
    remove_leading_zeros,
    to_csv,
    to_xlsx,
)
from medextract.types import Account

SAMPLE_ACCOUNT_TEXT = textwrap.dedent(
    """\
    Internação : 12345 Prontuario : 67890
    Paciente: JOAO DA SILVA Prontuario
    Data : 08/05/2025
    Convenio : SUS Medico Executante
    Medico Executante : DR FULANO
    Cirurgia(s): CIRURGIA XPTO
    Produto         Quantidade  Lote    Dt.Valid
    PRODUTO ALPHA   1           UN  ABC123  01/01/2026
    PRODUTO BETA    2           UN  000XYZ  01/06/2026
    ============================================================================================================
    """
)


def test_extract_field_found():
    result = extract_field(SAMPLE_ACCOUNT_TEXT, r"Paciente:\s*([^\n]+?)(?=\sProntuario|$)")
    assert result == "JOAO DA SILVA"


def test_extract_field_not_found():
    result = extract_field(SAMPLE_ACCOUNT_TEXT, r"NaoExiste:\s*(.+)")
    assert result == "Not Found"


def test_extract_account_details_keys():
    details = extract_account_details(SAMPLE_ACCOUNT_TEXT)
    assert "paciente" in details
    assert "data_de_uso" in details
    assert "convenio" in details
    assert "medico" in details
    assert "cirurgias" in details
    assert "produtos" in details
    assert "infos" in details


def test_extract_account_details_values():
    details = extract_account_details(SAMPLE_ACCOUNT_TEXT)
    assert details["paciente"] == "JOAO DA SILVA"
    assert details["data_de_uso"] == "08/05/2025"
    assert details["medico"] == "DR FULANO"
    assert details["infos"]["internacao"] == "12345"
    assert details["infos"]["prontuario"] == "67890"


def test_remove_leading_zeros():
    assert remove_leading_zeros("00042") == "42"
    assert remove_leading_zeros("0") == "0"
    assert remove_leading_zeros("000") == "0"
    assert remove_leading_zeros("ABC") == "ABC"


def test_clean_qtde_valid():
    assert clean_qtde("1,000") == 1
    assert clean_qtde("2") == 2


def test_clean_qtde_invalid():
    assert clean_qtde("abc") is None


def test_clean_convenio():
    assert clean_convenio("SUS Intercambio londrina", ["Intercambio", "londrina"]) == "SUS"
    assert clean_convenio("UNIMED", []) == "UNIMED"


def test_processor_account_returns_list():
    result = processor_account([SAMPLE_ACCOUNT_TEXT])
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def _make_account() -> Account:
    return {
        "paciente": "JOAO DA SILVA",
        "data_de_uso": "08/05/2025",
        "convenio": "SUS",
        "medico": "DR FULANO",
        "cirurgias": {"descricao": "CIRURGIA XPTO"},
        "produtos": [
            {"nome": "PRODUTO ALPHA", "qt_lote": 2, "lote": "ABC123", "dt_valid": "01/01/2026"},
            {"nome": "PRODUTO BETA", "qt_lote": 1, "lote": "XYZ", "dt_valid": "01/06/2026"},
        ],
        "infos": {"internacao": "12345", "prontuario": "67890"},
    }


def test_aggregate_lotes_sums_same_lote():
    account: Account = {
        "paciente": "P",
        "data_de_uso": "01/01/2025",
        "convenio": "SUS",
        "medico": "DR",
        "cirurgias": {"descricao": ""},
        "produtos": [
            {"nome": "X", "qt_lote": 3, "lote": "L1", "dt_valid": "01/01/2026"},
            {"nome": "X", "qt_lote": 2, "lote": "L1", "dt_valid": "01/01/2026"},
        ],
        "infos": {"internacao": "", "prontuario": ""},
    }
    result = aggregate_lotes([account])
    assert len(result) == 1
    assert result[0]["qt_lote"] == 5


def test_to_csv_headers():
    csv_output = to_csv([_make_account()])
    first_line = csv_output.splitlines()[0]
    assert "PACIENTE" in first_line
    assert "LOTE" in first_line
    assert ";" in first_line


def test_to_csv_content():
    csv_output = to_csv([_make_account()])
    assert "JOAO DA SILVA" in csv_output
    assert "08/05/2025" in csv_output
    assert "ABC123" in csv_output


def test_to_csv_against_fixture():
    """Verifica que o CSV gerado a partir do PDF de fixture bate com o esperado."""
    fixture_pdf = Path("tests/fixtures/input_example.pdf")
    fixture_csv = Path("tests/fixtures/output_example.csv")
    if not fixture_pdf.exists() or not fixture_csv.exists():
        pytest.skip("Fixtures não encontradas")

    from medextract.commands.convert.extract_account import extract_account

    raw = extract_account(str(fixture_pdf))
    from medextract.commands.convert.processor_account import processor_account as pa

    accounts = pa(raw)
    result = to_csv(accounts)
    expected = fixture_csv.read_text(encoding="utf-8")
    assert result.replace("\r\n", "\n") == expected


def test_to_xlsx_creates_file(tmp_path: Path):
    dest = tmp_path / "out.xlsx"
    to_xlsx([_make_account()], dest)
    assert dest.exists()
    assert dest.stat().st_size > 0


def test_to_xlsx_has_correct_headers(tmp_path: Path):
    import openpyxl

    dest = tmp_path / "out.xlsx"
    to_xlsx([_make_account()], dest)
    wb = openpyxl.load_workbook(dest)
    ws = wb.active
    headers = [ws.cell(1, c).value for c in range(1, 7)]
    assert headers == ["PACIENTE", "DATA DE USO", "CONVENIO", "MEDICO", "LOTE", "QT LOTE"]
