#!/usr/bin/env python3
"""
Permission Integration Module
Connect this to your existing user/permission system
"""

from typing import Dict, Optional
import os

class PermissionManager:
    """Manages user permissions for document templates"""
    
    def __init__(self):
        # These would normally come from your database
        self.plan_limits = {
            "free": {
                "max_templates": 3,
                "max_documents_per_month": 10,
                "can_upload_templates": True,
                "can_edit_templates": True,
                "can_delete_templates": False,
                "can_process_documents": True
            },
            "basic": {
                "max_templates": 10,
                "max_documents_per_month": 50,
                "can_upload_templates": True,
                "can_edit_templates": True,
                "can_delete_templates": True,
                "can_process_documents": True
            },
            "premium": {
                "max_templates": 50,
                "max_documents_per_month": 200,
                "can_upload_templates": True,
                "can_edit_templates": True,
                "can_delete_templates": True,
                "can_process_documents": True
            },
            "enterprise": {
                "max_templates": -1,  # Unlimited
                "max_documents_per_month": -1,  # Unlimited
                "can_upload_templates": True,
                "can_edit_templates": True,
                "can_delete_templates": True,
                "can_process_documents": True
            }
        }
    
    def get_user_permissions(self, user_id: str) -> Dict:
        """
        Get user permissions based on their plan
        In production, this would query your user database
        """
        try:
            # TODO: Replace this with actual database query to your Supabase
            # Example implementation:
            # from supabase import create_client, Client
            # supabase: Client = create_client(url, key)
            # 
            # # Get user subscription
            # subscription = supabase.table('subscribers').select('subscription_tier, subscribed').eq('user_id', user_id).execute()
            # 
            # if subscription.data and subscription.data[0]['subscribed']:
            #     plan = subscription.data[0]['subscription_tier']
            # else:
            #     plan = "free"
            
            # For demo purposes, return premium permissions
            plan = os.getenv("DEMO_USER_PLAN", "premium")
            
            permissions = self.plan_limits.get(plan, self.plan_limits["free"]).copy()
            permissions["plan"] = plan
            permissions["user_id"] = user_id
            
            return permissions
        except Exception as e:
            print(f"Error getting user permissions: {e}")
            # Return free plan as fallback
            permissions = self.plan_limits["free"].copy()
            permissions["plan"] = "free"
            permissions["user_id"] = user_id
            return permissions
    
    def check_template_limit(self, user_id: str, current_count: int) -> bool:
        """Check if user can upload more templates"""
        permissions = self.get_user_permissions(user_id)
        max_templates = permissions["max_templates"]
        
        if max_templates == -1:  # Unlimited
            return True
        
        return current_count < max_templates
    
    def check_document_limit(self, user_id: str, current_month_count: int) -> bool:
        """Check if user can process more documents this month"""
        permissions = self.get_user_permissions(user_id)
        max_documents = permissions["max_documents_per_month"]
        
        if max_documents == -1:  # Unlimited
            return True
        
        return current_month_count < max_documents
    
    def can_perform_action(self, user_id: str, action: str) -> bool:
        """Check if user can perform a specific action"""
        permissions = self.get_user_permissions(user_id)
        return permissions.get(action, False)

# Example integration with your existing system
def integrate_with_your_platform():
    """
    Example of how to integrate with your existing platform
    Replace these functions with your actual database queries
    """
    
    def get_user_from_database(user_id: str):
        """Replace with your actual user database query"""
        # Example: return supabase.table('users').select('*').eq('id', user_id).execute()
        pass
    
    def get_user_subscription(user_id: str):
        """Replace with your actual subscription database query"""
        # Example: return supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()
        pass
    
    def get_user_template_count(user_id: str):
        """Replace with your actual template count query"""
        # Example: return supabase.table('document_templates').select('count').eq('created_by', user_id).execute()
        pass
    
    def get_user_document_count_this_month(user_id: str):
        """Replace with your actual document count query"""
        # Example: return supabase.table('processed_documents').select('count').eq('created_by', user_id).gte('created_at', start_of_month).execute()
        pass

# Usage example in your FastAPI endpoints:
"""
from permission_integration import PermissionManager

permission_manager = PermissionManager()

@app.get("/user-permissions")
async def get_user_permissions(user_id: str = None):
    # Get user_id from your authentication system
    # user_id = get_current_user_id()  # Your auth function
    
    permissions = permission_manager.get_user_permissions(user_id)
    return {"success": True, "permissions": permissions}

@app.post("/upload-template")
async def upload_template(user_id: str = None, ...):
    # Check permissions before allowing upload
    if not permission_manager.can_perform_action(user_id, "can_upload_templates"):
        return JSONResponse({"error": "Insufficient permissions"}, status_code=403)
    
    # Check template limit
    current_count = get_user_template_count(user_id)
    if not permission_manager.check_template_limit(user_id, current_count):
        return JSONResponse({"error": "Template limit reached"}, status_code=403)
    
    # Proceed with upload...
"""
