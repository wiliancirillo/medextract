import glob
import logging
import os
from enum import Enum
from pathlib import Path

import typer

from .convert.extract_account import extract_account
from .convert.extract_sta_cruz import extract_sta_cruz
from .convert.processor_account import (
    processor_account,
)
from .convert.processor_account import (
    to_csv as account_to_csv,
)
from .convert.processor_account import (
    to_xlsx as account_to_xlsx,
)
from .convert.processor_sta_cruz import (
    processor_sta_cruz_account,
)
from .convert.processor_sta_cruz import (
    to_csv as sta_cruz_to_csv,
)
from .convert.processor_sta_cruz import (
    to_xlsx as sta_cruz_to_xlsx,
)

logger = logging.getLogger(__name__)

app = typer.Typer()


class OutputFormat(str, Enum):
    csv = "csv"
    xlsx = "xlsx"


def _resolve_pdf_paths(source: str) -> list[Path]:
    """Resolve um caminho, glob ou diretório em uma lista de PDFs."""
    p = Path(source)
    if p.is_dir():
        paths = sorted(p.glob("*.pdf"))
        if not paths:
            raise typer.BadParameter(f"Nenhum PDF encontrado em '{source}'")
        return paths
    expanded = [Path(f) for f in sorted(glob.glob(source))]
    if expanded:
        return expanded
    if not p.exists():
        raise typer.BadParameter(f"Arquivo não encontrado: '{source}'")
    return [p]


def _output_path(base_name: str, fmt: OutputFormat, output: Path | None) -> Path:
    if output:
        return output
    os.makedirs("output", exist_ok=True)
    return Path("output") / f"{base_name}.{fmt.value}"


@app.command("to-csv")
def convert_to_csv(
    pdf_path: str = typer.Argument(..., help="Caminho do PDF, glob (*.pdf) ou diretório"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Arquivo de saída"),
    fmt: OutputFormat = typer.Option(OutputFormat.csv, "--format", "-f", help="Formato de saída"),
) -> None:
    """Converte PDF(s) padrão em CSV ou XLSX."""
    paths = _resolve_pdf_paths(pdf_path)

    for path in paths:
        logger.info("Processando %s", path)
        raw_accounts = extract_account(str(path))
        accounts = processor_account(raw_accounts)

        dest = _output_path(path.stem, fmt, output if len(paths) == 1 else None)

        if fmt == OutputFormat.xlsx:
            account_to_xlsx(accounts, dest)
        else:
            dest.write_text(account_to_csv(accounts), encoding="utf-8")

        typer.echo(f"Arquivo salvo em {dest}")


@app.command("st-cruz")
def convert_st_cruz(
    pdf_path: str = typer.Argument(..., help="Caminho do PDF, glob (*.pdf) ou diretório"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Arquivo de saída"),
    fmt: OutputFormat = typer.Option(OutputFormat.csv, "--format", "-f", help="Formato de saída"),
) -> None:
    """Converte PDF(s) do Hospital Santa Cruz em CSV ou XLSX."""
    paths = _resolve_pdf_paths(pdf_path)

    for path in paths:
        logger.info("Processando %s", path)
        raw_accounts = extract_sta_cruz(str(path))
        structured_accounts = processor_sta_cruz_account(raw_accounts)

        base_name = f"{path.stem}_sta_cruz"
        dest = _output_path(base_name, fmt, output if len(paths) == 1 else None)

        if fmt == OutputFormat.xlsx:
            sta_cruz_to_xlsx(structured_accounts, dest)
        else:
            dest.write_text(sta_cruz_to_csv(structured_accounts), encoding="utf-8")

        typer.echo(f"Arquivo salvo em {dest}")
