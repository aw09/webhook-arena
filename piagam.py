from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx2pdf import convert

# Define the path to the Word document and PDF output
doc_path = "/home/agung/Desktop/piagam.docx"
edited_doc_path = "/home/agung/Desktop/piagam_edited.docx"
pdf_path = "/home/agung/Desktop/piagam.pdf"

# Function to replace text in the entire document's XML
def replace_text_in_xml(doc, search_text, replace_text):
    for element in doc.element.body:
        replace_text_in_element(element, search_text, replace_text)

# Recursive function to replace text in XML elements
def replace_text_in_element(element, search_text, replace_text):
    for sub_element in element:
        if sub_element.text:
            sub_element.text = sub_element.text.replace(search_text, replace_text)
        replace_text_in_element(sub_element, search_text, replace_text)

# Load the Word document
doc = Document(doc_path)

# Replace text in XML
replace_text_in_xml(doc, 'TES_NAMA', 'Actual Name')

# Save the edited document
doc.save(edited_doc_path)

convert(edited_doc_path, pdf_path)