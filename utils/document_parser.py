import io
import pdfplumber
import docx
from core.logger import get_logger

logger = get_logger(__name__)

def _get_file_stream(file_input):
    """Helper to handle file paths, byte streams, and file-like objects seamlessly."""
    if isinstance(file_input, bytes):
        return io.BytesIO(file_input)
    elif hasattr(file_input, "read"):
        # For Streamlit UploadedFile objects, ensure we read from the start
        file_input.seek(0)
        return file_input
    # Assume it's a string path
    return file_input

def extract_text_from_pdf(file_input) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    Supports file paths, bytes, or file-like objects (e.g. Streamlit uploads).
    Provides malformed file protection and UTF-8 safe output.
    """
    try:
        text_content = []
        stream = _get_file_stream(file_input)
        
        with pdfplumber.open(stream) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                else:
                    logger.debug(f"No text found on page {i} of PDF.")
                    
        final_text = "\n".join(text_content).strip()
        
        # Ensure UTF-8 safety
        return final_text.encode('utf-8', 'ignore').decode('utf-8')
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF. Error: {str(e)}")
        return ""

def extract_text_from_docx(file_input) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    Supports file paths, bytes, or file-like objects.
    Provides malformed file protection and UTF-8 safe output.
    """
    try:
        stream = _get_file_stream(file_input)
        doc = docx.Document(stream)
            
        # Only extract paragraphs that actually contain text
        text_content = [para.text for para in doc.paragraphs if para.text.strip()]
        final_text = "\n".join(text_content).strip()
        
        # Ensure UTF-8 safety
        return final_text.encode('utf-8', 'ignore').decode('utf-8')
        
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX. Error: {str(e)}")
        return ""
