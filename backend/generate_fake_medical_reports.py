# scripts/generate_fake_medical_reports.py

import os
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path

OUTPUT_DIR = "data/newpdfs"
NUM_PDFS = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)
fake = Faker()

def generate_report(index):
    file_path = os.path.join(OUTPUT_DIR, f"report_{index+1}.pdf")
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    name = fake.name()
    address = fake.address().replace("\n", ", ")
    dob = fake.date_of_birth().strftime("%d-%m-%Y")
    diagnosis = fake.sentence(nb_words=6)
    doctor = fake.name()

    y = height - 100
    line_height = 20

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Patient Name: {name}")
    c.drawString(50, y - line_height, f"Address: {address}")
    c.drawString(50, y - 2*line_height, f"Date of Birth: {dob}")
    c.drawString(50, y - 3*line_height, f"Diagnosis: {diagnosis}")
    c.drawString(50, y - 4*line_height, f"Doctor: {doctor}")
    c.drawString(50, y - 6*line_height, "Prescription: Take medicine 2x daily.")

    c.save()
    print(f"✅ Created: {file_path}")

def main():
    for i in range(NUM_PDFS):
        generate_report(i)

if __name__ == "__main__":
    main()
