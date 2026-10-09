import os
import xml.etree.ElementTree as ET

import requests

GROBID_URL = os.getenv("GROBID_URL", "http://localhost:8070")
TEI = {"t": "http://www.tei-c.org/ns/1.0"}


def _text(el):
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def grobid_available(timeout=3):
    try:
        return requests.get(f"{GROBID_URL}/api/isalive", timeout=timeout).text.strip() == "true"
    except requests.RequestException:
        return False


def parse_header_tei(xml_text):
    """Convert GROBID header TEI XML into the same dict shape as MetaData.parse_paper."""
    root = ET.fromstring(xml_text)
    result = {
        "TITLE": "",
        "METADATA": {"AUTHORS": [], "EMAILS": [], "AFFILIATIONS": [], "KEYWORDS": []},
        "ABSTRACT": "",
    }

    title = root.find(".//t:titleStmt/t:title", TEI)
    result["TITLE"] = _text(title)

    authors, emails, affiliations = [], [], []
    for author in root.findall(".//t:sourceDesc//t:author", TEI):
        parts = [_text(n) for n in author.findall("t:persName/t:forename", TEI)]
        parts += [_text(author.find("t:persName/t:surname", TEI))]
        name = " ".join(p for p in parts if p)
        if name and name not in authors:
            authors.append(name)
        for mail in author.findall("t:email", TEI):
            m = _text(mail)
            if m and m not in emails:
                emails.append(m)
        for aff in author.findall("t:affiliation", TEI):
            org = ", ".join(_text(o) for o in aff.findall("t:orgName", TEI))
            addr = _text(aff.find("t:address", TEI))
            full = ", ".join(x for x in (org, addr) if x)
            if full and full not in affiliations:
                affiliations.append(full)

    result["METADATA"]["AUTHORS"] = authors
    result["METADATA"]["EMAILS"] = emails
    result["METADATA"]["AFFILIATIONS"] = affiliations
    result["METADATA"]["KEYWORDS"] = [
        _text(t) for t in root.findall(".//t:profileDesc//t:keywords//t:term", TEI) if _text(t)
    ]
    result["ABSTRACT"] = _text(root.find(".//t:profileDesc/t:abstract", TEI))
    return result


def extract_with_grobid(pdf_path, timeout=120):
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{GROBID_URL}/api/processHeaderDocument",
            files={"input": f},
            data={"consolidateHeader": "0"},
            timeout=timeout,
        )
    resp.raise_for_status()
    return parse_header_tei(resp.text)


def merge_results(primary, fallback):
    """Use `primary` (GROBID) values, filling any empty field from `fallback` (OCR parser)."""
    merged = {
        "TITLE": primary.get("TITLE") or fallback.get("TITLE", ""),
        "ABSTRACT": primary.get("ABSTRACT") or fallback.get("ABSTRACT", ""),
        "METADATA": {},
    }
    pm, fm = primary.get("METADATA", {}), fallback.get("METADATA", {})
    for key in ("AUTHORS", "EMAILS", "AFFILIATIONS", "KEYWORDS"):
        merged["METADATA"][key] = pm.get(key) or fm.get(key, [])
    return merged


def process_fulltext(pdf_path, timeout=300):
    """Run GROBID's full-document endpoint. Returns (tei_xml, metadata_dict)."""
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{GROBID_URL}/api/processFulltextDocument",
            files={"input": f},
            data={"consolidateHeader": "0", "consolidateCitations": "0"},
            timeout=timeout,
        )
    resp.raise_for_status()
    return resp.text, parse_header_tei(resp.text)


# ---------------------------------------------------------------------------
# Regex fallback: recover title / abstract / keywords from the TEI body text when
# GROBID's header model left them empty (e.g. "Abstract—..." inside a plain <p>).
# ---------------------------------------------------------------------------
import re

_DASH = r"[:\-–—−.\s]*"
_KW_LABEL = re.compile(r"(?i)\b(?:index\s+terms?|key\s*[- ]?words?)\b" + _DASH)
_ABS_LABEL = re.compile(r"(?i)\babstract\b" + _DASH)
_ABS_END = re.compile(
    r"(?i)\b(?:index\s+terms?|key\s*[- ]?words?)\b"
    r"|\b(?:(?:1|I)\s*[.:]?\s+)?introduction\b"
)
_KW_END = re.compile(
    r"\n|(?<=[a-z0-9\)])\.\s+(?=[A-Z0-9])|\b(?:(?:1|I)\s*[.:]?\s+)?introduction\b|\babstract\b",
    re.I,
)


def body_text(root, limit=8000):
    body = root.find(".//t:text/t:body", TEI)
    if body is None:
        return ""
    parts = []
    for el in body.iter():
        if el.tag.endswith("}head") or el.tag.endswith("}p"):
            txt = _text(el)
            if txt:
                parts.append(txt)
        if sum(len(p) for p in parts) > limit:
            break
    return "\n".join(parts)[:limit]


def regex_abstract(text):
    m = _ABS_LABEL.search(text[:6000])
    if not m:
        return ""
    rest = text[m.end():]
    end = _ABS_END.search(rest)
    if end and end.start() > 100:
        rest = rest[:end.start()]
    nl = rest.find("\n", 150)  # allow a paragraph break only after a reasonable length
    if nl != -1:
        rest = rest[:nl]
    rest = " ".join(rest.split())
    return rest if len(rest) >= 80 else ""


def regex_keywords(text):
    m = _KW_LABEL.search(text[:8000])
    if not m:
        return []
    rest = text[m.end():]
    end = _KW_END.search(rest)
    if end:
        rest = rest[:end.start()]
    rest = rest[:400]
    kws = [k.strip(" .;,—–-") for k in re.split(r"[,;·•]", " ".join(rest.split()))]
    return [k for k in kws if 1 < len(k) <= 80]


def parse_fulltext_tei(xml_text, use_regex=True):
    """Header fields from a fulltext TEI, with regex recovery for empty title/abstract/keywords."""
    result = parse_header_tei(xml_text)
    if not use_regex:
        return result
    root = ET.fromstring(xml_text)
    text = body_text(root)
    if not result["ABSTRACT"]:
        result["ABSTRACT"] = regex_abstract(text)
    if not result["METADATA"]["KEYWORDS"]:
        result["METADATA"]["KEYWORDS"] = regex_keywords(text)
    if not result["TITLE"]:
        head = root.find(".//t:text/t:body//t:head", TEI)
        h = _text(head)
        if 15 <= len(h) <= 300:
            result["TITLE"] = h
    return result


def extract_primary(pdf_path, timeout=300):
    """Primary extraction path: GROBID fulltext + regex recovery.

    Returns the metadata dict, or None if the result has no title and no authors
    (e.g. a scanned PDF with no text layer) so the caller can fall back to OCR.
    """
    xml_text, _ = process_fulltext(pdf_path, timeout=timeout)
    result = parse_fulltext_tei(xml_text)
    if not result["TITLE"] and not result["METADATA"]["AUTHORS"]:
        return None
    return result
