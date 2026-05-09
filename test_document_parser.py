import os
from utils.document_parser import extract_text_from_pdf, extract_text_from_docx

def test_document_parser():
    print("="*50)
    print("DOCUMENT PARSER UTILITY - TEST MODULE")
    print("="*50)
    
    print("\n[+] Testing environment and imports...")
    try:
        import pdfplumber
        import docx
        print("✅ pdfplumber and python-docx imported successfully.")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure you ran: pip install -r requirements.txt")
        return

    print("\n[+] How to use the parser:")
    print("To parse a PDF:")
    print("   text = extract_text_from_pdf('path/to/resume.pdf')")
    print("   # Or pass the uploaded file object from Streamlit directly!")
    
    print("\nTo parse a DOCX:")
    print("   text = extract_text_from_docx('path/to/resume.docx')")
    
    print("\n[+] Features included:")
    print("  ✔️ UTF-8 safe decoding")
    print("  ✔️ Catches malformed PDFs (returns empty string cleanly without crashing)")
    print("  ✔️ Automatic handling of file bytes vs file paths")
    
if __name__ == "__main__":
    test_document_parser()
