from ultralytics import YOLO
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import numpy as np

MODEL_PATH = "data/dataset/runs/detect/train/weights/best.pt"

def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)

def detect_sensitive_areas(image, model, conf_threshold=0.05):
    results = model.predict(np.array(image), conf=conf_threshold)
    boxes = []
    for box in results[0].boxes:
        xyxy = box.xyxy.cpu().numpy()[0]
        conf = float(box.conf.cpu().numpy()[0])
        cls_id = int(box.cls.cpu().numpy()[0])
        if conf >= conf_threshold:
            boxes.append(xyxy)
    return boxes

def redact_image(image, boxes):
    draw = ImageDraw.Draw(image)
    for box in boxes:
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], fill="black")
    return image

def images_to_pdf(images, output_pdf_path):
    images[0].save(output_pdf_path, save_all=True, append_images=images[1:])

def redact_pdf(input_pdf_path, output_pdf_path):
    model = YOLO(MODEL_PATH)
    pages = pdf_to_images(input_pdf_path)
    redacted_pages = []
    for page in pages:
        boxes = detect_sensitive_areas(page, model)
        redacted_page = redact_image(page, boxes)
        redacted_pages.append(redacted_page)
    images_to_pdf(redacted_pages, output_pdf_path)
    print(f"Redacted PDF saved to: {output_pdf_path}")

if __name__ == "__main__":
    input_pdf = "data/test1.pdf"
    output_pdf = "data/output_pdfs/redacted_output1.pdf"
    redact_pdf(input_pdf, output_pdf)
