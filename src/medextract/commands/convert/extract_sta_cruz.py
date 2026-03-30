import re

import fitz


def extract_sta_cruz(pdf_path: str) -> list[str]:
    """
    Extracts all accounts from a PDF file of the Santa Cruz Hospital.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        List[str]: A list of strings, where each string contains the details of
        one account.

    Raises:
        ValueError: If the file cannot be opened as a PDF.
    """
    try:
        document = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Não foi possível abrir o arquivo PDF '{pdf_path}': {e}") from e

    try:
        full_text = ""
        for page in document:
            full_text += page.get_text()
    finally:
        document.close()

    # Normaliza
    lines = full_text.splitlines()
    lines = [re.sub(r"\s+", " ", line).strip() for line in lines if line.strip()]

    accounts: list[str] = []
    current_account: list[str] = []
    collecting = False

    for line in lines:
        if line.endswith("Material"):
            # início de uma conta
            if current_account:
                accounts.append("\n".join(current_account))
                current_account = []
            collecting = True

        if collecting:
            current_account.append(line)

        if line.startswith("Total "):
            # fim da conta
            collecting = False
            accounts.append("\n".join(current_account))
            current_account = []

    if current_account:
        accounts.append("\n".join(current_account))

    return accounts
