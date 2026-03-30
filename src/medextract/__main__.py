import logging

import typer

from medextract.commands.convert_command import app as convert_app
from medextract.commands.report_command import app as report_app

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = typer.Typer(no_args_is_help=True)
app.add_typer(convert_app, name="convert", help="Converte PDFs em CSV ou XLSX")
app.add_typer(report_app, name="report", help="Gera relatórios consolidados")


if __name__ == "__main__":
    app()
