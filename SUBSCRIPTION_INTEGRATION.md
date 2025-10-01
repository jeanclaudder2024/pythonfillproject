# Template System - Subscription Integration Guide

## **🎯 Overview**
This guide shows how to integrate the document template system with your existing subscription-based permission system.

## **✅ What's Been Implemented**

### **1. Database Schema Updates**
- Added `subscription_level` field to `document_templates` table
- Updated RLS policies to filter templates based on user subscription
- Templates now support: `basic`, `premium`, `enterprise` levels

### **2. FastAPI Integration**
- Added subscription level parameter to template upload
- Enhanced permission system to work with your existing plans
- Template filtering based on user subscription level

### **3. React Components**
- Added subscription level selector in admin panel
- Template cards now display subscription level badges
- Vessel document downloader filters templates by user plan
- Permission-based UI controls

## **🔧 How It Works**

### **Template Access Control**
```
Basic Plan Users:
├── Can access: Basic templates only
├── Can upload: Basic templates only
└── Can edit/delete: Their own templates

Premium Plan Users:
├── Can access: Basic + Premium templates
├── Can upload: Basic + Premium templates
└── Can edit/delete: Their own templates

Enterprise Plan Users:
├── Can access: All templates (Basic + Premium + Enterprise)
├── Can upload: All template levels
└── Can edit/delete: Their own templates
```

### **Database RLS Policies**
The system uses Row Level Security to automatically filter templates:

```sql
-- Users can only see templates they have access to
CREATE POLICY "Users can view templates based on subscription" 
ON document_templates FOR SELECT USING (
    is_active = true AND (
        subscription_level = 'basic' OR
        (subscription_level = 'premium' AND user_has_premium_access) OR
        (subscription_level = 'enterprise' AND user_has_enterprise_access)
    )
);
```

## **🚀 Integration Steps**

### **Step 1: Connect to Your User System**

Update `autofill/permission_integration.py`:

```python
def get_user_permissions(self, user_id: str) -> Dict:
    # Replace with your actual Supabase connection
    from supabase import create_client, Client
    
    supabase: Client = create_client(
        url="your_supabase_url",
        key="your_supabase_key"
    )
    
    # Get user subscription
    subscription = supabase.table('subscribers').select(
        'subscription_tier, subscribed'
    ).eq('user_id', user_id).execute()
    
    if subscription.data and subscription.data[0]['subscribed']:
        plan = subscription.data[0]['subscription_tier']
    else:
        plan = "free"
    
    permissions = self.plan_limits.get(plan, self.plan_limits["free"]).copy()
    permissions["plan"] = plan
    permissions["user_id"] = user_id
    
    return permissions
```

### **Step 2: Update React Auth Context**

In your React app, get the user's subscription level:

```typescript
// In your auth context or component
const [userPlan, setUserPlan] = useState<string>('basic');

useEffect(() => {
  // Get user subscription from your auth system
  const getUserSubscription = async () => {
    const { data } = await supabase
      .from('subscribers')
      .select('subscription_tier')
      .eq('user_id', user.id)
      .single();
    
    if (data?.subscription_tier) {
      setUserPlan(data.subscription_tier);
    }
  };
  
  getUserSubscription();
}, [user]);
```

### **Step 3: Pass User Plan to Components**

Update `VesselDocumentDownloader` to use real user data:

```typescript
// Pass user plan as prop
<VesselDocumentDownloader 
  vesselImo={vessel.imo} 
  vesselName={vessel.name}
  userPlan={userPlan} // Add this prop
/>
```

## **📊 Template Management by Plan**

### **Admin Panel Features**
- **Upload Templates**: Select subscription level when uploading
- **View Templates**: See all templates with subscription level badges
- **Edit Templates**: Modify name, description, and subscription level
- **Delete Templates**: Remove templates with confirmation
- **Permission Checks**: Buttons only show if user has permission

### **User Experience**
- **Template Filtering**: Users only see templates they can access
- **Subscription Badges**: Clear indication of template access level
- **Upgrade Prompts**: Show upgrade options for premium/enterprise templates
- **Usage Limits**: Enforce template limits based on plan

## **🎨 UI Features**

### **Template Cards**
```
┌─────────────────────────────────────┐
│ 📄 ICPO Template              [Premium] │
│ ICPO document for vessel trading    │
│ [Active] [Premium] [👁️] [✏️] [🗑️]    │
│                                     │
│ Placeholders: {vessel_name}, {imo}  │
│ Test with Vessel: [Select Vessel ▼] │
└─────────────────────────────────────┘
```

### **Upload Form**
```
┌─────────────────────────────────────┐
│ Upload New Template                 │
│                                     │
│ Template Name: [ICPO Template    ]  │
│ Description:   [ICPO document...]   │
│ Subscription:  [Premium        ▼]   │
│ File:          [Choose File     ]   │
│                                     │
│ [Upload Template] [Cancel]          │
└─────────────────────────────────────┘
```

## **🔐 Security Features**

### **Database Level**
- **RLS Policies**: Automatic filtering at database level
- **Subscription Checks**: Verify user subscription before access
- **Admin Override**: Admins can access all templates

### **API Level**
- **Permission Validation**: Check permissions before operations
- **Template Limits**: Enforce plan-based template limits
- **User Tracking**: Track who created/modified templates

### **Frontend Level**
- **UI Hiding**: Hide features user can't access
- **Upgrade Prompts**: Show upgrade options for premium features
- **Permission Indicators**: Clear visual feedback on access levels

## **📈 Usage Tracking**

### **Template Limits by Plan**
```javascript
const planLimits = {
  free: { max_templates: 3, max_documents_per_month: 10 },
  basic: { max_templates: 10, max_documents_per_month: 50 },
  premium: { max_templates: 50, max_documents_per_month: 200 },
  enterprise: { max_templates: -1, max_documents_per_month: -1 } // Unlimited
};
```

### **Usage Monitoring**
- Track template uploads per user
- Monitor document generation per month
- Enforce limits based on subscription
- Show usage statistics in admin panel

## **🔄 Migration Steps**

### **1. Update Database**
```bash
# Run the migration
supabase db push
```

### **2. Update Existing Templates**
```sql
-- Set default subscription level for existing templates
UPDATE document_templates 
SET subscription_level = 'basic' 
WHERE subscription_level IS NULL;
```

### **3. Test Integration**
1. Upload templates with different subscription levels
2. Test access with different user plans
3. Verify RLS policies work correctly
4. Test template limits and permissions

## **🎯 Next Steps**

1. **Connect Real Auth**: Replace demo user system with your auth
2. **Add Usage Tracking**: Monitor template and document usage
3. **Implement Billing**: Connect to your billing system
4. **Add Analytics**: Track template usage and performance
5. **Admin Dashboard**: Add admin controls for template management

## **🛠️ Customization**

### **Add New Subscription Levels**
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

### **Custom Template Categories**
```sql
-- Add category field to templates
ALTER TABLE document_templates 
ADD COLUMN category VARCHAR(50) DEFAULT 'general';
```

The template system is now fully integrated with your subscription-based permission system! 🎉
