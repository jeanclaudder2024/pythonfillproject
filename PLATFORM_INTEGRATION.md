# Platform Integration Guide

## **🎯 Overview**
This guide shows how to integrate the document template system with your existing platform's permission system.

## **📋 Features Added**

### **✅ Template Management**
- **Edit Templates**: Change name, description, and active status
- **Delete Templates**: Remove templates with confirmation dialog
- **Permission-Based Access**: Buttons only show if user has permissions

### **✅ Permission System**
- **Plan-Based Limits**: Different limits for free, basic, premium, enterprise plans
- **Action Permissions**: Control who can upload, edit, delete templates
- **Usage Tracking**: Monitor template count and document processing limits

## **🔧 Integration Steps**

### **1. Connect to Your User System**

Replace the demo user system in `permission_integration.py`:

```python
def get_user_from_database(user_id: str):
    """Replace with your actual user database query"""
    # Example for Supabase:
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    return response.data[0] if response.data else None

def get_user_subscription(user_id: str):
    """Replace with your actual subscription database query"""
    # Example for Supabase:
    response = supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()
    return response.data[0] if response.data else None
```

### **2. Update FastAPI Authentication**

In `working_fastapi.py`, replace the demo user_id with your authentication:

```python
@app.post("/upload-template")
async def upload_template(
    name: str = Form(...),
    description: str = Form(...),
    template_file: UploadFile = File(...),
    authorization: str = Header(None)  # Get from your auth system
):
    # Get user_id from your authentication system
    user_id = get_current_user_id(authorization)  # Your auth function
    
    # Rest of the function...
```

### **3. Connect to Your Database**

Update the template storage to use your database instead of JSON files:

```python
# In working_fastapi.py, replace templates_storage with database calls
async def save_template_to_database(template_info):
    """Save template to your database"""
    # Example for Supabase:
    response = supabase.table('document_templates').insert(template_info).execute()
    return response.data

async def get_templates_from_database():
    """Get templates from your database"""
    # Example for Supabase:
    response = supabase.table('document_templates').select('*').execute()
    return response.data
```

## **📊 Permission Plans**

### **Free Plan**
- 3 templates max
- 10 documents per month
- Can upload and edit templates
- Cannot delete templates

### **Basic Plan**
- 10 templates max
- 50 documents per month
- Full template management

### **Premium Plan**
- 50 templates max
- 200 documents per month
- Full template management

### **Enterprise Plan**
- Unlimited templates
- Unlimited documents
- Full template management

## **🎨 UI Features**

### **Template Cards**
- **View Button**: See template details and placeholders
- **Edit Button**: Modify template name, description, status (if permitted)
- **Delete Button**: Remove template with confirmation (if permitted)
- **Status Badge**: Shows if template is active/inactive

### **Permission Indicators**
- **Plan Display**: Shows current plan and usage
- **Disabled Buttons**: Upload button disabled when limit reached
- **Hidden Actions**: Edit/delete buttons hidden if no permission

### **Edit Dialog**
- **Name Field**: Change template name
- **Description Field**: Update template description
- **Active Toggle**: Enable/disable template
- **Save/Cancel**: Apply changes or cancel

### **Delete Confirmation**
- **Alert Dialog**: Confirms deletion action
- **Template Name**: Shows which template will be deleted
- **Cancel/Delete**: Safe deletion with confirmation

## **🔐 Security Features**

### **Permission Checks**
- **Upload Permission**: Check before allowing template upload
- **Edit Permission**: Verify before showing edit button
- **Delete Permission**: Confirm before allowing deletion
- **Template Limits**: Enforce plan-based template limits

### **User Tracking**
- **Created By**: Track who created each template
- **Usage Monitoring**: Monitor document processing per user
- **Plan Validation**: Verify user's current plan

## **🚀 Deployment Notes**

### **Environment Variables**
```bash
# Set user plan for demo
DEMO_USER_PLAN=premium  # free, basic, premium, enterprise

# Your database connection
DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### **Database Schema**
Make sure your database has these tables:
- `users` - User information
- `subscriptions` - User subscription plans
- `document_templates` - Template storage
- `processed_documents` - Document processing history

## **📝 Next Steps**

1. **Connect Authentication**: Replace demo user system with your auth
2. **Database Integration**: Connect to your actual database
3. **Plan Management**: Integrate with your subscription system
4. **Usage Tracking**: Monitor actual usage for billing
5. **Admin Panel**: Add admin controls for plan management

## **🛠️ Customization**

### **Add New Permissions**
```python
# In permission_integration.py
"can_share_templates": True,
"can_export_templates": True,
"can_import_templates": True,
```

### **Custom Plan Limits**
```python
# In permission_integration.py
"custom_plan": {
    "max_templates": 25,
    "max_documents_per_month": 100,
    "can_upload_templates": True,
    "can_edit_templates": True,
    "can_delete_templates": True,
    "can_process_documents": True
}
```

The system is now ready to integrate with your platform's permission system! 🎉
