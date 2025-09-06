from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf(file_object):
    """
    Extracts text from a PDF file uploaded via Streamlit.

    Args:
        file_object (BytesIO): The file object from st.file_uploader.

    Returns:
        str: The extracted text content from the PDF.
    """
    try:
        # The file_object is a BytesIO stream. PyPDF2 can read this directly.
        pdf_reader = PdfReader(file_object)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF file: {e}"