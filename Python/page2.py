import warnings
import re

warnings.filterwarnings("ignore")


def SummarizeSection():
    INPUT_FILE = "./data/content.txt"

    with open(INPUT_FILE, 'r', encoding='utf-8') as page:
        content = [line.rstrip("\n") for line in page if line.strip()]

    data_dict = {}
    title_count = 0
    current_content_key = None

    # For collecting content lines before finalizing
    content_lines = []

    # AUTHOR section handling
    reading_authors = False
    author_extracted = False
    author_block = ""

    for raw_line in content:
        line = raw_line.strip()

        # -----------------------------------------------------
        # AUTHOR BLOCK START (first PLAIN_TEXT after TITLE1)
        # -----------------------------------------------------
        if not author_extracted and line.startswith("[PLAIN_TEXT]") and title_count == 1:
            reading_authors = True
            author_block += line.replace("[PLAIN_TEXT]", "").strip() + " "
            continue

        # -----------------------------------------------------
        # CAPTURE MULTI-LINE AUTHORS UNTIL TITLE or ABSTRACT
        # -----------------------------------------------------
        if reading_authors:
            if line.startswith("[TITLE]") or line.upper().startswith("ABSTRACT"):
                reading_authors = False
                author_extracted = True

                authors, emails = process_author_block(author_block)

                data_dict["AUTHOR"] = authors
                if emails:
                    data_dict["EMAIL"] = emails

                # Continue processing this TITLE/ABSTRACT normally
            else:
                author_block += " " + line
                continue

        # -----------------------------------------------------
        # TITLE (tagged)
        # -----------------------------------------------------
        if line.startswith("[TITLE]"):

            # finalize previous content block
            if current_content_key:
                finalize_content_block(data_dict, current_content_key, content_lines)
                content_lines = []

            title_count += 1
            title_text = line.replace("[TITLE]", "").strip()

            data_dict[f"TITLE{title_count}"] = title_text

            current_content_key = f"CONTENT{title_count}"
            data_dict[current_content_key] = ""  # placeholder
            continue

        # -----------------------------------------------------
        # ABSTRACT (untagged)
        # -----------------------------------------------------
        if line.upper().startswith("ABSTRACT"):

            # finalize previous content block
            if current_content_key:
                finalize_content_block(data_dict, current_content_key, content_lines)
                content_lines = []

            title_count += 1
            data_dict[f"TITLE{title_count}"] = "ABSTRACT"

            current_content_key = f"CONTENT{title_count}"
            data_dict[current_content_key] = ""

            # Case: ABSTRACT has text in same line
            after = line[len("ABSTRACT"):].strip()
            if after:
                content_lines.append(after)
            continue

        # -----------------------------------------------------
        # CONTENT (tagged)
        # -----------------------------------------------------
        if line.startswith("[PLAIN_TEXT]"):
            text = line.replace("[PLAIN_TEXT]", "").strip()
            if current_content_key:
                content_lines.append(text)
            continue

        # -----------------------------------------------------
        # GENERAL CONTENT LINE
        # -----------------------------------------------------
        if current_content_key:
            content_lines.append(line)
            continue

    # -----------------------------------------------------
    # FINAL BLOCK (after loop ends)
    # -----------------------------------------------------
    if current_content_key and content_lines:
        finalize_content_block(data_dict, current_content_key, content_lines)

    return data_dict


# ============================================================
# FINALIZE CONTENT BLOCK (remove last line if no ".")
# ============================================================
def finalize_content_block(data_dict, key, lines):
    """
    Saves content into data_dict[key],
    removing the last line if it does not end with a real '.'.
    """

    def ends_with_period(line):
        line = line.rstrip()  # remove spaces, tabs, unicode spaces
        return line.endswith('.') or line.endswith('."')

    # Remove last line if incomplete
    while lines and not ends_with_period(lines[-1]):
        lines.pop()

    data_dict[key] = " ".join(lines).strip()


# ============================================================
# AUTHOR BLOCK PROCESSING
# ============================================================

def process_author_block(text):
    text = text.strip()

    # Extract emails
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    for e in emails:
        text = text.replace(e, "")

    # 1. Extract Author Names Using Patterns
    name_pattern = r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b"
    found_names = re.findall(name_pattern, text)

    # Remove duplicates while preserving order
    unique_names = list(dict.fromkeys(found_names))

    # 2. Remove names from text, leaving affiliations
    affiliations_text = text
    for n in unique_names:
        affiliations_text = affiliations_text.replace(n, "")

    # 3. Clean affiliations
    affiliations_text = affiliations_text.replace("*", "").replace("†", "").replace("+", "").strip()

    affiliations = re.split(r"\s{2,}|[*+]+|«|\+|—|-", affiliations_text)
    affiliations = [a.strip() for a in affiliations if len(a.strip()) > 8]

    # Combine authors + affiliations
    authors_combined = unique_names + affiliations

    return authors_combined, emails


# ============================================================

# if __name__ == "__main__":
#     data = SummarizeSection()
#     print(data)
