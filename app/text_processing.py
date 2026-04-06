from __future__ import annotations

import re


RE_QUOTE = re.compile(r"(^>.*$)", re.MULTILINE)
RE_SIGNATURE = re.compile(r"(--\s*\n.*)$", re.DOTALL)
RE_AD_FOOTER = re.compile(r"(unsubscribe|do not reply|marketing)[:\s\S]*$", re.IGNORECASE)

PHONE_RE = re.compile(r"(\+?\d[\d\-\s]{7,}\d)")
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
ADDRESS_RE = re.compile(r"\d{1,5}\s+[\w\s]+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln)", re.IGNORECASE)


def clean_body(text: str) -> str:
    x = RE_QUOTE.sub("", text)
    x = RE_SIGNATURE.sub("", x)
    x = RE_AD_FOOTER.sub("", x)
    x = re.sub(r"\n{3,}", "\n\n", x)
    return x.strip()


def mask_pii(text: str) -> str:
    x = PHONE_RE.sub("[PHONE]", text)
    x = EMAIL_RE.sub("[EMAIL]", x)
    x = ADDRESS_RE.sub("[ADDRESS]", x)
    return x
