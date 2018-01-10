# ledgerutils

Plain Text Accounting Scripts

## import.py

Import some sources to ledger format. Currently support for Itau CSV, Nubank CSV and QIF format.

Syntax: ./import.py ACCOUNT INPUT_FILE [LEDGER_FILE]

 * ACCOUNT: Could be "itau", "nubank", or "qif"
 * INPUT_FILE: Path to the file
 * LEDGER_FILE: (Optional) Write the ledger file with the new entries

Rename `ledgerutils.conf.sample` to `ledgerutils.conf` to customize values for
Nubank
