from __future__ import annotations
import logging
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from app.clients.supabase import SupabaseClient

logger = logging.getLogger(__name__)

class User(BaseModel):
    """User model with search credits and premium status"""
    user_id: str
    id: int
    created_at: datetime
    search_credits: int = 0  # smallint in db
    is_premium: bool = False

class UserDB:
    TABLE_NAME = "user_table"

    def __init__(self):
        self.supabase = SupabaseClient()

    async def create_user(self, user_data: Dict):
        try:
            # Add timestamps
            user_data["created_at"] = "now()"
            user_data["updated_at"] = "now()"
            # Ensure search_credits is set
            if "search_credits" not in user_data:
                user_data["search_credits"] = 3
            
            response =  self.supabase.client.table(self.TABLE_NAME).upsert(user_data).execute()
            logger.info(f"✅ User created/updated successfully: {user_data['user_id']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create user: {str(e)}")
            return False

    async def get_user(self, user_id: str) -> Optional[User]:
        try:
            response = self.supabase.client.table(self.TABLE_NAME).select("*").eq('user_id', user_id).execute()
            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user: {str(e)}")
            return None

    async def is_search_permitted(self, user_id: str) -> bool:
        try:
            user = await self.get_user(user_id)
            logger.info(f"🔍 Checking search credits for user {user_id}")
            logger.info(f"✅ User info: {user}")
            
            if not user:
                logger.error(f"❌ User {user_id} not found")
                return False
                
            if user.is_premium:
                logger.info(f"✅ User {user_id} is premium")
                return True
                
            if user.search_credits > 0:
                logger.info(f"✅ User {user_id} has {user.search_credits} search credits")
                self.supabase.client.table(self.TABLE_NAME).update({
                    'search_credits': user.search_credits - 1,
                    'updated_at': 'now()',
                    'is_premium': user.is_premium
                }).eq('user_id', user_id).execute()
                return True
                
            logger.info(f"❌ User {user_id} does not have enough search credits")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check search permission: {str(e)}", exc_info=True)
            return False