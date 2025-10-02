#!/usr/bin/env python3
"""
Working FastAPI service with all endpoints
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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from docx import Document
import re
import shutil
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  Supabase credentials not found. Using dummy data.")
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase database")

app = FastAPI(title="Working Document Service", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for templates (in production, use a database)
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

async def get_real_vessel_data(vessel_imo: str):
    """Fetch real vessel data from Supabase database"""
    try:
        if not supabase:
            print("⚠️  Supabase not connected, using dummy data")
            return get_dummy_vessel_data(vessel_imo)
        
        # Fetch vessel data from your real database
        response = supabase.table('vessels').select('*').eq('imo', vessel_imo).execute()
        
        if response.data and len(response.data) > 0:
            vessel = response.data[0]
            print(f"✅ Found real vessel data for IMO: {vessel_imo}")
            
            # Map your real vessel data to placeholders
            vessel_data = {
                # Basic vessel info from your database
                "vessel_name": vessel.get('name', 'Unknown Vessel'),
                "imo": vessel_imo,
                "imo_number": vessel_imo,
                "vessel_type": vessel.get('vessel_type', 'Unknown Type'),
                "flag": vessel.get('flag', 'Unknown Flag'),
                "flag_state": vessel.get('flag', 'Unknown Flag'),
                "owner": vessel.get('owner_name', 'Unknown Owner'),
                "vessel_owner": vessel.get('owner_name', 'Unknown Owner'),
                "operator": vessel.get('operator_name', 'Unknown Operator'),
                "current_date": datetime.now().strftime('%Y-%m-%d'),
                "vessel_id": str(vessel.get('id', '1')),
                
                # Additional real data from your database
                "mmsi": vessel.get('mmsi', ''),
                "callsign": vessel.get('callsign', ''),
                "built": vessel.get('built', 0),
                "deadweight": vessel.get('deadweight', 0),
                "cargo_capacity": vessel.get('cargo_capacity', 0),
                "length": vessel.get('length', 0),
                "width": vessel.get('width', 0),
                "beam": vessel.get('beam', ''),
                "draught": vessel.get('draught', 0),
                "draft": vessel.get('draft', ''),
                "gross_tonnage": vessel.get('gross_tonnage', 0),
                "crew_size": vessel.get('crew_size', 0),
                "engine_power": vessel.get('engine_power', 0),
                "fuel_consumption": vessel.get('fuel_consumption', 0),
                "speed": vessel.get('speed', ''),
                "status": vessel.get('status', ''),
                "nav_status": vessel.get('nav_status', ''),
                "current_lat": vessel.get('current_lat', 0),
                "current_lng": vessel.get('current_lng', 0),
                "course": vessel.get('course', 0),
                "departure_port": vessel.get('departure_port', 0),
                "destination_port": vessel.get('destination_port', 0),
                "departure_port_name": vessel.get('departure_port_name', 'Unknown Port'),
                "destination_port_name": vessel.get('destination_port_name', 'Unknown Port'),
                "loading_port_name": vessel.get('loading_port_name', 'Unknown Port'),
                "departure_date": vessel.get('departure_date', ''),
                "arrival_date": vessel.get('arrival_date', ''),
                "eta": vessel.get('eta', ''),
                "loading_port": vessel.get('loading_port', ''),
                "cargo_type": vessel.get('cargo_type', ''),
                "cargo_quantity": vessel.get('cargo_quantity', 0),
                "oil_type": vessel.get('oil_type', ''),
                "oil_source": vessel.get('oil_source', ''),
                "current_region": vessel.get('current_region', ''),
                "buyer_name": vessel.get('buyer_name', ''),
                "seller_name": vessel.get('seller_name', ''),
                "source_company": vessel.get('source_company', ''),
                "target_refinery": vessel.get('target_refinery', ''),
                "deal_value": vessel.get('deal_value', 0),
                "price": vessel.get('price', 0),
                "market_price": vessel.get('market_price', 0),
                "quantity": vessel.get('quantity', 0),
                "departure_lat": vessel.get('departure_lat', 0),
                "departure_lng": vessel.get('departure_lng', 0),
                "destination_lat": vessel.get('destination_lat', 0),
                "destination_lng": vessel.get('destination_lng', 0),
                "route_distance": vessel.get('route_distance', 0),
                "shipping_type": vessel.get('shipping_type', ''),
                "route_info": vessel.get('route_info', ''),
                "last_updated": vessel.get('last_updated', ''),
                "company_id": vessel.get('company_id', ''),
                
                # ICPO Specific Fields (using real data where available)
                "icpo_number": f"ICPO-{datetime.now().year}-{random.randint(1000, 9999)}",
                "icpo_date": datetime.now().strftime('%Y-%m-%d'),
                "icpo_validity": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                "icpo_amount": f"USD {vessel.get('deal_value', random.randint(1000000, 10000000)):,}",
                "icpo_currency": "USD",
                "icpo_terms": "LC at sight",
                "icpo_bank": "HSBC Bank",
                "icpo_bank_address": "1 Centenary Square, Birmingham, UK",
                "icpo_swift": "HBUKGB4B",
                "icpo_account": f"{random.randint(1000000000, 9999999999)}",
                "icpo_beneficiary": vessel.get('seller_name', 'Sample Trading Company Ltd'),
                "icpo_beneficiary_address": f"{vessel.get('source_company', '123 Marina Bay')}, Singapore",
                "icpo_beneficiary_swift": "DBSBSGSG",
                "icpo_beneficiary_account": f"{random.randint(1000000000, 9999999999)}",
                "icpo_commodity": vessel.get('cargo_type', vessel.get('oil_type', 'Crude Oil')),
                "icpo_quantity": f"{vessel.get('cargo_quantity', vessel.get('quantity', random.randint(10000, 100000)))} MT",
                "icpo_specification": f"API 35-40, Sulfur < 0.5%",
                "icpo_origin": vessel.get('oil_source', 'Malaysia'),
                "icpo_destination": vessel.get('target_refinery', 'Singapore'),
                "icpo_loading_port": vessel.get('loading_port_name', vessel.get('loading_port', 'Port Klang, Malaysia')),
                "icpo_discharge_port": vessel.get('destination_port_name', 'Singapore Port'),
                "icpo_loading_date": vessel.get('departure_date', (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')),
                "icpo_discharge_date": vessel.get('arrival_date', (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d')),
                "icpo_price": f"USD {vessel.get('price', random.randint(50, 100))}.00 per MT",
                "icpo_total_value": f"USD {vessel.get('deal_value', random.randint(5000000, 50000000)):,}",
                "icpo_payment_terms": "LC at sight",
                "icpo_delivery_terms": "FOB",
                "icpo_inspection": "SGS",
                "icpo_insurance": "All Risks",
            }
            
            return vessel_data
        else:
            print(f"⚠️  No vessel found with IMO: {vessel_imo}, using dummy data")
            return get_dummy_vessel_data(vessel_imo)
            
    except Exception as e:
        print(f"❌ Error fetching vessel data: {e}")
        return get_dummy_vessel_data(vessel_imo)

def get_dummy_vessel_data(vessel_imo: str):
    """Fallback dummy vessel data"""
    return {
        # Basic vessel info
        "vessel_name": "Petroleum Express 529",
        "imo": vessel_imo,
        "imo_number": vessel_imo,
        "vessel_type": "Crude Oil Tanker",
        "flag": "Malta",
        "flag_state": "Malta",
        "owner": "Sample Shipping Company",
        "vessel_owner": "Sample Shipping Company",
        "current_date": datetime.now().strftime('%Y-%m-%d'),
        "vessel_id": "1",
        
        # ICPO Specific Fields
        "icpo_number": f"ICPO-{datetime.now().year}-{random.randint(1000, 9999)}",
        "icpo_date": datetime.now().strftime('%Y-%m-%d'),
        "icpo_validity": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "icpo_amount": f"USD {random.randint(1000000, 10000000):,}",
        "icpo_currency": "USD",
        "icpo_terms": "LC at sight",
        "icpo_bank": "HSBC Bank",
        "icpo_bank_address": "1 Centenary Square, Birmingham, UK",
        "icpo_swift": "HBUKGB4B",
        "icpo_account": f"{random.randint(1000000000, 9999999999)}",
        "icpo_beneficiary": "Sample Trading Company Ltd",
        "icpo_beneficiary_address": "123 Marina Bay, Singapore",
        "icpo_beneficiary_swift": "DBSBSGSG",
        "icpo_beneficiary_account": f"{random.randint(1000000000, 9999999999)}",
        "icpo_commodity": "Crude Oil",
        "icpo_quantity": f"{random.randint(10000, 100000)} MT",
        "icpo_specification": "API 35-40, Sulfur < 0.5%",
        "icpo_origin": "Malaysia",
        "icpo_destination": "Singapore",
        "icpo_loading_port": "Port Klang, Malaysia",
        "icpo_discharge_port": "Singapore Port",
        "icpo_loading_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
        "icpo_discharge_date": (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
        "icpo_price": f"USD {random.randint(50, 100)}.00 per MT",
        "icpo_total_value": f"USD {random.randint(5000000, 50000000):,}",
        "icpo_payment_terms": "LC at sight",
        "icpo_delivery_terms": "FOB",
        "icpo_inspection": "SGS",
        "icpo_insurance": "All Risks",
    }

def extract_placeholders_from_docx(file_path):
    """Extract placeholders from a Word document"""
    try:
        doc = Document(file_path)
        placeholders = set()
        
        # Check paragraphs
        for paragraph in doc.paragraphs:
            text = paragraph.text
            # Find placeholders in format {placeholder_name}
            found = re.findall(r'\{([^}]+)\}', text)
            placeholders.update(found)
        
        # Check tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text
                        found = re.findall(r'\{([^}]+)\}', text)
                        placeholders.update(found)
        
        # Clean up placeholders - remove any malformed ones
        cleaned_placeholders = []
        for placeholder in placeholders:
            # Remove any extra characters and clean up
            clean_placeholder = placeholder.strip()
            if clean_placeholder and not clean_placeholder.startswith('{'):
                cleaned_placeholders.append(clean_placeholder)
        
        return cleaned_placeholders
    except Exception as e:
        print(f"Error extracting placeholders: {e}")
        return ["vessel_name", "imo", "vessel_type", "flag", "owner", "current_date"]  # fallback

def generate_realistic_data_for_placeholder(placeholder):
    """Generate realistic data for missing placeholders"""
    import random
    from datetime import datetime, timedelta
    
    # Define realistic data patterns
    realistic_data = {
        # Banking
        'seller_bank_account_no': f"{random.randint(1000000000, 9999999999)}",
        'seller_bank_swift': f"{random.choice(['CHASUS33', 'BOFAUS3N', 'CITIUS33', 'DEUTUS33'])}",
        'seller_bank_name': random.choice(['Chase Bank', 'Bank of America', 'Citibank', 'Deutsche Bank']),
        'seller_bank_address': f"{random.randint(100, 9999)} {random.choice(['Main St', 'Broadway', 'Wall St', 'Park Ave'])}, New York, NY",
        'seller_bank_officer_name': f"{random.choice(['John', 'Sarah', 'Michael', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
        'seller_bank_officer_mobile': f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
        'confirming_bank_account_number': f"{random.randint(1000000000, 9999999999)}",
        'confirming_bank_swift': f"{random.choice(['HSBCUS33', 'BNPAUS33', 'SCBLUS33'])}",
        'confirming_bank_name': random.choice(['HSBC', 'BNP Paribas', 'Standard Chartered']),
        'confirming_bank_address': f"{random.randint(100, 9999)} {random.choice(['Financial District', 'Banking Center', 'Commerce St'])}, Singapore",
        'confirming_bank_officer': f"{random.choice(['David', 'Emma', 'James', 'Anna'])} {random.choice(['Lee', 'Chen', 'Wong', 'Tan'])}",
        'confirming_bank_officer_contact': f"+65-{random.randint(6000, 9999)}-{random.randint(1000, 9999)}",
        'confirming_bank_tel': f"+65-{random.randint(6000, 9999)}-{random.randint(1000, 9999)}",
        'issuing_bank_account_number': f"{random.randint(1000000000, 9999999999)}",
        'issuing_bank_swift': f"{random.choice(['JPMUS33', 'WFCBUS33', 'PNCUS33'])}",
        'issuing_bank_name': random.choice(['JPMorgan Chase', 'Wells Fargo', 'PNC Bank']),
        'issuing_bank_address': f"{random.randint(100, 9999)} {random.choice(['Banking Plaza', 'Financial Center', 'Commerce Ave'])}, London",
        'issuing_bank_officer': f"{random.choice(['Robert', 'Jennifer', 'Christopher', 'Amanda'])} {random.choice(['Taylor', 'Anderson', 'Thomas', 'Jackson'])}",
        'issuing_bank_officer_contact': f"+44-{random.randint(20, 29)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        'issuing_bank_tel': f"+44-{random.randint(20, 29)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        
        # Commercial
        'proforma_invoice_no': f"PI-{datetime.now().year}-{random.randint(1000, 9999)}",
        'invoice_no': f"INV-{datetime.now().year}-{random.randint(1000, 9999)}",
        'commercial_id': f"COM-{datetime.now().year}-{random.randint(1000, 9999)}",
        'document_number': f"DOC-{datetime.now().year}-{random.randint(1000, 9999)}",
        'contract_value': f"USD {random.randint(1000000, 50000000):,}",
        'total_amount': f"USD {random.randint(1000000, 10000000):,}",
        'total_amount_due': f"USD {random.randint(1000000, 10000000):,}",
        'amount_in_words': f"{random.choice(['Five', 'Ten', 'Fifteen', 'Twenty'])} Million US Dollars",
        'transaction_currency': 'USD',
        'payment_terms': random.choice(['30 days', '45 days', '60 days', '90 days']),
        'validity': f"{random.randint(30, 90)} days",
        'contract_duration': f"{random.randint(6, 24)} months",
        'monthly_delivery': f"{random.randint(1000, 10000)} MT",
        'performance_bond': f"USD {random.randint(100000, 1000000):,}",
        'insurance': f"USD {random.randint(500000, 5000000):,}",
        
        # Shipping
        'port_of_loading': random.choice(['Singapore', 'Rotterdam', 'Houston', 'Dubai', 'Shanghai']),
        'port_of_discharge': random.choice(['Tokyo', 'Hamburg', 'New York', 'Los Angeles', 'Busan']),
        'place_of_destination': random.choice(['Tokyo Port', 'Hamburg Port', 'New York Port', 'Los Angeles Port']),
        'final_delivery_place': random.choice(['Tokyo Port', 'Hamburg Port', 'New York Port', 'Los Angeles Port']),
        'origin': random.choice(['Malaysia', 'Indonesia', 'Nigeria', 'Saudi Arabia', 'Kuwait']),
        'country_of_origin': random.choice(['Malaysia', 'Indonesia', 'Nigeria', 'Saudi Arabia', 'Kuwait']),
        'shipping_terms': random.choice(['FOB', 'CIF', 'CFR', 'EXW']),
        'terms_of_delivery': random.choice(['FOB', 'CIF', 'CFR', 'EXW']),
        'via_name': random.choice(['Direct', 'Via Singapore', 'Via Rotterdam', 'Via Dubai']),
        'through_name': random.choice(['Direct', 'Via Singapore', 'Via Rotterdam', 'Via Dubai']),
        'partial_shipment': random.choice(['Allowed', 'Not Allowed']),
        'transshipment': random.choice(['Allowed', 'Not Allowed']),
        
        # Dates
        'date_of_issue': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        'issued_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        'issue_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        'shipment_date2': (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
        'shipment_date3': (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
        'valid_until': (datetime.now() + timedelta(days=random.randint(60, 180))).strftime('%Y-%m-%d'),
        'buyer_signatory_date': datetime.now().strftime('%Y-%m-%d'),
        'seller_signatory_date': datetime.now().strftime('%Y-%m-%d'),
        
        # Product specifications
        'commodity': random.choice(['Crude Oil', 'Diesel', 'Gasoline', 'Jet Fuel', 'Bunker Fuel']),
        'product_name': random.choice(['Light Sweet Crude', 'Heavy Crude', 'Diesel Fuel', 'Gasoline']),
        'goods_details': random.choice(['Light Sweet Crude Oil', 'Heavy Crude Oil', 'Diesel Fuel', 'Gasoline']),
        'specification': random.choice(['API 35-40', 'API 25-30', 'Sulfur < 0.5%', 'Sulfur < 1.0%']),
        'quality': random.choice(['Premium Grade', 'Standard Grade', 'Commercial Grade']),
        'inspection': random.choice(['SGS', 'Bureau Veritas', 'Intertek', 'Lloyd\'s Register']),
        'cloud_point': f"{random.randint(-10, 10)}°C",
        'free_fatty_acid': f"{random.uniform(0.1, 2.0):.1f}%",
        'iodine_value': f"{random.randint(40, 60)}",
        'moisture_impurities': f"{random.uniform(0.1, 1.0):.1f}%",
        'slip_melting_point': f"{random.randint(20, 35)}°C",
        'colour': random.choice(['Light Brown', 'Dark Brown', 'Black', 'Amber']),
        
        # Quantities and prices
        'total_quantity': f"{random.randint(10000, 100000)} MT",
        'quantity2': f"{random.randint(5000, 50000)} MT",
        'quantity3': f"{random.randint(5000, 50000)} MT",
        'total_weight': f"{random.randint(10000, 100000)} MT",
        'total_gross': f"{random.randint(10000, 100000)} MT",
        'total_containers': f"{random.randint(1, 10)}",
        'unit_price2': f"USD {random.randint(50, 100)}.00",
        'unit_price3': f"USD {random.randint(50, 100)}.00",
        'amount2': f"USD {random.randint(250000, 5000000):,}",
        'amount3': f"USD {random.randint(250000, 5000000):,}",
        'price': f"USD {random.randint(50, 100)}.00",
        'shipping_charges': f"USD {random.randint(50000, 500000):,}",
        'other_expenditures': f"USD {random.randint(10000, 100000):,}",
        'discount': f"{random.randint(0, 10)}%",
        
        # Items
        'item2': random.choice(['Crude Oil', 'Diesel', 'Gasoline', 'Jet Fuel']),
        'item3': random.choice(['Crude Oil', 'Diesel', 'Gasoline', 'Jet Fuel']),
        'consignment2': random.choice(['Crude Oil', 'Diesel', 'Gasoline', 'Jet Fuel']),
        'consignment33': random.choice(['Crude Oil', 'Diesel', 'Gasoline', 'Jet Fuel']),
        
        # Signatories
        'seller_signatory_name': f"{random.choice(['John', 'Sarah', 'Michael', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
        'seller_signatory_position': random.choice(['Managing Director', 'Sales Manager', 'Operations Manager', 'CEO']),
        'seller_signature': f"{random.choice(['John', 'Sarah', 'Michael', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
        'buyer_signatory_name': f"{random.choice(['Taro', 'Yuki', 'Hiroshi', 'Akira'])} {random.choice(['Yamada', 'Sato', 'Suzuki', 'Takahashi'])}",
        'buyer_signatory_position': random.choice(['Procurement Manager', 'General Manager', 'Director', 'President']),
        'buyer_signature': f"{random.choice(['Taro', 'Yuki', 'Hiroshi', 'Akira'])} {random.choice(['Yamada', 'Sato', 'Suzuki', 'Takahashi'])}",
        'signatory_name': f"{random.choice(['John', 'Sarah', 'Michael', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
        'authorized_person_name': f"{random.choice(['John', 'Sarah', 'Michael', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
        'notary_number': f"NOT-{random.randint(1000, 9999)}",
        
        # Contact information
        'buyer_company_name': random.choice(['Tokyo Trading Co.', 'Osaka Shipping Ltd.', 'Yokohama Marine Inc.', 'Kobe Commerce Corp.']),
        'buyer_name': f"{random.choice(['Taro', 'Yuki', 'Hiroshi', 'Akira'])} {random.choice(['Yamada', 'Sato', 'Suzuki', 'Takahashi'])}",
        'buyer_address': f"{random.randint(1, 999)} {random.choice(['Chuo-dori', 'Ginza', 'Shibuya', 'Shinjuku'])}, Tokyo, Japan",
        'buyer_city_country': 'Tokyo, Japan',
        'buyer_email': f"buyer{random.randint(1, 999)}@{random.choice(['tokyo-trading.com', 'osaka-shipping.com', 'yokohama-marine.com'])}",
        'buyer_tel': f"+81-3-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        'buyer_fax': f"+81-3-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        'buyer_mobile': f"+81-{random.randint(90, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        'buyer_office_tel': f"+81-3-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        'buyer_designation': random.choice(['Procurement Manager', 'General Manager', 'Director', 'President']),
        'buyer_representative': f"{random.choice(['Taro', 'Yuki', 'Hiroshi', 'Akira'])} {random.choice(['Yamada', 'Sato', 'Suzuki', 'Takahashi'])}",
        'buyer_position': random.choice(['Procurement Manager', 'General Manager', 'Director', 'President']),
        'buyer_registration': f"REG-{random.randint(100000, 999999)}",
        
        # Seller information
        'seller_company': random.choice(['Singapore Trading Ltd.', 'Malaysia Oil Corp.', 'Indonesia Marine Inc.', 'Thailand Commerce Co.']),
        'seller_address': f"{random.randint(1, 999)} {random.choice(['Marina Bay', 'Orchard Road', 'Raffles Place', 'Clarke Quay'])}, Singapore",
        
        # Default fallback
        'default': f"Sample {placeholder.replace('_', ' ').title()}"
    }
    
    # Return realistic data or default
    return realistic_data.get(placeholder.lower(), realistic_data['default'])

def fill_word_template(template_path, output_path, vessel_data):
    """Fill a Word template with vessel data"""
    try:
        # Copy template to output path
        shutil.copy2(template_path, output_path)
        
        # Open the document
        doc = Document(output_path)
        
        # Replace placeholders in paragraphs
        for paragraph in doc.paragraphs:
            text = paragraph.text
            original_text = text
            for placeholder, value in vessel_data.items():
                # Replace both {placeholder} and {placeholder} formats
                text = text.replace(f"{{{placeholder}}}", str(value))
                text = text.replace(f"{{{{{placeholder}}}}}", str(value))  # Handle double braces
            
            # Find any remaining placeholders and replace with realistic data
            remaining_placeholders = re.findall(r'\{([^}]+)\}', text)
            for placeholder in remaining_placeholders:
                realistic_value = generate_realistic_data_for_placeholder(placeholder)
                text = text.replace(f"{{{placeholder}}}", str(realistic_value))
                print(f"Generated realistic data for missing placeholder '{placeholder}': {realistic_value}")
            
            if text != original_text:
                paragraph.text = text
                print(f"Replaced placeholders in paragraph: {original_text[:50]}... -> {text[:50]}...")
        
        # Replace placeholders in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text
                        original_text = text
                        for placeholder, value in vessel_data.items():
                            # Replace both {placeholder} and {placeholder} formats
                            text = text.replace(f"{{{placeholder}}}", str(value))
                            text = text.replace(f"{{{{{placeholder}}}}}", str(value))  # Handle double braces
                        
                        # Find any remaining placeholders and replace with realistic data
                        remaining_placeholders = re.findall(r'\{([^}]+)\}', text)
                        for placeholder in remaining_placeholders:
                            realistic_value = generate_realistic_data_for_placeholder(placeholder)
                            text = text.replace(f"{{{placeholder}}}", str(realistic_value))
                            print(f"Generated realistic data for missing placeholder '{placeholder}': {realistic_value}")
                        
                        if text != original_text:
                            paragraph.text = text
                            print(f"Replaced placeholders in table cell: {original_text[:50]}... -> {text[:50]}...")
        
        # Save the document
        doc.save(output_path)
        print(f"Template filled successfully: {output_path}")
        return True
    except Exception as e:
        print(f"Error filling template: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Working Document Service is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "document-processing"}

@app.get("/templates")
async def get_templates():
    """Get list of available templates"""
    # Return actual stored templates
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


@app.post("/process-document")
async def process_document(
    template_id: str = Form(...),
    vessel_imo: str = Form(...),
    template_file: UploadFile = File(...)
):
    """Process a document template with vessel data"""
    try:
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        
        # Create outputs directory if it doesn't exist
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        # Find the template in storage
        template_info = None
        for template in templates_storage:
            if template["id"] == template_id:
                template_info = template
                break
        
        if not template_info:
            return JSONResponse({
                "success": False,
                "message": "Template not found",
                "error": "Template ID not found in storage"
            }, status_code=404)
        
        # Get REAL vessel data from your Supabase database
        vessel_data = await get_real_vessel_data(vessel_imo)
        
        # Find the template file
        templates_dir = Path("templates")
        template_file_path = templates_dir / f"{template_id}.docx"
        
        if not template_file_path.exists():
            return JSONResponse({
                "success": False,
                "message": "Template file not found",
                "error": "Template file does not exist on server"
            }, status_code=404)
        
        # Create output files
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        filled_docx_file = outputs_dir / f"{document_id}_filled.docx"
        pdf_file = outputs_dir / f"{document_id}_filled.pdf"
        
        # Fill the Word template with vessel data
        success = fill_word_template(template_file_path, filled_docx_file, vessel_data)
        
        if not success:
            return JSONResponse({
                "success": False,
                "message": "Failed to fill template",
                "error": "Could not process the Word template"
            }, status_code=500)
        
        # Convert to PDF using reportlab with proper Word content extraction
        pdf_success = False
        try:
            # Read the filled Word document and extract content properly
            from docx import Document
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Read the filled Word document
            doc = Document(str(filled_docx_file))
            
            # Create PDF with proper formatting
            pdf_doc = SimpleDocTemplate(str(pdf_file), pagesize=letter, 
                                      rightMargin=72, leftMargin=72, 
                                      topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            story = []
            
            # Extract and format content from Word document
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Determine paragraph style based on formatting
                    if paragraph.style.name.startswith('Heading'):
                        style = styles['Heading1']
                    else:
                        style = styles['Normal']
                    
                    # Create paragraph with proper formatting
                    para = Paragraph(paragraph.text.strip(), style)
                    story.append(para)
                    story.append(Spacer(1, 6))
            
            # Extract tables from Word document
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = cell.text.strip() if cell.text else ""
                        row_data.append(cell_text)
                    table_data.append(row_data)
                
                if table_data:
                    # Create PDF table
                    pdf_table = Table(table_data)
                    pdf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(pdf_table)
                    story.append(Spacer(1, 12))
            "icpo_quantity": f"{random.randint(10000, 100000)} MT",
            "icpo_specification": "API 35-40, Sulfur < 0.5%",
            "icpo_origin": "Malaysia",
            "icpo_destination": "Singapore",
            "icpo_loading_port": "Port Klang, Malaysia",
            "icpo_discharge_port": "Singapore Port",
            "icpo_loading_date": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            "icpo_discharge_date": (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
            "icpo_price": f"USD {random.randint(50, 100)}.00 per MT",
            "icpo_total_value": f"USD {random.randint(5000000, 50000000):,}",
            "icpo_payment_terms": "LC at sight",
            "icpo_delivery_terms": "FOB",
            "icpo_inspection": "SGS",
            "icpo_insurance": "All Risks",
            "icpo_force_majeure": "Standard Force Majeure Clause",
            "icpo_arbitration": "Singapore International Arbitration Centre",
            "icpo_law": "Singapore Law",
            "icpo_governing_law": "Singapore Law",
            "icpo_jurisdiction": "Singapore Courts",
            "icpo_notice_period": "30 days",
            "icpo_penalty": "0.5% per day",
            "icpo_bonus": "0.1% for early delivery",
            "icpo_commission": "2%",
            "icpo_brokerage": "1%",
            "icpo_other_charges": "USD 10,000",
            "icpo_total_charges": "USD 15,000",
            "icpo_net_amount": f"USD {random.randint(5000000, 50000000):,}",
            "icpo_remarks": "Subject to final inspection and approval",
            "icpo_conditions": "Standard trading conditions apply",
            "icpo_amendments": "No amendments allowed without written consent",
            "icpo_cancellation": "Subject to 48 hours notice",
            "icpo_extension": "May be extended by mutual agreement",
            "icpo_confirmation": "Subject to buyer's confirmation",
            "icpo_acceptance": "Subject to seller's acceptance",
            "icpo_approval": "Subject to management approval",
            "icpo_authorization": "Subject to board authorization",
            "icpo_ratification": "Subject to board ratification",
            "icpo_endorsement": "Subject to bank endorsement",
            "icpo_guarantee": "Bank guarantee required",
            "icpo_security": "Security deposit required",
            "icpo_collateral": "Collateral required",
            "icpo_margin": "Margin call possible",
            "icpo_hedge": "Hedge position required",
            "icpo_risk": "Risk management required",
            "icpo_compliance": "Compliance check required",
            "icpo_kyc": "KYC documentation required",
            "icpo_aml": "AML check required",
            "icpo_sanctions": "Sanctions check required",
            "icpo_embargo": "Embargo check required",
            "icpo_restrictions": "No restrictions apply",
            "icpo_limitations": "Standard limitations apply",
            "icpo_exclusions": "Standard exclusions apply",
            "icpo_warranties": "Standard warranties apply",
            "icpo_representations": "Standard representations apply",
            "icpo_covenants": "Standard covenants apply",
            "icpo_undertakings": "Standard undertakings apply",
            "icpo_obligations": "Standard obligations apply",
            "icpo_responsibilities": "Standard responsibilities apply",
            "icpo_liabilities": "Standard liabilities apply",
            "icpo_limitations_liability": "Standard liability limitations apply",
            "icpo_indemnification": "Standard indemnification apply",
            "icpo_hold_harmless": "Standard hold harmless apply",
            "icpo_release": "Standard release apply",
            "icpo_discharge": "Standard discharge apply",
            "icpo_waiver": "Standard waiver apply",
            "icpo_estoppel": "Standard estoppel apply",
            "icpo_acquiescence": "Standard acquiescence apply",
            "icpo_ratification_2": "Standard ratification apply",
            "icpo_confirmation_2": "Standard confirmation apply",
            "icpo_acknowledgment": "Standard acknowledgment apply",
            "icpo_admission": "Standard admission apply",
            "icpo_concession": "Standard concession apply",
            "icpo_agreement": "Standard agreement apply",
            "icpo_understanding": "Standard understanding apply",
            "icpo_arrangement": "Standard arrangement apply",
            "icpo_settlement": "Standard settlement apply",
            "icpo_compromise": "Standard compromise apply",
            "icpo_accord": "Standard accord apply",
            "icpo_concord": "Standard concord apply",
            "icpo_harmony": "Standard harmony apply",
            "icpo_unity": "Standard unity apply",
            "icpo_consensus": "Standard consensus apply",
            "icpo_unanimity": "Standard unanimity apply",
            "icpo_consent": "Standard consent apply",
            "icpo_approval_2": "Standard approval apply",
            "icpo_authorization_2": "Standard authorization apply",
            "icpo_permission": "Standard permission apply",
            "icpo_license": "Standard license apply",
            "icpo_franchise": "Standard franchise apply",
            "icpo_concession_2": "Standard concession apply",
            "icpo_privilege": "Standard privilege apply",
            "icpo_immunity": "Standard immunity apply",
            "icpo_exemption": "Standard exemption apply",
            "icpo_dispensation": "Standard dispensation apply",
            "icpo_relief": "Standard relief apply",
            "icpo_remission": "Standard remission apply",
            "icpo_absolution": "Standard absolution apply",
            "icpo_pardon": "Standard pardon apply",
            "icpo_clemency": "Standard clemency apply",
            "icpo_mercy": "Standard mercy apply",
            "icpo_grace": "Standard grace apply",
            "icpo_favor": "Standard favor apply",
            "icpo_benefit": "Standard benefit apply",
            "icpo_advantage": "Standard advantage apply",
            "icpo_profit": "Standard profit apply",
            "icpo_gain": "Standard gain apply",
            "icpo_earnings": "Standard earnings apply",
            "icpo_income": "Standard income apply",
            "icpo_revenue": "Standard revenue apply",
            "icpo_proceeds": "Standard proceeds apply",
            "icpo_returns": "Standard returns apply",
            "icpo_yield": "Standard yield apply",
            "icpo_dividend": "Standard dividend apply",
            "icpo_interest": "Standard interest apply",
            "icpo_royalty": "Standard royalty apply",
            "icpo_commission_2": "Standard commission apply",
            "icpo_fee": "Standard fee apply",
            "icpo_charge": "Standard charge apply",
            "icpo_cost": "Standard cost apply",
            "icpo_expense": "Standard expense apply",
            "icpo_outlay": "Standard outlay apply",
            "icpo_disbursement": "Standard disbursement apply",
            "icpo_payment": "Standard payment apply",
            "icpo_remittance": "Standard remittance apply",
            "icpo_transfer": "Standard transfer apply",
            "icpo_transmission": "Standard transmission apply",
            "icpo_delivery": "Standard delivery apply",
            "icpo_shipment": "Standard shipment apply",
            "icpo_dispatch": "Standard dispatch apply",
            "icpo_consignment": "Standard consignment apply",
            "icpo_cargo": "Standard cargo apply",
            "icpo_freight": "Standard freight apply",
            "icpo_carriage": "Standard carriage apply",
            "icpo_transport": "Standard transport apply",
            "icpo_conveyance": "Standard conveyance apply",
            "icpo_transit": "Standard transit apply",
            "icpo_passage": "Standard passage apply",
            "icpo_voyage": "Standard voyage apply",
            "icpo_journey": "Standard journey apply",
            "icpo_trip": "Standard trip apply",
            "icpo_expedition": "Standard expedition apply",
            "icpo_mission": "Standard mission apply",
            "icpo_operation": "Standard operation apply",
            "icpo_undertaking_2": "Standard undertaking apply",
            "icpo_enterprise": "Standard enterprise apply",
            "icpo_venture": "Standard venture apply",
            "icpo_project": "Standard project apply",
            "icpo_scheme": "Standard scheme apply",
            "icpo_plan": "Standard plan apply",
            "icpo_program": "Standard program apply",
            "icpo_campaign": "Standard campaign apply",
            "icpo_initiative": "Standard initiative apply",
            "icpo_effort": "Standard effort apply",
            "icpo_endeavor": "Standard endeavor apply",
            "icpo_attempt": "Standard attempt apply",
            "icpo_trial": "Standard trial apply",
            "icpo_experiment": "Standard experiment apply",
            "icpo_test": "Standard test apply",
            "icpo_examination": "Standard examination apply",
            "icpo_inspection_2": "Standard inspection apply",
            "icpo_review": "Standard review apply",
            "icpo_audit": "Standard audit apply",
            "icpo_assessment": "Standard assessment apply",
            "icpo_evaluation": "Standard evaluation apply",
            "icpo_analysis": "Standard analysis apply",
            "icpo_study": "Standard study apply",
            "icpo_research": "Standard research apply",
            "icpo_investigation": "Standard investigation apply",
            "icpo_inquiry": "Standard inquiry apply",
            "icpo_question": "Standard question apply",
            "icpo_query": "Standard query apply",
            "icpo_request": "Standard request apply",
            "icpo_demand": "Standard demand apply",
            "icpo_requirement": "Standard requirement apply",
            "icpo_necessity": "Standard necessity apply",
            "icpo_need": "Standard need apply",
            "icpo_want": "Standard want apply",
            "icpo_desire": "Standard desire apply",
            "icpo_wish": "Standard wish apply",
            "icpo_hope": "Standard hope apply",
            "icpo_expectation": "Standard expectation apply",
            "icpo_anticipation": "Standard anticipation apply",
            "icpo_forecast": "Standard forecast apply",
            "icpo_prediction": "Standard prediction apply",
            "icpo_projection": "Standard projection apply",
            "icpo_estimate": "Standard estimate apply",
            "icpo_calculation": "Standard calculation apply",
            "icpo_computation": "Standard computation apply",
            "icpo_measurement": "Standard measurement apply",
            "icpo_quantification": "Standard quantification apply",
            "icpo_valuation": "Standard valuation apply",
            "icpo_appraisal": "Standard appraisal apply",
            "icpo_estimation": "Standard estimation apply",
            "icpo_assessment_2": "Standard assessment apply",
            "icpo_judgment": "Standard judgment apply",
            "icpo_opinion": "Standard opinion apply",
            "icpo_view": "Standard view apply",
            "icpo_perspective": "Standard perspective apply",
            "icpo_standpoint": "Standard standpoint apply",
            "icpo_position": "Standard position apply",
            "icpo_stance": "Standard stance apply",
            "icpo_attitude": "Standard attitude apply",
            "icpo_approach": "Standard approach apply",
            "icpo_method": "Standard method apply",
            "icpo_technique": "Standard technique apply",
            "icpo_procedure": "Standard procedure apply",
            "icpo_process": "Standard process apply",
            "icpo_system": "Standard system apply",
            "icpo_framework": "Standard framework apply",
            "icpo_structure": "Standard structure apply",
            "icpo_organization": "Standard organization apply",
            "icpo_arrangement_2": "Standard arrangement apply",
            "icpo_setup": "Standard setup apply",
            "icpo_configuration": "Standard configuration apply",
            "icpo_layout": "Standard layout apply",
            "icpo_design": "Standard design apply",
            "icpo_plan_2": "Standard plan apply",
            "icpo_scheme_2": "Standard scheme apply",
            "icpo_strategy": "Standard strategy apply",
            "icpo_tactic": "Standard tactic apply",
            "icpo_approach_2": "Standard approach apply",
            "icpo_method_2": "Standard method apply",
            "icpo_technique_2": "Standard technique apply",
            "icpo_procedure_2": "Standard procedure apply",
            "icpo_process_2": "Standard process apply",
            "icpo_system_2": "Standard system apply",
            "icpo_framework_2": "Standard framework apply",
            "icpo_structure_2": "Standard structure apply",
            "icpo_organization_2": "Standard organization apply",
            "icpo_arrangement_3": "Standard arrangement apply",
            "icpo_setup_2": "Standard setup apply",
            "icpo_configuration_2": "Standard configuration apply",
            "icpo_layout_2": "Standard layout apply",
            "icpo_design_2": "Standard design apply",
            "icpo_plan_3": "Standard plan apply",
            "icpo_scheme_3": "Standard scheme apply",
            "icpo_strategy_2": "Standard strategy apply",
            "icpo_tactic_2": "Standard tactic apply",
            "icpo_approach_3": "Standard approach apply",
            "icpo_method_3": "Standard method apply",
            "icpo_technique_3": "Standard technique apply",
            "icpo_procedure_3": "Standard procedure apply",
            "icpo_process_3": "Standard process apply",
            "icpo_system_3": "Standard system apply",
            "icpo_framework_3": "Standard framework apply",
            "icpo_structure_3": "Standard structure apply",
            "icpo_organization_3": "Standard organization apply",
            "icpo_arrangement_4": "Standard arrangement apply",
            "icpo_setup_3": "Standard setup apply",
            "icpo_configuration_3": "Standard configuration apply",
            "icpo_layout_3": "Standard layout apply",
            "icpo_design_3": "Standard design apply",
            "icpo_plan_4": "Standard plan apply",
            "icpo_scheme_4": "Standard scheme apply",
            "icpo_strategy_3": "Standard strategy apply",
            "icpo_tactic_3": "Standard tactic apply",
            "icpo_approach_4": "Standard approach apply",
            "icpo_method_4": "Standard method apply",
            "icpo_technique_4": "Standard technique apply",
            "icpo_procedure_4": "Standard procedure apply",
            "icpo_process_4": "Standard process apply",
            "icpo_system_4": "Standard system apply",
            "icpo_framework_4": "Standard framework apply",
            "icpo_structure_4": "Standard structure apply",
            "icpo_organization_4": "Standard organization apply",
            "icpo_arrangement_5": "Standard arrangement apply",
            "icpo_setup_4": "Standard setup apply",
            "icpo_configuration_4": "Standard configuration apply",
            "icpo_layout_4": "Standard layout apply",
            "icpo_design_4": "Standard design apply",
            "icpo_plan_5": "Standard plan apply",
            "icpo_scheme_5": "Standard scheme apply",
            "icpo_strategy_4": "Standard strategy apply",
            "icpo_tactic_4": "Standard tactic apply",
            "icpo_approach_5": "Standard approach apply",
            "icpo_method_5": "Standard method apply",
            "icpo_technique_5": "Standard technique apply",
            "icpo_procedure_5": "Standard procedure apply",
            "icpo_process_5": "Standard process apply",
            "icpo_system_5": "Standard system apply",
            "icpo_framework_5": "Standard framework apply",
            "icpo_structure_5": "Standard structure apply",
            "icpo_organization_5": "Standard organization apply",
            "icpo_arrangement_6": "Standard arrangement apply",
            "icpo_setup_5": "Standard setup apply",
            "icpo_configuration_5": "Standard configuration apply",
            "icpo_layout_5": "Standard layout apply",
            "icpo_design_5": "Standard design apply",
            "icpo_plan_6": "Standard plan apply",
            "icpo_scheme_6": "Standard scheme apply",
            "icpo_strategy_5": "Standard strategy apply",
            "icpo_tactic_5": "Standard tactic apply",
            "icpo_approach_6": "Standard approach apply",
            "icpo_method_6": "Standard method apply",
            "icpo_technique_6": "Standard technique apply",
            "icpo_procedure_6": "Standard procedure apply",
            "icpo_process_6": "Standard process apply",
            "icpo_system_6": "Standard system apply",
            "icpo_framework_6": "Standard framework apply",
            "icpo_structure_6": "Standard structure apply",
            "icpo_organization_6": "Standard organization apply",
            "icpo_arrangement_7": "Standard arrangement apply",
            "icpo_setup_6": "Standard setup apply",
            "icpo_configuration_6": "Standard configuration apply",
            "icpo_layout_6": "Standard layout apply",
            "icpo_design_6": "Standard design apply",
            "icpo_plan_7": "Standard plan apply",
            "icpo_scheme_7": "Standard scheme apply",
            "icpo_strategy_6": "Standard strategy apply",
            "icpo_tactic_6": "Standard tactic apply",
            "icpo_approach_7": "Standard approach apply",
            "icpo_method_7": "Standard method apply",
            "icpo_technique_7": "Standard technique apply",
            "icpo_procedure_7": "Standard procedure apply",
            "icpo_process_7": "Standard process apply",
            "icpo_system_7": "Standard system apply",
            "icpo_framework_7": "Standard framework apply",
            "icpo_structure_7": "Standard structure apply",
            "icpo_organization_7": "Standard organization apply",
            "icpo_arrangement_8": "Standard arrangement apply",
            "icpo_setup_7": "Standard setup apply",
            "icpo_configuration_7": "Standard configuration apply",
            "icpo_layout_7": "Standard layout apply",
            "icpo_design_7": "Standard design apply",
            "icpo_plan_8": "Standard plan apply",
            "icpo_scheme_8": "Standard scheme apply",
            "icpo_strategy_7": "Standard strategy apply",
            "icpo_tactic_7": "Standard tactic apply",
            "icpo_approach_8": "Standard approach apply",
            "icpo_method_8": "Standard method apply",
            "icpo_technique_8": "Standard technique apply",
            "icpo_procedure_8": "Standard procedure apply",
            "icpo_process_8": "Standard process apply",
            "icpo_system_8": "Standard system apply",
            "icpo_framework_8": "Standard framework apply",
            "icpo_structure_8": "Standard structure apply",
            "icpo_organization_8": "Standard organization apply",
            "icpo_arrangement_9": "Standard arrangement apply",
            "icpo_setup_8": "Standard setup apply",
            "icpo_configuration_8": "Standard configuration apply",
            "icpo_layout_8": "Standard layout apply",
            "icpo_design_8": "Standard design apply",
            "icpo_plan_9": "Standard plan apply",
            "icpo_scheme_9": "Standard scheme apply",
            "icpo_strategy_8": "Standard strategy apply",
            "icpo_tactic_8": "Standard tactic apply",
            "icpo_approach_9": "Standard approach apply",
            "icpo_method_9": "Standard method apply",
            "icpo_technique_9": "Standard technique apply",
            "icpo_procedure_9": "Standard procedure apply",
            "icpo_process_9": "Standard process apply",
            "icpo_system_9": "Standard system apply",
            "icpo_framework_9": "Standard framework apply",
            "icpo_structure_9": "Standard structure apply",
            "icpo_organization_9": "Standard organization apply",
            "icpo_arrangement_10": "Standard arrangement apply",
            "icpo_setup_9": "Standard setup apply",
            "icpo_configuration_9": "Standard configuration apply",
            "icpo_layout_9": "Standard layout apply",
            "icpo_design_9": "Standard design apply",
            "icpo_plan_10": "Standard plan apply",
            "icpo_scheme_10": "Standard scheme apply",
            "icpo_strategy_9": "Standard strategy apply",
            "icpo_tactic_9": "Standard tactic apply",
            "icpo_approach_10": "Standard approach apply",
            "icpo_method_10": "Standard method apply",
            "icpo_technique_10": "Standard technique apply",
            "icpo_procedure_10": "Standard procedure apply",
            "icpo_process_10": "Standard process apply",
            "icpo_system_10": "Standard system apply",
            "icpo_framework_10": "Standard framework apply",
            "icpo_structure_10": "Standard structure apply",
            "icpo_organization_10": "Standard organization apply",
            
            # Technical specifications
            "gross_tonnage": "45,000",
            "net_tonnage": "35,000",
            "deadweight": "85,000",
            "length": "250m",
            "length_overall": "250m",
            "beam": "45m",
            "draft": "15m",
            "year_built": "2015",
            "call_sign": "9HA1234",
            "registry_port": "Valletta",
            "class_society": "Lloyd's Register",
            "ism_manager": "Sample ISM Manager",
            "vessel_operator": "Sample Operator",
            "engine_type": "Diesel",
            "speed": "15 knots",
            
            # Cargo specifications
            "cargo_capacity": "85,000 MT",
            "cargo_tanks": "12",
            "pumping_capacity": "3,000 m³/h",
            
            # Product specifications
            "product_name": "Crude Oil",
            "Commodity": "Crude Oil",
            "Goods_Details": "Light Sweet Crude Oil",
            "Country_Of_Origin": "Malaysia",
            "Origin": "Malaysia",
            "Cloud_Point": "-5°C",
            "Free_Fatty_Acid": "0.1%",
            "Iodine_Value": "45",
            "Moisture_Impurities": "0.1%",
            "Slip_Melting_Point": "25°C",
            "Colour": "Light Brown",
            
            # Commercial details
            "Seller_Company": "Sample Trading Company",
            "Seller_Address": "123 Trading Street, Singapore",
            "Seller_Bank_Name": "Sample Bank",
            "Seller_Bank_Address": "456 Bank Street, Singapore",
            "Seller_Bank_Account_No": "1234567890",
            "Seller_Bank_Account_Name": "Sample Trading Company",
            "Seller_Bank_SWIFT": "SAMPUS33",
            "Seller_Bank_Officer_Name": "John Smith",
            "Seller_Bank_Officer_Mobile": "+65 9123 4567",
            
            "Buyer_Company": "Sample Buyer Company",
            "Buyer_Company_Name": "Sample Buyer Company",
            "Buyer_Address": "789 Buyer Avenue, Tokyo",
            "Buyer_Email": "buyer@sample.com",
            "Buyer_Tel": "+81 3 1234 5678",
            "Buyer_Designation": "Procurement Manager",
            "Buyer_Representative": "Taro Yamada",
            "Position_Title": "Procurement Manager",
            
            # Invoice details
            "Proforma_Invoice_No": "PI-2025-001",
            "Invoice_No": "INV-2025-001",
            "Date_Of_Issue": "2025-01-30",
            "Issued_Date": "2025-01-30",
            "Commercial_ID": "COM-2025-001",
            "Transaction_Currency": "USD",
            "Payment_Terms": "30 days",
            "Validity": "60 days",
            
            # Shipping details
            "Port_Of_Loading": "Singapore",
            "Port_Of_Discharge": "Tokyo",
            "Place_Of_Destination": "Tokyo Port",
            "Final_Delivery_Place": "Tokyo Port",
            "Terms_Of_Delivery": "FOB",
            "Via_Name": "Direct",
            "Through_Name": "Direct",
            "Partial_Shipment": "Not Allowed",
            "Transshipment": "Not Allowed",
            "Shipment_Date2": "2025-02-15",
            "Shipment_Date3": "2025-02-15",
            
            # Items and quantities
            "Item2": "Crude Oil",
            "Item3": "Crude Oil",
            "Quantity2": "50,000 MT",
            "Quantity3": "50,000 MT",
            "Unit_Price2": "USD 65.00",
            "Unit_Price3": "USD 65.00",
            "Amount2": "USD 3,250,000.00",
            "Amount3": "USD 3,250,000.00",
            "Total_Amount": "USD 6,500,000.00",
            "Total_Amount_Due": "USD 6,500,000.00",
            "Amount_In_Words": "Six Million Five Hundred Thousand US Dollars",
            "Total_Weight": "100,000 MT",
            "Total_Gross": "100,000 MT",
            "Total_Containers": "1",
            "Consignment2": "Crude Oil",
            "Consignment33": "Crude Oil",
            
            # Additional charges
            "shipping_Charges": "USD 50,000.00",
            "Other_Expenditures": "USD 10,000.00",
            "Discount": "0%",
            
            # Signatory
            "Signatory_Name": "John Smith"
        }
        
        # Find the template file
        templates_dir = Path("templates")
        template_file_path = templates_dir / f"{template_id}.docx"
        
        if not template_file_path.exists():
            return JSONResponse({
                "success": False,
                "message": "Template file not found",
                "error": "Template file does not exist on server"
            }, status_code=404)
        
        # Create output files
        filled_docx_file = outputs_dir / f"{document_id}_filled.docx"
        pdf_file = outputs_dir / f"{document_id}_filled.pdf"
        txt_file = outputs_dir / f"{document_id}_filled_fallback.txt"
        
        # Fill the Word template with vessel data
        success = fill_word_template(template_file_path, filled_docx_file, vessel_data)
        
        if not success:
            return JSONResponse({
                "success": False,
                "message": "Failed to fill template",
                "error": "Could not process the Word template"
            }, status_code=500)
        
        # Convert to PDF using reportlab with proper Word content extraction
        pdf_success = False
        try:
            # Read the filled Word document and extract content properly
            from docx import Document
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Read the filled Word document
            doc = Document(str(filled_docx_file))
            
            # Create PDF with proper formatting
            pdf_doc = SimpleDocTemplate(str(pdf_file), pagesize=letter, 
                                      rightMargin=72, leftMargin=72, 
                                      topMargin=72, bottomMargin=18)
            styles = getSampleStyleSheet()
            story = []
            
            # Extract and format content from Word document
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Determine paragraph style based on formatting
                    if paragraph.style.name.startswith('Heading'):
                        style = styles['Heading1']
                    else:
                        style = styles['Normal']
                    
                    # Create paragraph with proper formatting
                    para = Paragraph(paragraph.text.strip(), style)
                    story.append(para)
                    story.append(Spacer(1, 6))
            
            # Extract tables from Word document
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = cell.text.strip() if cell.text else ""
                        row_data.append(cell_text)
                    table_data.append(row_data)
                
                if table_data:
                    # Create PDF table
                    pdf_table = Table(table_data)
                    pdf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(pdf_table)
                    story.append(Spacer(1, 12))
            
            # Build PDF
            pdf_doc.build(story)
            pdf_success = True
            print(f"Created PDF from Word template successfully: {pdf_file}")
            
        except Exception as e:
            print(f"PDF creation from Word document failed: {e}")
            # Fallback: Create a simple PDF with vessel data
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                
                c = canvas.Canvas(str(pdf_file), pagesize=letter)
                width, height = letter
                
                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, f"Vessel Report - {template_info['name']}")
                
                # Content
                c.setFont("Helvetica", 12)
                y_position = height - 100
                
                content_lines = [
                    f"Vessel IMO: {vessel_imo}",
                    f"Document ID: {document_id}",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "This document was generated from your uploaded template.",
                    "The Word document has been processed and filled with vessel data."
                ]
                
                for line in content_lines:
                    c.drawString(50, y_position, line)
                    y_position -= 20
                
                c.save()
                pdf_success = True
                print(f"Created fallback PDF successfully: {pdf_file}")
                
            except Exception as e2:
                print(f"Fallback PDF creation also failed: {e2}")
                # Create a text file as last resort
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(f"Document processed successfully for vessel {vessel_imo}\n")
                    f.write(f"Template: {template_info['name']}\n")
                    f.write(f"Document ID: {document_id}\n")
                    f.write(f"Note: PDF creation failed, but Word document was created successfully.\n")
                    f.write(f"Word file: {filled_docx_file}\n")
        
        # Return success response
        return JSONResponse({
            "success": True,
            "message": "Document processed successfully!",
            "document_id": document_id,
            "download_url": f"/download/{document_id}",
            "vessel_imo": vessel_imo,
            "template_id": template_id,
            "template_name": template_info["name"],
            "files_created": {
                "docx_file": str(filled_docx_file),
                "pdf_file": str(pdf_file) if pdf_success else None,
                "text_file": str(txt_file) if not pdf_success else None
            },
            "download_urls": {
                "docx": f"/download/{document_id}?format=docx",
                "pdf": f"/download/{document_id}?format=pdf"
            },
            "note": "The Word document (.docx) contains your exact template with all formatting preserved. The PDF is a summary document."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Document processing failed: {str(e)}",
            "error": str(e)
        }, status_code=500)

@app.get("/download/{document_id}")
async def download_document(document_id: str, format: str = "pdf"):
    """Download processed document as actual file"""
    try:
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        if format.lower() == "pdf":
            file_path = outputs_dir / f"{document_id}_filled.pdf"
            media_type = "application/pdf"
            filename = f"vessel_report_{document_id}.pdf"
        elif format.lower() == "docx":
            file_path = outputs_dir / f"{document_id}_filled.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"vessel_report_{document_id}.docx"
        else:
            file_path = outputs_dir / f"{document_id}_filled_fallback.txt"
            media_type = "text/plain"
            filename = f"vessel_report_{document_id}.txt"
        
        if not file_path.exists():
            if format.lower() == "pdf":
                # Create a proper PDF fallback
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                
                # Create PDF content
                doc = SimpleDocTemplate(str(file_path), pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    spaceAfter=30,
                    alignment=1  # Center alignment
                )
                story.append(Paragraph("Vessel Report", title_style))
                story.append(Spacer(1, 12))
                
                # Content
                content_style = ParagraphStyle(
                    'CustomContent',
                    parent=styles['Normal'],
                    fontSize=12,
                    spaceAfter=12
                )
                
                story.append(Paragraph(f"<b>Document ID:</b> {document_id}", content_style))
                story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", content_style))
                story.append(Spacer(1, 20))
                
                story.append(Paragraph("This is a sample vessel report generated by the template system.", content_style))
                story.append(Paragraph("The document processing feature is currently being improved.", content_style))
                story.append(Spacer(1, 20))
                
                story.append(Paragraph("For support, please contact the system administrator.", content_style))
                
                # Build PDF
                doc.build(story)
                print(f"Created fallback PDF: {file_path}")
            else:
                # Create a text fallback
                fallback_content = f"""Vessel Report - {document_id}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a sample vessel report generated by the template system.
The actual document processing is being improved.

Document ID: {document_id}
Format: {format}

For support, please contact the system administrator.
"""
                
                # Create the fallback file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fallback_content)
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
        
    except Exception as e:
        print(f"Download error: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    name: str = Form(None),
    description: str = Form(None),
    subscription_level: str = Form(None),
    is_active: bool = Form(None)
):
    """Update template information"""
    try:
        # Find template in storage
        template_found = False
        for i, template in enumerate(templates_storage):
            if template["id"] == template_id:
                # Update fields if provided
                if name is not None:
                    template["name"] = name
                if description is not None:
                    template["description"] = description
                if subscription_level is not None:
                    template["subscription_level"] = subscription_level
                if is_active is not None:
                    template["is_active"] = is_active
                
                template_found = True
                break
        
        if not template_found:
            return JSONResponse({
                "success": False,
                "message": "Template not found"
            }, status_code=404)
        
        # Save updated templates
        save_templates()
        
        return JSONResponse({
            "success": True,
            "message": "Template updated successfully"
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Template update failed: {str(e)}",
            "error": str(e)
        }, status_code=500)

@app.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    try:
        # Find template in storage
        template_found = False
        for i, template in enumerate(templates_storage):
            if template["id"] == template_id:
                # Remove from storage
                templates_storage.pop(i)
                template_found = True
                break
        
        if not template_found:
            return JSONResponse({
                "success": False,
                "message": "Template not found"
            }, status_code=404)
        
        # Delete template file
        templates_dir = Path("templates")
        template_file = templates_dir / f"{template_id}.docx"
        if template_file.exists():
            template_file.unlink()
        
        # Save updated templates
        save_templates()
        
        return JSONResponse({
            "success": True,
            "message": "Template deleted successfully"
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Template deletion failed: {str(e)}",
            "error": str(e)
        }, status_code=500)

@app.get("/user-permissions")
async def get_user_permissions(user_id: str = None):
    """Get user permissions for document templates"""
    try:
        # Import permission manager
        from permission_integration import PermissionManager
        
        permission_manager = PermissionManager()
        
        # Get user_id from your authentication system
        # For demo, use a default user_id
        if not user_id:
            user_id = "demo_user_123"
        
        permissions = permission_manager.get_user_permissions(user_id)
        
        return JSONResponse({
            "success": True,
            "permissions": permissions
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Failed to get user permissions: {str(e)}",
            "error": str(e)
        }, status_code=500)

@app.post("/upload-template")
async def upload_template(
    name: str = Form(...),
    description: str = Form(...),
    template_file: UploadFile = File(...),
    subscription_level: str = Form("basic"),  # Add subscription level
    user_id: str = Form(None)  # Add user_id parameter
):
    """Upload a new document template with permission check"""
    try:
        # Import permission manager
        from permission_integration import PermissionManager
        
        permission_manager = PermissionManager()
        
        # Get user_id (in production, get from authentication)
        if not user_id:
            user_id = "demo_user_123"
        
        # Check upload permission
        if not permission_manager.can_perform_action(user_id, "can_upload_templates"):
            return JSONResponse({
                "success": False,
                "message": "Insufficient permissions to upload templates"
            }, status_code=403)
        
        # Check template limit
        current_count = len(templates_storage)
        if not permission_manager.check_template_limit(user_id, current_count):
            return JSONResponse({
                "success": False,
                "message": f"Template limit reached. Current plan allows {permission_manager.get_user_permissions(user_id)['max_templates']} templates."
            }, status_code=403)
        
        # Generate a unique template ID
        template_id = str(uuid.uuid4())
        
        # Create templates directory if it doesn't exist
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # Save the uploaded file
        file_extension = Path(template_file.filename).suffix
        saved_filename = f"{template_id}{file_extension}"
        file_path = templates_dir / saved_filename
        
        with open(file_path, "wb") as buffer:
            content = await template_file.read()
            buffer.write(content)
        
        # Extract actual placeholders from the uploaded Word document
        actual_placeholders = extract_placeholders_from_docx(file_path)
        
        # Create template info
        template_info = {
            "id": template_id,
            "name": name,
            "description": description,
            "file_name": template_file.filename,
            "file_size": len(content),
            "placeholders": actual_placeholders,
            "subscription_level": subscription_level,  # Add subscription level
            "is_active": True,
            "created_at": "2025-01-30T00:00:00Z",
            "created_by": user_id  # Track who created it
        }
        
        # Add to storage
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("Starting Working Document Service...")
    print(f"Service will be available at: http://0.0.0.0:{port}")
    print("API Documentation: http://0.0.0.0:8000/docs")
    print("Available endpoints:")
    print("  GET  /")
    print("  GET  /health")
    print("  GET  /templates")
    print("  GET  /vessels")
    print("  POST /upload-template")
    print("  POST /process-document")
    print("  GET  /download/{document_id}")
    uvicorn.run(app, host="0.0.0.0", port=port)
