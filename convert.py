import os
from pdf2docx import Converter

def convert_to_doc(pdf_path):
    doc_path = pdf_path.replace('.pdf', '.doc')
    cv = Converter(pdf_path)
    cv.convert(doc_path, start=0, end=None)
    cv.close()
    return doc_path