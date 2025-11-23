import re
import spacy
import os
import unicodedata
import string

# ---------------------------------------------------------
# HELPER FUNCTIONS (Unchanged mostly, just logic flow below)
# ---------------------------------------------------------

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
    
    # Only splitting by comma if extraction found something, 
    # though usually hybrid returns specific chunks.
    # Returning the list directly is usually safer unless splitting is strictly required.
    return ans 

def extract_authors_heuristic(text):
    # 1. Cleaning: Remove specific markers often found in author lines
    # Remove email brackets like {a,b}@domain.com
    replacements = {
        "!”": ",", "!?": ",", "?!": ",", "”": ",", "“": ",", "’": ",", "‘": ",",
        "—": "-", "–": "-", "·": ",", "•": ",", "|": ",", "{": "(", "}": ")",
        "[": ")", "]": ")", "  ": " ", '?': ',','°': ',',"*!": ",","!": ",",
        "'*°": ",","°*'": ",","®": ",","'": ",",";": ",","™": ",","©": ",","~": ",","`": ","
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    text = re.sub(r"\{[^}]+\}", "", text) 
    # Remove punctuation that isn't a separator
    text = text.replace("*", "").replace("†", "").replace("‡", "")
    
    # 2. Split by common separators
    # Authors are usually separated by "," or " and "
    parts = re.split(r",| and |&", text)
    
    candidates = []
    
    # 3. Validation Filters
    # Words that indicate this segment is NOT an author
    non_person_keywords = [
        "university", "institute", "college", "research", "center", "centre", 
        "laboratory", "school", "department", "engineering", "science", 
        "abstract", "introduction", "keywords", "email", "http", "www", 
        "@", "member", "fellow", "ieee", "acm"
    ]
    
    for part in parts:
        part = part.strip()
        part_lower = part.lower()
        
        # Filter A: Length check (Too short or too long to be a name)
        if len(part) < 2 or len(part) > 40:
            continue
            
        # Filter B: Check for digits (Authors usually don't have numbers)
        if any(char.isdigit() for char in part):
            continue
            
        # Filter C: Keyword Blocklist
        if any(kw in part_lower for kw in non_person_keywords):
            continue
            
        # Filter D: Must have at least one capitalized word
        if not any(word[0].isupper() for word in part.split() if word):
            continue

        # If it passes all checks, assume it is an Asian/Western name
        candidates.append(part)
        
    return candidates

def extract_persons(text, nlp):
    replacements = {
        "!”": ",", "!?": ",", "?!": ",", "”": ",", "“": ",", "’": ",", "‘": ",",
        "—": "-", "–": "-", "·": ",", "•": ",", "|": ",", "{": "(", "}": ")",
        "[": ")", "]": ")", "  ": " ", '?': ',','°': ',',"*!": ","
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    doc = nlp(text)
    return [ent.text.strip(",") for ent in doc.ents if ent.label_ == "PERSON"]

def clean(text):
    return text.strip(" :\t\n")

def extract_emails_helper(text):
    # Handle {name, name}@domain format
    text = re.sub(r"{([^}]+)}\s*@\s*([\w\.-]+\.\w+)", 
                  lambda m: ", ".join([f"{x.strip()}@{m.group(2)}" 
                  for x in m.group(1).split(",")]), 
                  text)
    text = text.replace(" }@", "@").replace("} @", "@")
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(email_pattern, text)))

# ---------------------------------------------------------
# MAIN PARSING LOGIC (UPDATED)
# ---------------------------------------------------------

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

    # --- STATE FLAGS ---
    main_title_found = False
    in_metadata_section = False # Only True BETWEEN Title and Abstract
    in_abstract = False
    
    i = 0
    while i < len(lines):
        tag, content = lines[i]
        text = content.strip()
        txt_lower = text.lower()

        # 1. DETECT MAIN TITLE
        # Once title is found, we enter the Metadata Section
        if tag == "[TITLE]" and not main_title_found:
            result["TITLE"] = clean(text)
            main_title_found = True
            in_metadata_section = True 
            i += 1
            continue
        
        # 2. DETECT ABSTRACT START
        # If we hit Abstract, we must CLOSE the Metadata Section
        is_abstract_start = ("abstract" in txt_lower[:20] or txt_lower.startswith("abstract"))
        
        if is_abstract_start and not in_abstract:
            in_metadata_section = False  # <--- STOP EXTRACTING METADATA
            in_abstract = True
            
            # Remove "Abstract" word
            text = re.sub(r"^abstract[:\s-]*", "", text, flags=re.I).strip()
            if text:
                abstract.append(text)
            i += 1
            continue

        # 3. PROCESS ABSTRACT CONTENT
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
                # We don't increment i here, so next loop processes this title
                continue

            abstract.append(text)
            if text.endswith("."):
                in_abstract = False
            i += 1
            continue

        # 4. PROCESS METADATA SECTION (Between Title and Abstract)
        # This block ONLY executes if we have found the title but NOT YET found the abstract
        elif in_metadata_section:
            
            # A. Extract Emails
            for x in extract_emails_helper(text):
                emails.add(x)

            # B. Extract Authors (Persons)
            potential_authors = extract_authors_heuristic(text)
            for p in potential_authors:
                authors.add(p)

            # C. Extract Affiliations
            # Note: Logic to remove author names from affiliation string
            aff_candidates = is_affiliation_line(text, nlp)
            for x in aff_candidates:
                added = False
                x = x.strip()
                
                # Try to remove author names from the affiliation line
                # to avoid "John Doe University of X" being the affiliation
                for author in authors:
                    if author in x:
                        cleaned = x.replace(author, "").strip(" ,.-\n")
                        if cleaned:
                            affiliations.add(cleaned)
                        added = True
                        break
                
                if not added:
                    affiliations.add(x)
            
            i += 1
            continue

        # 5. PROCESS KEYWORDS (If strictly outside abstract logic)
        # This handles the case where Keywords are their own section not caught by abstract exit
        if "keyword" in txt_lower or "index terms" in txt_lower:
             # Specific logic for keyword tags
            if tag == "[TITLE]":
                # Look ahead for plain text keywords
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
                # Inline keywords
                kw = re.sub(r"(?i)^[^\w]*?(?:keywords?|index\s+terms?)\b[:\s-]*", "", text).strip()
                kw = kw.split(",")
                keywords.extend([clean(k) for k in kw if k.strip()])
                i += 1
                continue

        # Default increment if nothing matched
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
    # Ensure directory structure matches your local environment
    path = os.path.join(os.getcwd(), "./data/content.txt")
    
    # Add a check to create dummy file if testing without file
    if not os.path.exists(path):
        print(f"File not found at {path}")
        return {}

    with open(path, 'r', encoding='utf-8', errors='replace') as file:
        text = file.read()
    
    nlp = spacy.load("en_core_web_md")
    lines = load_tagged_lines(text)
    res = parse_paper(lines, nlp)
    
    import json
    # print(json.dumps(res, indent=4))
    return res

if __name__ == '__main__':
    SummarizeSection()