from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="Document Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Document Service is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/templates")
async def get_templates():
    return []

@app.get("/vessels")
async def get_vessels():
    return [
        {
            "id": "1",
            "name": "Petroleum Express 529",
            "imo": "IMO1861018",
            "vessel_type": "Crude Oil Tanker",
            "flag": "Malta"
        }
    ]

@app.get("/user-permissions")
async def get_user_permissions():
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
    uvicorn.run(app, host="0.0.0.0", port=port)
