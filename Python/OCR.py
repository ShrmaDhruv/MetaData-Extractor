import os
import cv2
import numpy as np
import pytesseract
import warnings
import torch
from pdf2image import convert_from_path
from doclayout_yolo import YOLOv10
import shutil
import re
# from page1 import SummarizeSection

def load_model(device):
    """
    Load the DocLayout YOLO model using a path that is robust to the
    current working directory (important inside Docker).

    Previously we used a plain relative path ("../models/...") which was
    resolved from the process working directory (e.g. `/app` in Docker).
    That pointed to `/models/...`, while the actual weights live in
    `/app/models/...`, so the file could not be found and `/process/`
    returned an error.

    We now build the path relative to this file so it works both locally
    and in the container.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(
        base_dir, "..", "models", "doclayout_yolo_docstructbench_imgsz1280_2501.pt"
    )
    model_path = os.path.abspath(model_path)

    if not os.path.exists(model_path):
        # Make the failure explicit so the API returns a clear message
        raise FileNotFoundError(f"Model weights not found at: {model_path}")

    return YOLOv10(model_path).to(device)

# OCR helper

def run_zoom_ocr(frame, coords,lbl=""):
    x1, y1, x2, y2 = coords
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return ""
    zoom = cv2.resize(roi, (roi.shape[1]*2, roi.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    raw_text = pytesseract.image_to_string(zoom, lang="eng")
    text = raw_text.strip()
    if lbl in ["section_header", "heading", "subtitle","title"]:
        text = text.replace("\n", " ")
        text = text.replace("- ", "")
    return text

def save_region_image(frame, coords, label, index, out_dir="./data/extracted_figures"):
    os.makedirs(out_dir, exist_ok=True)
    x1, y1, x2, y2 = coords
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return None
    filename = f"{out_dir}/{label}_{index}.png"
    cv2.imwrite(filename, roi)
    return filename

def process_page(frame, page_num,model):
    folder_path = "./data/extracted_figures"
    os.makedirs(folder_path, exist_ok=True)

    results = model.predict(frame)
    boxes = results[0].boxes
    classes = results[0].names
    # Collect detections
    detections = []
    for box in boxes:
        cls_id = int(box.cls.cpu().numpy())
        label = classes[cls_id].lower().replace(" ", "_")
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        detections.append({"label": label, "coords": (x1, y1, x2, y2)})
    # Sort by vertical position
    detections = sorted(detections, key=lambda d: d["coords"][1])
    printed_items = []
    printed_captions = set()
    prev_lbl = ""

    # Same text formating
    def normalize_text(text):
        return re.sub(r"\s+", " ", text.strip()).lower()
    # Unwanted Hyphen fix
    def fix_hyphenation(text):
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
        text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
        return text

    def clean_text(text):
        text = fix_hyphenation(text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    # Duplicate Text
    def is_duplicate(new_text, new_coords, printed_items, iou_threshold=0.5):
        norm_text = normalize_text(new_text)
        x1, y1, x2, y2 = new_coords

        for old_text, old_coords in printed_items:
            ox1, oy1, ox2, oy2 = old_coords
            if norm_text == old_text:
                return True
            inter_x1, inter_y1 = max(x1, ox1), max(y1, oy1)
            inter_x2, inter_y2 = min(x2, ox2), min(y2, oy2)
            inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
            if inter_area == 0:
                continue

            new_area = (x2 - x1) * (y2 - y1)
            old_area = (ox2 - ox1) * (oy2 - oy1)
            union_area = new_area + old_area - inter_area

            if union_area > 0 and inter_area / union_area > iou_threshold:
                return True
        return False

    # Write text
    with open("./data/content.txt","a", encoding="utf-8") as file:
        file.write(f"\n---------PAGE {page_num}--------\n\n")

        for idx, det in enumerate(detections):
            lbl = det["label"]
            coords = det["coords"]

            text = run_zoom_ocr(frame, coords, lbl)
            text = clean_text(text)

            if not text and lbl not in ["figure", "image", "table"]:  # Not Recongnized values
                continue

            if text and is_duplicate(text, coords, printed_items): #Duplicate glitch
                continue

            if text:
                printed_items.append((normalize_text(text), coords))
            if lbl == "title":
                file.write(f"\n[{lbl.upper()}] {text}\n\n")
                prev_lbl = lbl

            elif lbl in ["section_header", "heading", "subtitle"]:
                file.write(f"\n[{lbl.upper()}] {text}\n\n")
                prev_lbl = lbl

            elif lbl in ["plain_text", "paragraph", "text"]:
                if prev_lbl == lbl:
                    file.write(f"{text}\n")
                else:
                    file.write(f"\n[{lbl.upper()}] {text}\n")
                    prev_lbl = lbl
            elif lbl in ["figure", "image", "table"] or ('formula' in lbl and 'formula_caption' not in lbl):
                img_path = save_region_image(frame, coords, lbl, idx)
                if img_path:
                    nearest_caption = None
                    min_dist = float("inf")

                    for cap_det in detections:
                        if "caption" in cap_det["label"]:
                            cy1 = cap_det["coords"][1]
                            fy2 = coords[3]
                            dist = abs(cy1 - fy2)
                            if dist < min_dist:
                                min_dist = dist
                                nearest_caption = cap_det

                    caption_text = ""
                    if nearest_caption:
                        caption_text = clean_text(run_zoom_ocr(frame, nearest_caption["coords"], lbl))

                    if caption_text and caption_text not in printed_captions:
                        file.write(f"\n[IMAGE CAPTION] {caption_text}\n\n")
                        printed_captions.add(caption_text)
                        file.write(f"\n[IMAGE] {img_path}\n\n")
                    else:
                        file.write(f"\n[IMAGE] {img_path}\n\n")

    print(f" Page {page_num} processed and saved to content.txt")

# Main Function
def output(filename : str):
    
    warnings.filterwarnings('ignore')

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_model(device)

    # Remove old Images

    folder_path = "./data/extracted_figures"
    if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    # Removing Old Text content
    
    content_path="./data/content.txt"
    if os.path.exists(content_path):
        os.remove(content_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "..", "uploads", filename)
    pdf_path = os.path.abspath(pdf_path)
    pages = convert_from_path(pdf_path, dpi=200)


    for page_num, page in enumerate(pages, 1):
        if page_num == 1:
            frame = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
            process_page(frame, page_num,model)
        else:
            break

