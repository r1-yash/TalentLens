import io
import docx
from utils.document_parser import extract_text_from_pdf, extract_text_from_docx

def test_document_parser():
    print("="*40)
    print("TEST: DOCUMENT PARSER (PDF & DOCX)")
    print("="*40)
    
    # 1. Invalid PDF path
    print("[+] Testing invalid file path...")
    text = extract_text_from_pdf("invalid_path_to_nothing.pdf")
    assert text == "", "Should return empty string on failure"
    print("    ✅ Malformed/Missing PDF handled gracefully.")
    
    # 2. DOCX creation & extraction
    print("\n[+] Testing DOCX parsing and UTF-8 safety...")
    doc = docx.Document()
    doc.add_paragraph("Hello UTF-8: Résumé & Café")
    byte_io = io.BytesIO()
    doc.save(byte_io)
    byte_io.seek(0)
    
    text = extract_text_from_docx(byte_io.read())
    assert "Résumé & Café" in text, "UTF-8 parsing failed for DOCX"
    print("    ✅ DOCX bytes parsed successfully.")
    
    # 3. Malformed PDF bytes
    print("\n[+] Testing malformed PDF handling...")
    malformed_pdf = b"This is not a real PDF file format"
    text = extract_text_from_pdf(malformed_pdf)
    assert text == "", "Malformed PDF bytes should return empty string"
    print("    ✅ Malformed PDF bytes handled safely without crashing.")

    print("\n✅ Document Parser validation complete.")

if __name__ == "__main__":
    test_document_parser()
