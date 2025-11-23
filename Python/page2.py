import re
import spacy
import os
import unicodedata
import string

# Load spaCy 
def load_tagged_lines(text):
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("[TITLE]"):
            lines.append(("[TITLE]", line.replace("[TITLE]", "").strip()))
        elif line.startswith("[PLAIN_TEXT]"):
            lines.append(("[PLAIN_TEXT]", line.replace("[PLAIN_TEXT]", "").strip()))
    return lines


def validate_with_regex(text,AFFILIATION_REGEX):

    # Final regex to validate & clean
    match = AFFILIATION_REGEX.search(text)
    return match.group(1).strip() if match else None

def extract_affiliation_hybrid(text, nlp):
    affiliations = set()

    # ---------------------------
    # Step 1: Extract USING REGEX first
    # ---------------------------
    AFFILIATION_CANDIDATE_REGEX = re.compile(
        r"[A-Z][A-Za-z&., '\-]*(Université|University|Institute|College|Hospital|Center|Centre|School|Laboratory|Labs|Research)[A-Za-z&., '\-]*"
    )
    AFFILIATION_REGEX = re.compile(
        r"\b([A-Z][A-Za-z&., '\-]*(Université|University|Institute|College|Hospital|Center|Centre|School|Laboratory|Labs|Research)[A-Za-z&., '\-]*)\b"
    )
    candidates = AFFILIATION_CANDIDATE_REGEX.findall(text)
    
    # candidates is list of tuples — extract first element
    candidates = [c[0] if isinstance(c, tuple) else c for c in candidates]

    # ---------------------------
    # Step 2: Run each candidate through spaCy ORG classifier
    # ---------------------------
    for cand in candidates:
        doc = nlp(cand)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                cleaned = validate_with_regex(ent.text,AFFILIATION_REGEX)
                if cleaned:
                    affiliations.add(cleaned)

    # ---------------------------
    # Step 3: also allow direct regex extraction
    # ---------------------------
    for match in re.findall(AFFILIATION_REGEX, text):
        affiliations.add(match[0])

    return list(affiliations)

def is_affiliation_line(text,nlp):

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "!”": "", "!?": "", "?!": "",
        "”": "", "“": "", "’": "'", "‘": "'",
        "—": "-", "–": "-",
        "·": " ", "•": " ", "|": " ",
        "{": " ", "}": " ", "[": " ", "]": " ",
        "  ": " "
    }

    for wrong, right in replacements.items():
        text = text.replace(wrong, right)

        text = re.sub(r"([.,])([A-Za-z])", r"\1 \2", text)

        text = re.sub(r"[^\w\s.,@\-()/&]", " ", text)

        text = re.sub(r"\s+", " ", text)
    ans  = extract_affiliation_hybrid(text, nlp)
    if (len(ans) == 0):return ans
    return ans[0].split(",")

def extract_persons(text,nlp):
    replacements = {
        "!”": "", "!?": "", "?!": "",
        "”": "", "“": "", "’": "'", "‘": "'",
        "—": "-", "–": "-",
        "·": " ", "•": " ", "|": " ",
        "{": " ", "}": " ", "[": " ", "]": " ",
        "  ": " ",
        '?': ','
    }

    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    doc = nlp(text)
    return [ent.text.strip(",") for ent in doc.ents if ent.label_ == "PERSON"]

def clean(text):
    return text.strip(" :\t\n")

def parse_paper(lines,nlp):
    result = {
        "TITLE": "",
        "METADATA": {
            "AUTHORS": [],
            "EMAILS": [],
            "AFFILIATIONS": [],
            "KEYWORDS": []
        },
        "ABSTRACT": ""
    }

    authors = set()
    emails = set()
    affiliations = set()
    keywords = []
    
    abstract = []
    in_abstract = False
    
    main_title_found = False

    i = 0
    while i < len(lines):
        tag, content = lines[i]
        text = content.strip()

        # 1. DETECT MAIN TITLE
        if tag == "[TITLE]" and not main_title_found:
            result["TITLE"] = clean(text)
            main_title_found = True
            i += 1
            continue
        

        # 2. DETECT ABSTRACT START
        txt_lower = text.lower()

        if ("abstract" in txt_lower[:20] or txt_lower.startswith("abstract")) and not in_abstract:
            in_abstract = True
            
            # Remove "Abstract" word if present
            text = re.sub(r"^abstract[:\s-]*", "", text, flags=re.I).strip()
            if text:
                abstract.append(text)
            i += 1
            continue

        # 3. CAPTURE ABSTRACT CONTENT
        if in_abstract:
            # Stop if KEYWORD encountered
            if "keyword" in txt_lower or "index terms" in txt_lower:
                in_abstract = False

                # Extract keywords immediately
                kw = re.sub(r"(?i)^[^\w]*?(?:keywords?|index\s+terms?)\b[:\s-]*", "", text).strip()
                kw = kw.split(",")
                keywords.extend([clean(k) for k in kw if k.strip()])
                i += 1
                continue
            
            # Stop if NEW title is encountered
            if tag == "[TITLE]":
                in_abstract = False
                i += 1
                continue

            # Append abstract line
            abstract.append(text)

            # If a sentence ends with period, abstract ends
            if text.endswith("."):
                in_abstract = False
            i += 1
            continue

        # 4. DETECT KEYWORDS (non-abstract case)
        if tag == "[TITLE]" and re.search(r"\b(?:keywords?|index terms?)\b", text, flags=re.I):
    # Move to next line which must be PLAIN_TEXT
            j = i + 1
            keyword_buffer = []
            count = 0
            while j < len(lines):
                nt, nc = lines[j]
                nc = nc.strip()
                

                # Stop if a NEW title starts → end of keyword block
                if nt == "[TITLE]":
                    break
                if nt == "[PLAIN_TEXT]":
                    count+=1
                    if count > 1:
                        break
                

                # Collect this line
                keyword_buffer.append(nc)

                # Stop at first period
                if "." in nc:
                    break

                j += 1

            # Join, remove period, split by comma
            kw_text = " ".join(keyword_buffer)
            kw_text = kw_text.split(".")[0]  # content only before period
            kws = [clean(k) for k in kw_text.split(",") if k.strip()]
            keywords.extend(kws)

            # Advance pointer
            i = j + 1
            continue
        if "keyword" in txt_lower or "index terms" in txt_lower:
            kw = re.sub(r"(?i)^[^\w]*?(?:keywords?|index\s+terms?)\b[:\s-]*", "", text).strip()
            kw = kw.split(",")
            keywords.extend([clean(k) for k in kw if k.strip()])
            i += 1
            continue
       
        # 5. EXTRACT EMAILS ANYWHERE
        def extract_emails(text):
            text = re.sub(r"{([^}]+)}\s*@\s*([\w\.-]+\.\w+)", 
                        lambda m: ", ".join([f"{x.strip()}@{m.group(2)}" 
                        for x in m.group(1).split(",")]), 
                        text)
            text = text.replace(" }@", "@").replace("} @", "@")
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            emails = re.findall(email_pattern, text)
            return list(set(emails))
        
        for x in extract_emails(text):
            emails.add(x)
       
        # 6. DETECT AUTHORS (NER)
        persons = extract_persons(text,nlp)
        for p in persons:
            authors.add(p.strip(string.punctuation))

        # ----------------------------
        # 7. DETECT AFFILIATIONS
        # ----------------------------
        aff =  is_affiliation_line(text,nlp)
        for x in aff:
            added = False
            x=x.strip()
            for author in authors:
                if author in x:
                    cleaned = x.replace(author, "").strip(" ,.-\n")
                    if cleaned:
                        affiliations.add(cleaned)
                    added = True
                    break
            
            # If no author name was found in x → add the full text
            if not added:
                affiliations.add(x) 

        i += 1

    # ----------------------------
    # FINAL OUTPUT
    # ----------------------------
    result["METADATA"]["AUTHORS"] = list(authors)
    result["METADATA"]["EMAILS"] = list(emails)
    result["METADATA"]["AFFILIATIONS"] = list(affiliations)
    result["METADATA"]["KEYWORDS"] = keywords
    result["ABSTRACT"] = " ".join(abstract).strip()

    return result

def SummarizeSection():
    # print(os.path.join(os.getcwd(),".\data\content.txt"))
    with open(os.path.join(os.getcwd(),"./data/content.txt"), 'r', encoding='utf-8', errors='replace') as file:
        text = file.read()
    nlp = spacy.load("en_core_web_md")
    text = load_tagged_lines(text)
    res = parse_paper(text,nlp)
    return res
if __name__ == '__main__':
    SummarizeSection()