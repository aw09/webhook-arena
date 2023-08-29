from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import os
import pandas as pd
from PyPDF2 import PdfMerger

DOC_PATH = "/home/agung/Desktop/piagam.docx"
temp_dir = "/home/agung/Desktop/temp/"
os.makedirs(temp_dir, exist_ok=True)

# Convert DOCX to PDF using reportlab
def convert_docx_to_pdf(input_path, output_path):
    command = f"libreoffice --headless --convert-to pdf --outdir {os.path.dirname(output_path)} {input_path}"
    os.system(command)

# Function to replace text in the entire document's XML
def replace_text_in_xml(doc, replacements):
    for element in doc.element.body:
        replace_text_in_element(element, replacements)

# Recursive function to replace text in XML elements
def replace_text_in_element(element, replacements):
    for sub_element in element:
        if sub_element.text:
            for search_text, replace_text in replacements.items():
                sub_element.text = sub_element.text.replace(search_text, replace_text)
        replace_text_in_element(sub_element, replacements)

# Create a PDF merger object
pdf_merger = PdfMerger()

# Read the CSV file into a DataFrame
df = pd.read_csv("data.csv")

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    replacements = {
        'TES_NAMA': row['Name'],
        'TES_SEKOLAH': row['School'],
        'TES_SEBAGAI': row['Role']
    }

    doc = Document(DOC_PATH)

    # Perform text replacements
    replace_text_in_xml(doc, replacements)
    

    edited_doc_path = os.path.join(temp_dir, f"temp_{index}.docx")
    doc.save(edited_doc_path)

    pdf_path = os.path.join(temp_dir, f"temp_{index}.pdf")
    convert_docx_to_pdf(edited_doc_path, pdf_path)

    pdf_merger.append(pdf_path)

pdf_merger.write("merged.pdf")
pdf_merger.close()
