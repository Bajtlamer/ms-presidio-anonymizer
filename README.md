# Text anonymizer bazed on Microsoft Presidio

CLI tool for anonymizing Markdown files before sending to Claude CLI.
Works with mixed EN/CZ content. Designed for Obsidian vaults.

## Workflow

    anonymize report.md
    # -> report.anon.md   (safe to send)
    # -> report.anon.map  (stays local, never leaves your machine)

    claude report.anon.md

    # If you want Claude's response with real names restored:
    deanonymize claude_response.md --map report.anon.map

## Shell aliases (add to ~/.zshrc or ~/.bashrc)

    alias anonymize="python /path/to/md_anonymizer/cli.py anonymize"
    alias deanonymize="python /path/to/md_anonymizer/cli.py deanonymize"

## Piping directly into Claude CLI

    python cli.py anonymize report.md --stdout | claude

## What gets anonymized

    PERSON, ORG, LOCATION        via spaCy NER (EN + CZ)
    EMAIL, URL, IP_ADDRESS       via regex
    PHONE                        via regex (CZ/SK +420/+421 + generic)
    CZ_RC (rodne cislo)          via regex
    CZ_ICO, CZ_DIC               via regex
    IBAN, CREDIT_CARD            via regex

## What is preserved

    Markdown headings, bold, italic, lists
    Code blocks (``` fenced)
    YAML frontmatter (--- ... ---)

## Rychlý start po zkopírování souborů:

```
cd ~/md_anonymizer
bash install.sh
```
### Přidej do ~/.zshrc:
```
alias anonymize="python ~/md_anonymizer/cli.py anonymize"
alias deanonymize="python ~/md_anonymizer/cli.py deanonymize"
```
### Použití:
```
anonymize muj_report.md
claude muj_report.anon.md
```