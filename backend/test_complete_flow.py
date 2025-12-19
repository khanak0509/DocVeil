#!/usr/bin/env python3
import sys
from pathlib import Path
from encryption import encrypt_file, decrypt_file_to_memory
from pypdf import PdfReader

def test_complete_flow():
    test_pdf = "five_page_detailed_document.pdf"
    encrypted_file = "uploads/test_complete_flow.enc"
    
    if not Path(test_pdf).exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        return False
    
    try:
        encrypt_file(test_pdf, encrypted_file)
        
        if not Path(encrypted_file).exists():
            print("❌ Encrypted file not created")
            return False
        
        plaintext_files = list(Path("uploads").glob("test_complete_flow.pdf"))
        if plaintext_files:
            print(f"❌ Security issue: Found plaintext PDF")
            return False
        
        pdf_bytes = decrypt_file_to_memory(encrypted_file)
        reader = PdfReader(pdf_bytes)
        num_pages = len(reader.pages)
        
        if num_pages != 5:
            print(f"❌ Expected 5 pages, got {num_pages}")
            return False
        
        plaintext_files = list(Path("uploads").glob("*.pdf"))
        old_count = 7
        if len(plaintext_files) > old_count:
            print(f"❌ Security issue: New plaintext PDF created")
            return False
        
        Path(encrypted_file).unlink()
        
        print("✅ Complete flow test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        if Path(encrypted_file).exists():
            Path(encrypted_file).unlink()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
