# scripts/pdf_to_images.py

import os
from pdf2image import convert_from_path


PDF_DIR = "data/newpdfs"
OUTPUT_DIR = "data/newimages"
DPI = 300

def convert_pdf_to_images(pdf_path, output_dir, dpi=300):
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    print(f"Processing: {filename}")
    
    images = convert_from_path(pdf_path, dpi=dpi)
    
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"{filename}_page{i}.png")
        image.save(image_path, "PNG")
        print(f"Saved: {image_path}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for file in os.listdir(PDF_DIR):
        if file.lower().endswith(".pdf"):
            convert_pdf_to_images(os.path.join(PDF_DIR, file), OUTPUT_DIR, DPI)

if __name__ == "__main__":
    main()
