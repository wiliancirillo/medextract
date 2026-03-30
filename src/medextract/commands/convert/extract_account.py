import re

import fitz


def extract_account(pdf_path: str) -> list[str]:
    """
    Extracts all accounts from a PDF file.

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

    # Split the text into lines
    lines = full_text.splitlines()

    lines = [re.sub(r"\s+", " ", line).strip() for line in lines]

    # Extract all accounts from the lines
    accounts: list[str] = []
    current_account: list[str] = []
    collecting = False

    for line in lines:
        if line.startswith("Internação :"):
            if current_account:
                accounts.append("\n".join(current_account))
                current_account = []
            collecting = True

        if collecting:
            current_account.append(line)

        # Line of equal signs marking the end of an account
        if line.startswith("=" * 108):
            collecting = False
            accounts.append("\n".join(current_account))
            current_account = []

    # Add the last account if no separator line was found
    if current_account:
        accounts.append("\n".join(current_account))

    return accounts
