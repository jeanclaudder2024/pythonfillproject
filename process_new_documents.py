#!/usr/bin/env python3
"""
Process the 3 new Word documents with random placeholder data
"""

import os
from document_processor import DocumentProcessor

def process_new_documents():
    """Process the 3 new documents with random placeholder data"""
    
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Define the 3 new documents
    new_documents = [
        "307cc290-4228-4de4-9cef-2e4dee909f6e_Commercial_Invoice_Batys_Final_with_Tag_2.docx",
        "b1554d71-37a0-4e1e-9eab-8311462eaae7_PERFORMA_INVOICE_WITH_TAGS_3.docx", 
        "e1f18464-44f8-4933-b8f6-f7b0b6c0c9b9_ICPO_TEMPLATE_WITH_TAG_DATA_1.docx"
    ]
    
    uploads_dir = "uploads"
    outputs_dir = "outputs"
    
    # Ensure outputs directory exists
    os.makedirs(outputs_dir, exist_ok=True)
    
    print("🚀 Processing 3 new Word documents with random placeholder data...")
    print("=" * 70)
    
    for i, doc_name in enumerate(new_documents, 1):
        print(f"\n📄 Processing Document {i}/3: {doc_name}")
        print("-" * 50)
        
        # Extract the UUID from the filename
        uuid = doc_name.split('_')[0]
        
        input_path = os.path.join(uploads_dir, doc_name)
        output_word_path = os.path.join(outputs_dir, f"{uuid}_filled.docx")
        output_pdf_path = os.path.join(outputs_dir, f"{uuid}_filled.pdf")
        
        if not os.path.exists(input_path):
            print(f"❌ Error: File not found: {input_path}")
            continue
            
        try:
            # Process the document with random data (vessel_imo=None for random data)
            word_output, pdf_output = processor.process_document(input_path, vessel_imo=None, file_id=uuid)
            
            if os.path.exists(word_output):
                print(f"✅ Word document processed successfully!")
                print(f"   📁 Output: {word_output}")
                
                if os.path.exists(pdf_output):
                    print(f"✅ PDF conversion successful!")
                    print(f"   📁 PDF Output: {pdf_output}")
                else:
                    # Check for fallback file
                    fallback_file = pdf_output.replace('.pdf', '_fallback.txt')
                    if os.path.exists(fallback_file):
                        print(f"⚠️  PDF conversion failed - fallback file created: {fallback_file}")
                    else:
                        print(f"⚠️  PDF conversion failed - no fallback file found")
                    
            else:
                print(f"❌ Error: Word document was not created")
                
        except Exception as e:
            print(f"❌ Error processing {doc_name}: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 Processing complete! Check the outputs folder for your filled documents.")

if __name__ == "__main__":
    process_new_documents()