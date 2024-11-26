from typing import Dict, Optional, Any, List
from app.clients.supabase import SupabaseClient

class OperatingHoursDB:
    TABLE_NAME = 'operating_hours'

    def __init__(self):
        self.supabase = SupabaseClient()

    def get_hours(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Get operating hours for a restaurant."""
        try:
            response = self.supabase.client.table(self.TABLE_NAME)\
                .select("*")\
                .eq('restaurant_id', restaurant_id)\
                .execute()
            
            if response.data:
                print("✅ Found operating hours")
                return response.data[0]
            return None
        except Exception as e:
            print(f"❌ Failed to get operating hours: {str(e)}")
            return None

    def update_hours(self, restaurant_id: str, time_open: str, time_closed: str, is_open: bool) -> bool:
        """Update or create operating hours for a restaurant."""
        try:
            print(f"🔄 Updating operating hours for restaurant: {restaurant_id}")
            data = {
                'restaurant_id': restaurant_id,
                'time_open': time_open,
                'time_closed': time_closed,
                "is_open": is_open,
                'is_hours_verified': True,  # Set to True since we're getting actual hours
                'is_consenting': True  # Assuming consent when hours are provided
            }
            
            # Check if record exists
            existing = self.get_hours(restaurant_id)
            
            if existing:
                # Update existing record
                self.supabase.client.table(self.TABLE_NAME)\
                    .update(data)\
                    .eq('id', existing['id'])\
                    .execute()
                print("✅ Operating hours updated successfully")
            else:
                # Create new record
                self.supabase.client.table(self.TABLE_NAME)\
                    .insert(data)\
                    .execute()
                print("✅ Operating hours created successfully")
            
            return True
        except Exception as e:
            print(f"❌ Failed to update operating hours: {str(e)}")
            return False

    def mark_hours_unverified(self, restaurant_id: str) -> bool:
        """Mark a restaurant's hours as unverified."""
        try:
            print(f"🔄 Marking hours as unverified for restaurant: {restaurant_id}")
            existing = self.get_hours(restaurant_id)
            
            data = {
                'restaurant_id': restaurant_id,
                'is_hours_verified': False
            }
            
            if existing:
                # Update existing record
                self.supabase.client.table(self.TABLE_NAME)\
                    .update(data)\
                    .eq('id', existing['id'])\
                    .execute()
            else:
                # Create new record
                self.supabase.client.table(self.TABLE_NAME)\
                    .insert(data)\
                    .execute()
            
            print("✅ Hours marked as unverified")
            return True
        except Exception as e:
            print(f"❌ Failed to mark hours as unverified: {str(e)}")
            return False

    def update_consent(self, restaurant_id: str, is_consenting: bool) -> bool:
        """Update the consent status for a restaurant."""
        try:
            print(f"🔄 Updating consent status for restaurant: {restaurant_id}")
            existing = self.get_hours(restaurant_id)
            
            data = {
                'restaurant_id': restaurant_id,
                'is_consenting': is_consenting
            }
            
            if existing:
                # Update existing record
                self.supabase.client.table(self.TABLE_NAME)\
                    .update(data)\
                    .eq('id', existing['id'])\
                    .execute()
            else:
                # Create new record
                self.supabase.client.table(self.TABLE_NAME)\
                    .insert(data)\
                    .execute()
            
            print(f"✅ Consent status updated to: {is_consenting}")
            return True
        except Exception as e:
            print(f"❌ Failed to update consent status: {str(e)}")
            return False

    def get_hours_bulk(self, restaurant_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get operating hours for multiple restaurants in one query."""
        try:
            response = self.supabase.client.table(self.TABLE_NAME)\
                .select("*")\
                .in_('restaurant_id', restaurant_ids)\
                .execute()
            
            # Create a map of restaurant_id to hours
            hours_map = {}
            for hours in response.data:
                hours_map[hours['restaurant_id']] = hours
            
            return hours_map
        except Exception as e:
            print(f"❌ Failed to get bulk operating hours: {str(e)}")
            return {}
