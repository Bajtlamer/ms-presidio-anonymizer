#!/bin/bash
pip install presidio-analyzer presidio-anonymizer spacy anthropic

# English model (required)
python -m spacy download en_core_web_lg

# Czech model (optional but recommended for CZ documents)
# Community model, NER quality is decent for names
pip install https://huggingface.co/spacy/cs_core_news_lg/...
# OR use the smaller version:
python -m spacy download cs_core_news_sm