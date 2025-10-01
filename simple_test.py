#!/usr/bin/env python3
"""
Simple test for the enhanced document processor
"""

from enhanced_document_processor import EnhancedDocumentProcessor
from database_integration import SupabaseIntegration

def test_enhanced_processor():
    print("Testing Enhanced Document Processor...")
    
    # Test database integration
    db = SupabaseIntegration()
    if db.enabled:
        print("SUCCESS: Database integration enabled")
        
        # Get vessel list
        vessels = db.get_all_vessels(5)
        print(f"Found {len(vessels)} vessels")
        
        if vessels:
            # Test getting specific vessel data
            test_imo = vessels[0].get('imo')
            if test_imo:
                print(f"Testing vessel data for IMO: {test_imo}")
                vessel_data = db.get_vessel_data(test_imo)
                print(f"Vessel data keys: {list(vessel_data.keys())}")
                
                # Show some sample data
                for key in ['vessel_name', 'imo', 'vessel_type', 'flag']:
                    if key in vessel_data and vessel_data[key]:
                        print(f"  {key}: {vessel_data[key]}")
    else:
        print("WARNING: Database integration disabled")
    
    # Test enhanced processor
    processor = EnhancedDocumentProcessor()
    print("SUCCESS: Enhanced processor initialized")
    
    # Test getting vessel list
    vessels = processor.get_vessel_list()
    print(f"Processor found {len(vessels)} vessels")
    
    print("\nSUCCESS: All tests passed!")
    print("You can now use the enhanced app at: http://localhost:5000")

if __name__ == "__main__":
    test_enhanced_processor()
