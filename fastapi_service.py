#!/usr/bin/env python3
"""
FastAPI service for document processing
This service handles document processing requests from the React platform
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import json
import asyncio
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

# Import our existing modules
from enhanced_document_processor import EnhancedDocumentProcessor
from database_integration import SupabaseIntegration

app = FastAPI(
    title="Document Processing Service",
    description="Advanced document processing service for vessel data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
processor = EnhancedDocumentProcessor()
db_integration = SupabaseIntegration()

# Pydantic models
class DocumentProcessingRequest(BaseModel):
    template_id: str
    vessel_imo: str
    user_id: Optional[str] = None

class DocumentProcessingResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None

class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    placeholders: List[str]
    placeholder_mappings: Dict[str, str]
    is_active: bool
    created_at: str

class VesselInfo(BaseModel):
    id: str
    name: str
    imo: str
    vessel_type: Optional[str] = None
    flag: Optional[str] = None

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Document Processing Service is running",
        "version": "1.0.0",
        "database_connected": db_integration.enabled,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected" if db_integration.enabled else "disconnected",
        "processor": "ready",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/templates", response_model=List[TemplateInfo])
async def get_templates():
    """Get all active document templates"""
    try:
        if not db_integration.enabled:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # This would fetch from your database - for now, return sample data
        templates = [
            TemplateInfo(
                id="template-1",
                name="Vessel Report Template",
                description="Standard vessel report with basic information",
                placeholders=["vessel_name", "imo", "vessel_type", "flag", "owner"],
                placeholder_mappings={
                    "vessel_name": "vessels.name",
                    "imo": "vessels.imo",
                    "vessel_type": "vessels.vessel_type",
                    "flag": "vessels.flag",
                    "owner": "vessels.owner_name"
                },
                is_active=True,
                created_at=datetime.now().isoformat()
            )
        ]
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@app.get("/vessels", response_model=List[VesselInfo])
async def get_vessels():
    """Get all available vessels"""
    try:
        if not db_integration.enabled:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        vessels = db_integration.get_all_vessels(limit=100)
        vessel_list = []
        
        for vessel in vessels:
            vessel_list.append(VesselInfo(
                id=str(vessel.get('id', '')),
                name=vessel.get('name', 'Unknown'),
                imo=vessel.get('imo', ''),
                vessel_type=vessel.get('vessel_type'),
                flag=vessel.get('flag')
            ))
        
        return vessel_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vessels: {str(e)}")

@app.post("/process-document", response_model=DocumentProcessingResponse)
async def process_document(
    background_tasks: BackgroundTasks,
    template_id: str = Form(...),
    vessel_imo: str = Form(...),
    template_file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """Process a document template with vessel data"""
    try:
        # Validate inputs
        if not template_file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Only .docx files are supported")
        
        if not vessel_imo:
            raise HTTPException(status_code=400, detail="Vessel IMO is required")
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Create temporary directory for processing
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Save uploaded template
            template_path = temp_dir / f"{document_id}_template.docx"
            with open(template_path, "wb") as buffer:
                shutil.copyfileobj(template_file.file, buffer)
            
            # Process the document
            word_output, pdf_output = processor.process_document(
                str(template_path), 
                vessel_imo, 
                document_id
            )
            
            # Move processed files to outputs directory
            outputs_dir = Path("outputs")
            outputs_dir.mkdir(exist_ok=True)
            
            final_word_path = outputs_dir / f"{document_id}_processed.docx"
            final_pdf_path = outputs_dir / f"{document_id}_processed.pdf"
            
            shutil.move(word_output, final_word_path)
            if os.path.exists(pdf_output):
                shutil.move(pdf_output, final_pdf_path)
            
            # Create download URLs
            download_url = f"/download/{document_id}"
            
            return DocumentProcessingResponse(
                success=True,
                message="Document processed successfully",
                document_id=document_id,
                download_url=download_url
            )
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        return DocumentProcessingResponse(
            success=False,
            message="Document processing failed",
            error=str(e)
        )

@app.get("/download/{document_id}")
async def download_document(document_id: str, format: str = "pdf"):
    """Download processed document"""
    try:
        outputs_dir = Path("outputs")
        
        if format.lower() == "pdf":
            file_path = outputs_dir / f"{document_id}_processed.pdf"
            media_type = "application/pdf"
            filename = f"processed_document_{document_id}.pdf"
        else:
            file_path = outputs_dir / f"{document_id}_processed.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"processed_document_{document_id}.docx"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/vessel/{vessel_imo}")
async def get_vessel_data(vessel_imo: str):
    """Get specific vessel data"""
    try:
        if not db_integration.enabled:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        vessel_data = db_integration.get_vessel_data(vessel_imo)
        
        if not vessel_data:
            raise HTTPException(status_code=404, detail="Vessel not found")
        
        return vessel_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vessel data: {str(e)}")

@app.post("/upload-template")
async def upload_template(
    name: str = Form(...),
    description: str = Form(...),
    template_file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """Upload a new document template"""
    try:
        if not template_file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Only .docx files are supported")
        
        # Here you would save the template to your database
        # For now, we'll just return success
        
        return {
            "success": True,
            "message": "Template uploaded successfully",
            "template_id": str(uuid.uuid4()),
            "filename": template_file.filename,
            "size": template_file.size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template upload failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting Document Processing Service...")
    print("Database integration:", "Enabled" if db_integration.enabled else "Disabled")
    print("Service will be available at: http://localhost:8000")
    uvicorn.run("fastapi_service:app", host="0.0.0.0", port=8000, reload=True)
