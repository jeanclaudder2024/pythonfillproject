import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseIntegration:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("WARNING: Supabase credentials not found. Using fallback data only.")
            self.enabled = False
        else:
            self.enabled = True
            print("SUCCESS: Supabase integration enabled")
    
    def get_vessel_data(self, vessel_imo: str) -> Dict[str, Any]:
        """Get vessel data from Supabase database"""
        if not self.enabled:
            return {}
        
        try:
            # Search for vessel by IMO
            response = requests.get(
                f"{self.supabase_url}/rest/v1/vessels",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "imo": f"eq.{vessel_imo}",
                    "select": "*"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    vessel = data[0]
                    print(f"SUCCESS: Found vessel data for IMO {vessel_imo}: {vessel.get('name', 'Unknown')}")
                    return self._format_vessel_data(vessel)
                else:
                    print(f"WARNING: No vessel found with IMO {vessel_imo}")
                    return {}
            else:
                print(f"ERROR: Error fetching vessel data: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"ERROR: Database error: {str(e)}")
            return {}
    
    def get_vessel_by_id(self, vessel_id: int) -> Dict[str, Any]:
        """Get vessel data by ID"""
        if not self.enabled:
            return {}
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/vessels",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "id": f"eq.{vessel_id}",
                    "select": "*"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    vessel = data[0]
                    print(f"✅ Found vessel data for ID {vessel_id}: {vessel.get('name', 'Unknown')}")
                    return self._format_vessel_data(vessel)
                else:
                    print(f"WARNING:  No vessel found with ID {vessel_id}")
                    return {}
            else:
                print(f"ERROR: Error fetching vessel data: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"ERROR: Database error: {str(e)}")
            return {}
    
    def get_port_data(self, port_id: int) -> Dict[str, Any]:
        """Get port data by ID"""
        if not self.enabled:
            return {}
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/ports",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "id": f"eq.{port_id}",
                    "select": "*"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    port = data[0]
                    print(f"✅ Found port data for ID {port_id}: {port.get('name', 'Unknown')}")
                    return self._format_port_data(port)
                else:
                    print(f"WARNING:  No port found with ID {port_id}")
                    return {}
            else:
                print(f"ERROR: Error fetching port data: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"ERROR: Database error: {str(e)}")
            return {}
    
    def get_company_data(self, company_id: int) -> Dict[str, Any]:
        """Get company data by ID"""
        if not self.enabled:
            return {}
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/companies",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "id": f"eq.{company_id}",
                    "select": "*"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    company = data[0]
                    print(f"✅ Found company data for ID {company_id}: {company.get('name', 'Unknown')}")
                    return self._format_company_data(company)
                else:
                    print(f"WARNING:  No company found with ID {company_id}")
                    return {}
            else:
                print(f"ERROR: Error fetching company data: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"ERROR: Database error: {str(e)}")
            return {}
    
    def _format_vessel_data(self, vessel: Dict[str, Any]) -> Dict[str, Any]:
        """Format vessel data for placeholder replacement"""
        return {
            # Basic vessel info
            'vessel_name': vessel.get('name', ''),
            'ship_name': vessel.get('name', ''),
            'imo': vessel.get('imo', ''),
            'imo_number': vessel.get('imo', ''),
            'mmsi': vessel.get('mmsi', ''),
            'callsign': vessel.get('callsign', ''),
            
            # Technical specifications
            'vessel_type': vessel.get('vessel_type', ''),
            'ship_type': vessel.get('vessel_type', ''),
            'length': vessel.get('length', ''),
            'width': vessel.get('width', ''),
            'beam': vessel.get('beam', ''),
            'draught': vessel.get('draught', ''),
            'draft': vessel.get('draught', ''),
            'deadweight': vessel.get('deadweight', ''),
            'tonnage': vessel.get('deadweight', ''),
            'gross_tonnage': vessel.get('gross_tonnage', ''),
            'net_tonnage': vessel.get('net_tonnage', ''),
            'speed': vessel.get('speed', ''),
            'max_speed': vessel.get('speed', ''),
            
            # Operational info
            'flag': vessel.get('flag', ''),
            'flag_state': vessel.get('flag', ''),
            'built': vessel.get('built', ''),
            'year': vessel.get('built', ''),
            'year_built': vessel.get('built', ''),
            
            # Ownership
            'owner': vessel.get('owner_name', ''),
            'owner_name': vessel.get('owner_name', ''),
            'operator': vessel.get('operator_name', ''),
            'operator_name': vessel.get('operator_name', ''),
            'company': vessel.get('owner_name', ''),
            
            # Cargo info
            'cargo_type': vessel.get('cargo_type', ''),
            'cargo_quantity': vessel.get('cargo_quantity', ''),
            'oil_type': vessel.get('oil_type', ''),
            
            # Current status
            'status': vessel.get('status', ''),
            'current_port': vessel.get('departure_port_name', ''),
            'port': vessel.get('departure_port_name', ''),
            'departure_port': vessel.get('departure_port_name', ''),
            'destination_port': vessel.get('destination_port_name', ''),
            
            # Dates
            'departure_date': vessel.get('departure_date', ''),
            'arrival_date': vessel.get('arrival_date', ''),
            'eta': vessel.get('eta', ''),
        }
    
    def _format_port_data(self, port: Dict[str, Any]) -> Dict[str, Any]:
        """Format port data for placeholder replacement"""
        return {
            'port_name': port.get('name', ''),
            'port': port.get('name', ''),
            'port_country': port.get('country', ''),
            'port_city': port.get('city', ''),
            'port_address': port.get('address', ''),
            'port_phone': port.get('phone', ''),
            'port_email': port.get('email', ''),
            'port_website': port.get('website', ''),
            'port_capacity': port.get('capacity', ''),
            'port_type': port.get('port_type', ''),
        }
    
    def _format_company_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Format company data for placeholder replacement"""
        return {
            'company_name': company.get('name', ''),
            'company': company.get('name', ''),
            'company_country': company.get('country', ''),
            'company_city': company.get('city', ''),
            'company_address': company.get('address', ''),
            'company_phone': company.get('phone', ''),
            'company_email': company.get('email', ''),
            'company_website': company.get('website', ''),
            'company_type': company.get('type', ''),
        }
    
    def get_all_vessels(self, limit: int = 100) -> list:
        """Get all vessels from database"""
        if not self.enabled:
            return []
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/vessels",
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "select": "id,name,imo,mmsi,vessel_type,flag",
                    "limit": limit
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"ERROR: Error fetching vessels: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"ERROR: Database error: {str(e)}")
            return []

# Test the integration
if __name__ == "__main__":
    db = SupabaseIntegration()
    
    if db.enabled:
        print("Testing database integration...")
        
        # Test getting all vessels
        vessels = db.get_all_vessels(5)
        print(f"Found {len(vessels)} vessels")
        
        if vessels:
            # Test getting specific vessel data
            test_imo = vessels[0].get('imo')
            if test_imo:
                vessel_data = db.get_vessel_data(test_imo)
                print(f"Vessel data for IMO {test_imo}:")
                for key, value in vessel_data.items():
                    if value:
                        print(f"  {key}: {value}")
    else:
        print("Database integration disabled - check your .env file")
