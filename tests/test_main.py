import re

from typer.testing import CliRunner

from medextract.__main__ import app

runner = CliRunner()


def strip_ansi(text):
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_help_message():
    result = runner.invoke(app, ["--help"])
    output = strip_ansi(result.output)
    assert result.exit_code == 0
    assert "--help" in output
