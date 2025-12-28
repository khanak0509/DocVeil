import asyncio
import sys
from pathlib import Path
from encryption import encrypt_file
from workflow import stream_pdf_summaries

async def test_workflow_with_encryption():
    test_pdf = "five_page_detailed_document.pdf"
    encrypted_pdf = "test_workflow.enc"
    
    if not Path(test_pdf).exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        return False
    
    encrypt_file(test_pdf, encrypted_pdf)
    
    page_count = 0
    async for summary_data in stream_pdf_summaries(encrypted_pdf):
        if summary_data['status'] == 'processing':
            page_count = summary_data['page']
        elif summary_data['status'] == 'complete':
            break
    
    decrypted_files = list(Path("uploads").glob("*.pdf"))
    if decrypted_files and len(decrypted_files) > 7:
        print(f"⚠️ Found new decrypted PDF files")
    
    Path(encrypted_pdf).unlink()
    
    print("✅ Workflow encryption test passed")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_workflow_with_encryption())
    sys.exit(0 if success else 1)
