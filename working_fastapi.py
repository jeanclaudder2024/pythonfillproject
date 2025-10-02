#!/usr/bin/env python3
"""
Working FastAPI service with all endpoints - CLEAN VERSION
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

@app.get("/")
async def root():
    return {"message": "Working Document Service is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "document-processing"}

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
    """Get user permissions (simplified version)"""
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("Starting Working Document Service...")
    print("Available endpoints:")
    print("  GET  /")
    print("  GET  /health")
    print("  GET  /templates")
    print("  GET  /vessels")
    print("  GET  /user-permissions")
    uvicorn.run(app, host="0.0.0.0", port=port)
