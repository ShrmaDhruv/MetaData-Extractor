import os
import warnings

warnings.filterwarnings('ignore')

def SummarizeSection():
    INPUT_FILE = "./data/content.txt"
    with open(INPUT_FILE, 'r', encoding='utf-8') as page:
        page.seek(0)
        content_read = page.readlines()
        content_read = [x for x in content_read if x != '\n']

        author = content_read[2].split(',')  # Name of authors list
        if author[0].__contains__('[PLAIN_TEXT]'):
            temp = author[0]
            author[0] = temp[13:]
            # print(author)

        data_dict = {}
        title_count = 0
        current_content_key = None

        for line in content_read:
            line = line.strip()

            
            if line.startswith('[TITLE]'):
                title_count += 1
                title_text = line.replace('[TITLE]', '').strip()
                data_dict[f"TITLE{title_count}"] = title_text
                current_content_key = f"CONTENT{title_count}"
                data_dict[current_content_key] = ""

            
            elif line.startswith('[PLAIN_TEXT]'):
                if current_content_key:
                    text = line.replace('[PLAIN_TEXT]', '').strip()
                    data_dict[current_content_key] += text + " "

            # Untagged ABSTRACT line → treat as a new TITLE
            elif line.upper().startswith('ABSTRACT'):
                title_count += 1
                data_dict[f"TITLE{title_count}"] = "ABSTRACT"
                current_content_key = f"CONTENT{title_count}"
                data_dict[current_content_key] = ""

            # Any other text (continuation of abstract/content)
            else:
                if current_content_key:
                    data_dict[current_content_key] += line + " "

        
        return data_dict



# data = SummarizeSection()

