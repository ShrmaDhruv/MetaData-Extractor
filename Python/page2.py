import re
import spacy
import os
import unicodedata
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

def validate_with_regex(text, AFFILIATION_REGEX):
    match = AFFILIATION_REGEX.search(text)
    return match.group(1).strip() if match else None

def extract_affiliation_hybrid(text, nlp):
    affiliations = set()
    
    # Regex definitions
    AFFILIATION_CANDIDATE_REGEX = re.compile(
        r"[A-Z][A-Za-z&., '\-]*(Université|University|Institute|College|Hospital|Center|Centre|School|Laboratory|Labs|Research)[A-Za-z&., '\-]*"
    )
    AFFILIATION_REGEX = re.compile(
        r"\b([A-Z][A-Za-z&., '\-]*(Université|University|Institute|College|Hospital|Center|Centre|School|Laboratory|Labs|Research)[A-Za-z&., '\-]*)\b"
    )
    
    candidates = AFFILIATION_CANDIDATE_REGEX.findall(text)
    # candidates is list of tuples — extract first element
    candidates = [c[0] if isinstance(c, tuple) else c for c in candidates]

    # Step 2: Run each candidate through spaCy ORG classifier
    for cand in candidates:
        doc = nlp(cand)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                cleaned = validate_with_regex(ent.text, AFFILIATION_REGEX)
                if cleaned:
                    affiliations.add(cleaned)

    # Step 3: also allow direct regex extraction
    for match in re.findall(AFFILIATION_REGEX, text):
        if isinstance(match, tuple):
            affiliations.add(match[0])
        else:
            affiliations.add(match)

    return list(affiliations)

def is_affiliation_line(text, nlp):
    text = unicodedata.normalize("NFKC", text)
    replacements = {
        "!”": ",", "!?": ",", "?!": ",", "”": ",", "“": ",", "’": ",", "‘": ",",
        "—": "-", "–": "-", "·": ",", "•": ",", "|": ",", "{": "(", "}": ")",
        "[": ")", "]": ")", "  ": " ", '?': ',','°': ',',"*!": ",","!": ",",
        "'*°": ",","°*'": ",","®": ","
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    
    text = re.sub(r"([.,])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"[^\w\s.,@\-()/&]", " ", text)
    text = re.sub(r"\s+", " ", text)
    
    ans = extract_affiliation_hybrid(text, nlp)
    if len(ans) == 0:
        return []
    return ans 

def extract_authors_heuristic(text):
    replacements = {
        "!”": ",", "!?": ",", "?!": ",", "”": ",", "“": ",", "’": ",", "‘": ",",
        "—": "-", "–": "-", "·": ",", "•": ",", "|": ",", "{": "(", "}": ")",
        "[": ")", "]": ")", "  ": " ", '?': ',','°': ',',"*!": ",","!": ",",
        "'*°": ",","°*'": ",","®": ",",";": ",","™": ",","©": ",","~": ",","`": ",","'": ","
        ,"\"": ","
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    text = re.sub(r"\{[^}]+\}", "", text) 
    text = text.replace("*", "").replace("†", "").replace("‡", "")    
    # Authors are usually separated by "," or " and "
    parts = re.split(r",| and |&| AND ", text)
    candidates = []
    # Words that indicate this segment is NOT an author
    non_person_keywords = [
        "university", "institute", "college", "research", "center", "centre", 
        "laboratory", "school", "department", "engineering", "science", 
        "abstract", "introduction", "keywords", "email", "http", "www", 
        "@", "member", "fellow", "ieee", "acm","technology","corporation",
        "inc","ltd","llc","company","hospital","clinic","medical","limited"
    ]
    for part in parts:
        part = part.strip()
        part_lower = part.lower()
        
        if len(part) < 2 or len(part) > 40:
            continue
            
        if any(char.isdigit() for char in part):
            continue
            
        if any(kw in part_lower for kw in non_person_keywords):
            continue
            
        # Filter D: Must have at least one capitalized word
        if not any(word[0].isupper() for word in part.split() if word):
            continue

        candidates.append(part)
        
    return candidates


def clean(text):
    return text.strip(" :\t\n")

def extract_emails_helper(text):
    text = re.sub(r"{([^}]+)}\s*@\s*([\w\.-]+\.\w+)", 
                  lambda m: ", ".join([f"{x.strip()}@{m.group(2)}" 
                  for x in m.group(1).split(",")]), 
                  text)
    text = text.replace(" }@", "@").replace("} @", "@")
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(email_pattern, text)))

# MAIN PARSING LOGIC (UPDATED)

def parse_paper(lines, nlp):
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

    main_title_found = False
    in_metadata_section = False # Only True BETWEEN Title and Abstract
    in_abstract = False
    
    i = 0
    while i < len(lines):
        tag, content = lines[i]
        text = content.strip()
        txt_lower = text.lower()

        # 1. DETECT MAIN TITLE
        if tag == "[TITLE]" and not main_title_found:
            result["TITLE"] = clean(text)
            main_title_found = True
            in_metadata_section = True 
            i += 1
            continue
        
        # 2. DETECT ABSTRACT START
        is_abstract_start = ("abstract" in txt_lower[:20] or txt_lower.startswith("abstract"))
        
        if is_abstract_start and not in_abstract:
            in_metadata_section = False  
            in_abstract = True
            
            text = re.sub(r"^abstract[:\s-]*", "", text, flags=re.I).strip()
            if text:
                abstract.append(text)
            i += 1
            continue

        if in_abstract:
            # Check if Abstract ends via Keywords or Index Terms
            if "keyword" in txt_lower or "index terms" in txt_lower:
                in_abstract = False
                kw = re.sub(r"(?i)^[^\w]*?(?:keywords?|index\s+terms?)\b[:\s-]*", "", text).strip()
                kw = kw.split(",")
                keywords.extend([clean(k) for k in kw if k.strip()])
                i += 1
                continue
            
            # Check if Abstract ends via a NEW Title tag
            if tag == "[TITLE]":
                in_abstract = False
                continue

            abstract.append(text)
            if text.endswith("."):
                in_abstract = False
            i += 1
            continue

        # 4. PROCESS METADATA SECTION (Between Title and Abstract)
        elif in_metadata_section:
            
            # A. Extract Emails
            for x in extract_emails_helper(text):
                emails.add(x)

            # B. Extract Authors (Persons)
            potential_authors = extract_authors_heuristic(text)
            for p in potential_authors:
                authors.add(p)

            # C. Extract Affiliations
            aff_candidates = is_affiliation_line(text, nlp)
            if len(aff_candidates) == 1:
                aff_candidates = aff_candidates[0].split(",")
            for x in aff_candidates:
                added = False
                x = x.strip()
                
                for author in authors:
                    if author in x:
                        cleaned = x.replace(author, "").strip(" ,.-\n")
                        if cleaned:
                            print(cleaned)
                            affiliations.add(cleaned)
                        added = True
                        break
                
                if not added:
                    affiliations.add(x)
            
            i += 1
            continue

        if "keyword" in txt_lower or "index terms" in txt_lower:
            if tag == "[TITLE]":
                j = i + 1
                keyword_buffer = []
                count = 0
                while j < len(lines):
                    nt, nc = lines[j]
                    nc = nc.strip()
                    if nt == "[TITLE]": break
                    if nt == "[PLAIN_TEXT]":
                        count += 1
                        if count > 1: break
                    keyword_buffer.append(nc)
                    if "." in nc: break
                    j += 1
                
                kw_text = " ".join(keyword_buffer).split(".")[0]
                kws = [clean(k) for k in kw_text.split(",") if k.strip()]
                keywords.extend(kws)
                i = j + 1
                continue
            else:
                kw = re.sub(r"(?i)^[^\w]*?(?:keywords?|index\s+terms?)\b[:\s-]*", "", text).strip()
                kw = kw.split(",")
                keywords.extend([clean(k) for k in kw if k.strip()])
                i += 1
                continue

        i += 1

    # FINAL OUTPUT
    result["METADATA"]["AUTHORS"] = list(authors)
    result["METADATA"]["EMAILS"] = list(emails)
    result["METADATA"]["AFFILIATIONS"] = list(affiliations)
    result["METADATA"]["KEYWORDS"] = keywords
    result["ABSTRACT"] = " ".join(abstract).strip()

    return result

def SummarizeSection():
    path = os.path.join(os.getcwd(), "./data/content.txt")    
    if not os.path.exists(path):
        print(f"File not found at {path}")
        return {}
    with open(path, 'r', encoding='utf-8', errors='replace') as file:
        text = file.read()
    
    nlp = spacy.load("en_core_web_md")
    lines = load_tagged_lines(text)
    res = parse_paper(lines, nlp)
    return res

if __name__ == '__main__':
    SummarizeSection()