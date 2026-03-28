"""
Account management module
"""
from typing import Dict, List, Optional
import json
from datetime import datetime
from utils import DataManager, logger


class AccountManager:
    """Manage social media accounts"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.accounts = self.data_manager.load_accounts()
        self.status_cache = {}
    
    def add_account(self, account_data: Dict) -> bool:
        """Add new account"""
        try:
            username = account_data.get('username')
            if not username:
                logger.error("Username is required")
                return False
            
            # Validate required fields
            required_fields = ['username', 'platform']
            for field in required_fields:
                if field not in account_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Initialize account
            account = {
                'username': username,
                'platform': account_data['platform'],
                'auth_type': account_data.get('auth_type', 'cookie'),
                'auth_data': account_data.get('auth_data', {}),
                'proxy': account_data.get('proxy'),
                'status': 'active',
                'last_active': None,
                'created_at': datetime.now().isoformat(),
                'comments_made': 0,
                'errors': 0
            }
            
            # Check if account exists
            if username in self.accounts:
                logger.warning(f"Account {username} already exists")
                return False
            
            self.accounts[username] = account
            self.data_manager.save_accounts(self.accounts)
            logger.info(f"Account {username} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            return False
    
    def update_account(self, username: str, update_data: Dict) -> bool:
        """Update account information"""
        try:
            if username not in self.accounts:
                logger.error(f"Account {username} not found")
                return False
            
            # Update fields
            for key, value in update_data.items():
                if key in ['proxy', 'status', 'auth_data']:
                    self.accounts[username][key] = value
                elif key in ['comments_made', 'errors']:
                    self.accounts[username][key] = value
                elif key == 'last_active':
                    self.accounts[username][key] = datetime.now().isoformat()
            
            self.data_manager.save_accounts(self.accounts)
            logger.info(f"Account {username} updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return False
    
    def delete_account(self, username: str) -> bool:
        """Delete account"""
        try:
            if username in self.accounts:
                del self.accounts[username]
                self.data_manager.save_accounts(self.accounts)
                logger.info(f"Account {username} deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            return False
    
    def get_account(self, username: str) -> Optional[Dict]:
        """Get account by username"""
        return self.accounts.get(username)
    
    def get_all_accounts(self) -> Dict:
        """Get all accounts"""
        return self.accounts
    
    def get_active_accounts(self) -> List[Dict]:
        """Get active accounts"""
        return [
            acc for acc in self.accounts.values() 
            if acc['status'] == 'active'
        ]
    
    def update_status(self, username: str, status: str, error: str = None):
        """Update account status"""
        if username in self.accounts:
            self.accounts[username]['status'] = status
            if error:
                self.accounts[username]['last_error'] = error
                self.accounts[username]['errors'] += 1
            self.data_manager.save_accounts(self.accounts)
    
    def increment_comments(self, username: str):
        """Increment comment count for account"""
        if username in self.accounts:
            self.accounts[username]['comments_made'] += 1
            self.accounts[username]['last_active'] = datetime.now().isoformat()
            self.data_manager.save_accounts(self.accounts)
    
    def get_statistics(self) -> Dict:
        """Get account statistics"""
        stats = {
            'total': len(self.accounts),
            'active': 0,
            'error': 0,
            'checkpoint': 0,
            'total_comments': 0
        }
        
        for acc in self.accounts.values():
            status = acc['status']
            if status == 'active':
                stats['active'] += 1
            elif status == 'error':
                stats['error'] += 1
            elif status == 'checkpoint':
                stats['checkpoint'] += 1
            
            stats['total_comments'] += acc.get('comments_made', 0)
        
        return stats
