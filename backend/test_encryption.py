import sys
from pathlib import Path
from encryption import encrypt_file, decrypt_file_to_memory, is_encrypted_file

def test_encryption():
    test_pdf = "five_page_detailed_document.pdf"
    encrypted_output = "test_encrypted.enc"
    
    if not Path(test_pdf).exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        return False
    
    encrypt_file(test_pdf, encrypted_output)
    
    if not Path(encrypted_output).exists():
        print("❌ Encrypted file was not created")
        return False
    
    if not is_encrypted_file(encrypted_output):
        print("❌ File not detected as encrypted")
        return False
    
    decrypted_bytes = decrypt_file_to_memory(encrypted_output)
    
    original_size = Path(test_pdf).stat().st_size
    decrypted_size = len(decrypted_bytes.getvalue())
    
    if original_size != decrypted_size:
        print(f"⚠️ Size mismatch - Original: {original_size} bytes, Decrypted: {decrypted_size} bytes")
        return False
    
    Path(encrypted_output).unlink()
    
    print("✅ All encryption tests passed")
    return True

if __name__ == "__main__":
    success = test_encryption()
    sys.exit(0 if success else 1)
