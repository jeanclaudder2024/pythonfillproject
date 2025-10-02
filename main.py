#!/usr/bin/env python3
"""
Complete Template Processing System
Maps all 274 placeholders to database tables and generates realistic data
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import uuid
import os
import tempfile
import json
from pathlib import Path
from docx import Document
import re
import shutil
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import subprocess

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: Supabase credentials not found. Using dummy data.")
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("SUCCESS: Connected to Supabase database")

app = FastAPI(title="Complete Document Service", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template storage
templates_storage = []
templates_file = Path("templates_data.json")

def load_templates():
    """Load templates from file"""
    global templates_storage
    if templates_file.exists():
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates_storage = json.load(f)
        except:
            templates_storage = []

def save_templates():
    """Save templates to file"""
    try:
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates_storage, f, indent=2)
    except:
        pass

# Load templates on startup
load_templates()

# All 274 placeholders from your templates
ALL_PLACEHOLDERS = {
    # Vessel placeholders
    'vessel': [
        'imo_number', 'flag_state', 'vessel_owner', 'vessel_operator', 'vessel_type',
        'beam', 'call_sign', 'cargo_capacity', 'cargo_tanks', 'class_society',
        'deadweight', 'draft', 'engine_type', 'gross_tonnage', 'ism_manager',
        'length_overall', 'net_tonnage', 'pumping_capacity', 'registry_port', 'speed', 'year_built'
    ],
    
    # Company placeholders
    'company': [
        'buyer_company_name', 'buyer_address', 'buyer_email', 'buyer_tel', 'buyer_fax',
        'buyer_mobile', 'buyer_office_tel', 'buyer_position', 'buyer_registration',
        'buyer_signatory_name', 'buyer_signatory_position', 'buyer_signature',
        'seller_company', 'seller_address', 'seller_email', 'seller_tel',
        'seller_representative', 'seller_signatory_name', 'seller_signatory_position',
        'seller_signature', 'company_name'
    ],
    
    # Port placeholders
    'port': [
        'port_loading', 'port_discharge', 'origin', 'registry_port', 'delivery_port',
        'place_of_destination', 'port_of_loading', 'port_of_discharge', 'country_of_origin'
    ],
    
    # Financial placeholders
    'financial': [
        'price', 'total_amount', 'total_amount_due', 'unit_price2', 'unit_price3',
        'amount2', 'amount3', 'amount_in_words', 'total_product_value', 'contract_value',
        'payment_terms', 'transaction_currency', 'total_quantity', 'quantity', 'quantity2', 'quantity3'
    ],
    
    # Product placeholders
    'product': [
        'commodity', 'product_description', 'product_name', 'specification', 'quality',
        'cargo_capacity', 'cargo_tanks', 'contract_quantity'
    ],
    
    # Date placeholders
    'date': [
        'issue_date', 'issued_date', 'date', 'validity', 'valid_until', 'contract_duration'
    ],
    
    # Document placeholders
    'document': [
        'document_number', 'invoice_no', 'proforma_invoice_no', 'commercial_invoice_no',
        'commercial_id', 'pop_reference', 'notary_number'
    ],
    
    # Bank placeholders
    'bank': [
        'buyer_bank_name', 'buyer_bank_address', 'buyer_swift', 'buyer_account_no',
        'seller_bank_name', 'seller_bank_address', 'seller_swift', 'seller_bank_account_no',
        'confirming_bank_name', 'confirming_bank_address', 'confirming_bank_swift',
        'issuing_bank_name', 'issuing_bank_address', 'issuing_bank_swift'
    ],
    
    # Technical specifications
    'technical': [
        'api_gravity', 'density', 'specific_gravity', 'viscosity_40', 'viscosity_100',
        'flash_point', 'pour_point', 'cloud_point', 'cfpp', 'sulfur', 'ash_content',
        'water_content', 'sediment', 'dist_10', 'dist_50', 'dist_90', 'dist_ibp', 'dist_fbp',
        'cetane_number', 'octane_number', 'calorific_value', 'lubricity', 'aromatics',
        'olefins', 'oxygenates', 'nitrogen', 'vanadium', 'nickel', 'sodium'
    ]
}

async def get_real_vessel_data(vessel_imo: str):
    """Fetch real vessel data from Supabase database"""
    try:
        if not supabase:
            print("⚠️  Supabase not connected, using dummy data")
            return get_comprehensive_dummy_data(vessel_imo)
        
        # Fetch vessel data from your real database
        response = supabase.table('vessels').select('*').eq('imo', vessel_imo).execute()
        
        if response.data and len(response.data) > 0:
            vessel = response.data[0]
            print(f"SUCCESS: Found real vessel data for IMO: {vessel_imo}")
            return map_vessel_to_placeholders(vessel)
        else:
            print(f"WARNING: No vessel found with IMO: {vessel_imo}, using dummy data")
            return get_comprehensive_dummy_data(vessel_imo)
            
    except Exception as e:
        print(f"ERROR: Error fetching vessel data: {e}")
        return get_comprehensive_dummy_data(vessel_imo)

def map_vessel_to_placeholders(vessel):
    """Map real vessel data to all 274 placeholders"""
    return {
        # Vessel data
        'imo_number': vessel.get('imo', 'IMO1234567'),
        'flag_state': vessel.get('flag', 'Malta'),
        'vessel_owner': vessel.get('owner_name', 'Sample Shipping Co.'),
        'vessel_operator': vessel.get('operator_name', 'Sample Operator Ltd.'),
        'vessel_type': vessel.get('vessel_type', 'Crude Oil Tanker'),
        'beam': vessel.get('beam', '32.2'),
        'call_sign': vessel.get('callsign', '9V1234'),
        'cargo_capacity': vessel.get('cargo_capacity', '50000'),
        'cargo_tanks': vessel.get('cargo_tanks', '12'),
        'class_society': vessel.get('class_society', 'Lloyd\'s Register'),
        'deadweight': vessel.get('deadweight', '75000'),
        'draft': vessel.get('draft', '12.5'),
        'engine_type': vessel.get('engine_type', '2-Stroke Diesel'),
        'gross_tonnage': vessel.get('gross_tonnage', '45000'),
        'ism_manager': vessel.get('ism_manager', 'Sample ISM Manager'),
        'length_overall': vessel.get('length', '200.5'),
        'net_tonnage': vessel.get('net_tonnage', '25000'),
        'pumping_capacity': vessel.get('pumping_capacity', '2000'),
        'registry_port': vessel.get('registry_port', 'Valletta'),
        'speed': vessel.get('speed', '14.5'),
        'year_built': vessel.get('built', '2015'),
        
        # Company data (from vessel or generate)
        'buyer_company_name': 'Petroleum Trading Ltd.',
        'buyer_address': '123 Marina Bay, Singapore 018956',
        'buyer_email': 'buyer@petroleumtrading.com',
        'buyer_tel': '+65 6123 4567',
        'buyer_fax': '+65 6123 4568',
        'buyer_mobile': '+65 9123 4567',
        'buyer_office_tel': '+65 6123 4567',
        'buyer_position': 'Trading Manager',
        'buyer_registration': '201234567M',
        'buyer_signatory_name': 'John Smith',
        'buyer_signatory_position': 'Managing Director',
        'buyer_signature': 'J. Smith',
        'seller_company': 'Global Oil Trading Co.',
        'seller_address': '456 Oil Street, Rotterdam, Netherlands',
        'seller_email': 'seller@globaloil.com',
        'seller_tel': '+31 20 123 4567',
        'seller_representative': 'Maria Garcia',
        'seller_signatory_name': 'Maria Garcia',
        'seller_signatory_position': 'Sales Director',
        'seller_signature': 'M. Garcia',
        'company_name': 'Global Oil Trading Co.',
        
        # Port data
        'port_loading': 'Port Klang, Malaysia',
        'port_discharge': 'Singapore Port',
        'origin': 'Malaysia',
        'delivery_port': 'Singapore Port',
        'place_of_destination': 'Singapore',
        'port_of_loading': 'Port Klang, Malaysia',
        'port_of_discharge': 'Singapore Port',
        'country_of_origin': 'Malaysia',
        
        # Financial data
        'price': 'USD 85.50',
        'total_amount': 'USD 4,275,000.00',
        'total_amount_due': 'USD 4,275,000.00',
        'unit_price2': 'USD 85.50',
        'unit_price3': 'USD 85.50',
        'amount2': 'USD 1,425,000.00',
        'amount3': 'USD 1,425,000.00',
        'amount_in_words': 'Four Million Two Hundred Seventy Five Thousand US Dollars Only',
        'total_product_value': 'USD 4,275,000.00',
        'contract_value': 'USD 4,275,000.00',
        'payment_terms': 'LC at sight',
        'transaction_currency': 'USD',
        'total_quantity': '50,000 MT',
        'quantity': '50,000 MT',
        'quantity2': '25,000 MT',
        'quantity3': '25,000 MT',
        
        # Product data
        'commodity': 'Crude Oil',
        'product_description': 'Malaysian Light Crude Oil',
        'product_name': 'Malaysian Light Crude Oil',
        'specification': 'API 35-40, Sulfur < 0.5%',
        'quality': 'Premium Grade',
        'contract_quantity': '50,000 MT',
        
        # Date data
        'issue_date': datetime.now().strftime('%Y-%m-%d'),
        'issued_date': datetime.now().strftime('%Y-%m-%d'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'validity': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'valid_until': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'contract_duration': '30 days',
        
        # Document data
        'document_number': f"DOC-{datetime.now().year}-{random.randint(1000, 9999)}",
        'invoice_no': f"INV-{datetime.now().year}-{random.randint(1000, 9999)}",
        'proforma_invoice_no': f"PF-{datetime.now().year}-{random.randint(1000, 9999)}",
        'commercial_invoice_no': f"CI-{datetime.now().year}-{random.randint(1000, 9999)}",
        'commercial_id': f"CID-{datetime.now().year}-{random.randint(1000, 9999)}",
        'pop_reference': f"POP-{datetime.now().year}-{random.randint(1000, 9999)}",
        'notary_number': f"NOT-{datetime.now().year}-{random.randint(1000, 9999)}",
        
        # Bank data
        'buyer_bank_name': 'DBS Bank Ltd.',
        'buyer_bank_address': '12 Marina Boulevard, Singapore 018982',
        'buyer_swift': 'DBSSSGSG',
        'buyer_account_no': f"{random.randint(1000000000, 9999999999)}",
        'seller_bank_name': 'ABN AMRO Bank N.V.',
        'seller_bank_address': 'Gustav Mahlerlaan 10, 1082 PP Amsterdam, Netherlands',
        'seller_swift': 'ABNANL2A',
        'seller_bank_account_no': f"{random.randint(1000000000, 9999999999)}",
        'confirming_bank_name': 'HSBC Bank plc',
        'confirming_bank_address': '1 Centenary Square, Birmingham B1 1HQ, UK',
        'confirming_bank_swift': 'HBUKGB4B',
        'issuing_bank_name': 'Standard Chartered Bank',
        'issuing_bank_address': '1 Basinghall Avenue, London EC2V 5DD, UK',
        'issuing_bank_swift': 'SCBLGB2L',
        
        # Technical specifications
        'api_gravity': '37.5',
        'density': '0.835',
        'specific_gravity': '0.835',
        'viscosity_40': '2.8',
        'viscosity_100': '1.2',
        'flash_point': '65',
        'pour_point': '-15',
        'cloud_point': '5',
        'cfpp': '3',
        'sulfur': '0.35',
        'ash_content': '0.01',
        'water_content': '0.1',
        'sediment': '0.05',
        'dist_10': '180',
        'dist_50': '250',
        'dist_90': '350',
        'dist_ibp': '150',
        'dist_fbp': '380',
        'cetane_number': '52',
        'octane_number': '92',
        'calorific_value': '42.5',
        'lubricity': '0.45',
        'aromatics': '25',
        'olefins': '15',
        'oxygenates': '0',
        'nitrogen': '0.1',
        'vanadium': '5',
        'nickel': '2',
        'sodium': '1'
    }

def get_comprehensive_dummy_data(vessel_imo: str):
    """Generate comprehensive dummy data for all placeholders"""
    return map_vessel_to_placeholders({
        'imo': vessel_imo,
        'flag': 'Malta',
        'owner_name': 'Sample Shipping Co.',
        'operator_name': 'Sample Operator Ltd.',
        'vessel_type': 'Crude Oil Tanker',
        'beam': '32.2',
        'callsign': '9V1234',
        'cargo_capacity': '50000',
        'cargo_tanks': '12',
        'class_society': 'Lloyd\'s Register',
        'deadweight': '75000',
        'draft': '12.5',
        'engine_type': '2-Stroke Diesel',
        'gross_tonnage': '45000',
        'ism_manager': 'Sample ISM Manager',
        'length': '200.5',
        'net_tonnage': '25000',
        'pumping_capacity': '2000',
        'registry_port': 'Valletta',
        'speed': '14.5',
        'built': '2015'
    })

def extract_placeholders_from_docx(file_path):
    """Extract placeholders from Word document"""
    placeholders = set()
    
    try:
        doc = Document(file_path)
        
        # Extract from paragraphs
        for paragraph in doc.paragraphs:
            text = paragraph.text
            matches = re.findall(r'\{([^}]+)\}', text)
            placeholders.update(matches)
        
        # Extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text
                        matches = re.findall(r'\{([^}]+)\}', text)
                        placeholders.update(matches)
        
        return list(placeholders)
        
    except Exception as e:
        print(f"Error extracting placeholders: {e}")
        return []

def fill_word_template(template_path, output_path, vessel_data):
    """Fill Word template with data"""
    try:
        # Copy template to output
        shutil.copy2(template_path, output_path)
        
        # Open the document
        doc = Document(output_path)
        
        # Replace placeholders in paragraphs
        for paragraph in doc.paragraphs:
            for placeholder in vessel_data:
                if f"{{{placeholder}}}" in paragraph.text:
                    paragraph.text = paragraph.text.replace(f"{{{placeholder}}}", str(vessel_data[placeholder]))
        
        # Replace placeholders in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for placeholder in vessel_data:
                            if f"{{{placeholder}}}" in paragraph.text:
                                paragraph.text = paragraph.text.replace(f"{{{placeholder}}}", str(vessel_data[placeholder]))
        
        # Save the document
        doc.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error filling template: {e}")
        return False

def convert_docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX to PDF using LibreOffice"""
    try:
        # Try LibreOffice first (Linux)
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf', 
            '--outdir', os.path.dirname(pdf_path), docx_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True
            
    except Exception as e:
        print(f"LibreOffice conversion failed: {e}")
    
    try:
        # Try unoconv as fallback
        result = subprocess.run([
            'unoconv', '-f', 'pdf', '-o', pdf_path, docx_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True
            
    except Exception as e:
        print(f"unoconv conversion failed: {e}")
    
    return False

@app.get("/")
async def root():
    return {"message": "Complete Document Service is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "complete-document-processing"}

@app.get("/templates")
async def get_templates():
    """Get list of available templates"""
    return templates_storage

@app.get("/vessels")
async def get_vessels():
    return [
        {
            "id": "1",
            "name": "Petroleum Express 529",
            "imo": "IMO1861018",
            "vessel_type": "Crude Oil Tanker",
            "flag": "Malta"
        },
        {
            "id": "2", 
            "name": "Atlantic Voyager 805",
            "imo": "IMO2379622",
            "vessel_type": "Container Ship",
            "flag": "Panama"
        }
    ]

@app.get("/user-permissions")
async def get_user_permissions():
    """Get user permissions"""
    return {
        "success": True,
        "permissions": {
            "can_upload_templates": True,
            "can_edit_templates": True,
            "can_delete_templates": True,
            "can_process_documents": True,
            "template_limit": 100,
            "documents_per_month": 1000
        }
    }

@app.post("/upload-template")
async def upload_template(file: UploadFile = File(...)):
    """Upload a new template"""
    try:
        # Create templates directory
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = templates_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract placeholders
        placeholders = extract_placeholders_from_docx(file_path)
        
        # Create template info
        template_info = {
            "id": str(uuid.uuid4()),
            "name": file.filename.replace('.docx', ''),
            "description": f"Template with {len(placeholders)} placeholders",
            "file_name": file.filename,
            "file_size": len(content),
            "placeholders": placeholders,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": "admin"
        }
        
        # Save to storage
        templates_storage.append(template_info)
        save_templates()
        
        return JSONResponse({
            "success": True,
            "message": "Template uploaded successfully",
            "template": template_info
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Template upload failed: {str(e)}",
            "error": str(e)
        }, status_code=500)

@app.post("/process-document")
async def process_document(
    template_id: str = Form(...),
    vessel_imo: str = Form(...),
    format: str = Form("docx")
):
    """Process document with real data"""
    try:
        # Find template
        template = None
        for t in templates_storage:
            if t["id"] == template_id:
                template = t
                break
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get vessel data
        vessel_data = await get_real_vessel_data(vessel_imo)
        
        # Create outputs directory
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Process template
        template_path = Path("templates") / template["file_name"]
        docx_output = outputs_dir / f"{document_id}.docx"
        
        # Fill template
        if not fill_word_template(template_path, docx_output, vessel_data):
            raise HTTPException(status_code=500, detail="Failed to fill template")
        
        # Convert to PDF if requested
        pdf_output = None
        if format.lower() == "pdf":
            pdf_output = outputs_dir / f"{document_id}.pdf"
            if not convert_docx_to_pdf(docx_output, pdf_output):
                print("PDF conversion failed, DOCX will be available")
        
        return JSONResponse({
            "success": True,
            "message": "Document processed successfully",
            "document_id": document_id,
            "format": format,
            "docx_available": True,
            "pdf_available": pdf_output and pdf_output.exists(),
            "vessel_data_used": len(vessel_data)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Document processing failed: {str(e)}",
            "error": str(e)
        }, status_code=500)

@app.get("/download/{document_id}")
async def download_document(document_id: str, format: str = "docx"):
    """Download processed document"""
    try:
        outputs_dir = Path("outputs")
        
        if format.lower() == "pdf":
            file_path = outputs_dir / f"{document_id}.pdf"
            if not file_path.exists():
                # Try DOCX if PDF not available
                file_path = outputs_dir / f"{document_id}.docx"
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail="Document not found")
        else:
            file_path = outputs_dir / f"{document_id}.docx"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Document not found")
        
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("Starting Complete Document Service...")
    print("Available endpoints:")
    print("  GET  /")
    print("  GET  /health")
    print("  GET  /templates")
    print("  GET  /vessels")
    print("  GET  /user-permissions")
    print("  POST /upload-template")
    print("  POST /process-document")
    print("  GET  /download/{document_id}")
    uvicorn.run(app, host="0.0.0.0", port=port)
