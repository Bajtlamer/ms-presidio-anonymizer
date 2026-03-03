# anonymizer

A CLI tool for anonymizing Markdown files before sending them to Claude or other LLMs. Designed for use with Obsidian vaults containing mixed English and Czech content.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [What Gets Anonymized](#what-gets-anonymized)
- [What Is Preserved](#what-is-preserved)
- [Shell Aliases](#shell-aliases)

---

## Overview

The tool replaces sensitive entities in Markdown files with consistent placeholders like `[PERSON_1]` or `[EMAIL_2]`. It produces two output files: an anonymized `.anon.md` file that is safe to share, and a `.anon.map` file that stores the mapping for later restoration.

Typical workflow:

```
python cli.py anonymize report.md
# Produces: report.anon.md   (safe to send to an LLM)
#           report.anon.map  (stays local, never share this file)

python cli.py deanonymize report.anon.md
# Restores original values using the .map file
```

---

## Requirements

- Python 3.13 (spaCy is not compatible with Python 3.14 or later)

If Python 3.13 is not installed:

```bash
brew install python@3.13
```

---

## Installation

```bash
git clone <repo>
cd anonymizer
./install.sh
source .venv/bin/activate
```

The install script creates a `.venv/` directory in the project folder and installs the following packages:

- `presidio-analyzer`
- `presidio-anonymizer`
- `spacy`
- `anthropic`

It also downloads the spaCy English model `en_core_web_lg`.

---

## Usage

### Anonymize a file

```bash
python cli.py anonymize report.md
```

Produces `report.anon.md` and `report.anon.map` in the same directory.

### Anonymize and pipe directly to Claude

```bash
python cli.py anonymize report.md --stdout | claude
```

### Deanonymize (restore original values)

```bash
python cli.py deanonymize report.anon.md --map report.anon.map
```

The `--map` flag is optional. If the `.map` file is in the same directory with the same base name, it is detected automatically.

### Aliases

The commands `anon` and `deanon` are available as shorter aliases:

```bash
python cli.py anon report.md
python cli.py deanon report.anon.md
```

---

## What Gets Anonymized

### Via spaCy NER (English only, model: en_core_web_lg)

| Entity type | Description |
|-------------|-------------|
| `PERSON` | Personal names |
| `ORG` | Organizations |
| `LOCATION` | Locations and places |

Note: spaCy has no official Czech language model as of spaCy 3.8. Czech named entities (names, organizations) are not detected by NER.

### Via regex (works for both English and Czech content)

| Entity type | Description |
|-------------|-------------|
| `EMAIL` | Email addresses |
| `URL` | URLs |
| `IP_ADDRESS` | IPv4 and IPv6 addresses |
| `PHONE` | CZ/SK numbers with +420/+421 prefix, and generic international format |
| `CZ_RC` | Czech rodne cislo: 6 digits / 3-4 digits |
| `CZ_ICO` | Czech ICO: "ICO" followed by 8 digits |
| `CZ_DIC` | Czech DIC: "DIC CZ" followed by 8-10 digits |
| `IBAN` | International bank account numbers |
| `CREDIT_CARD` | Credit card numbers |

---

## What Is Preserved

The following content is never modified:

- Markdown formatting: headings, bold, italic, lists
- Fenced code blocks (``` and ~~~)
- YAML frontmatter (--- ... ---)

---

## Shell Aliases

For convenience, add the following aliases to `~/.zshrc` or `~/.bashrc`:

```bash
alias anonymize="python /path/to/anonymizer/cli.py anonymize"
alias deanonymize="python /path/to/anonymizer/cli.py deanonymize"
```

After reloading your shell, you can use the commands directly:

```bash
anonymize report.md
deanonymize report.anon.md
```
