"""
Proxy management module
"""
from typing import Dict, Optional
import random
import requests
from utils import logger, ProxyTest


class ProxyManager:
    """Manage proxies for accounts"""
    
    def __init__(self):
        self.proxy_cache = {}
        self.proxy_test = ProxyTest()
    
    def assign_proxy(self, account_username: str, proxy: str) -> bool:
        """Assign proxy to account"""
        try:
            # Test proxy before assigning
            if proxy and not self.proxy_test.test_proxy(proxy):
                logger.warning(f"Proxy {proxy} is not working for account {account_username}")
                return False
            
            self.proxy_cache[account_username] = {
                'proxy': proxy,
                'last_used': None,
                'failures': 0
            }
            logger.info(f"Proxy assigned to account {account_username}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning proxy: {e}")
            return False
    
    def get_proxy(self, account_username: str) -> Optional[str]:
        """Get proxy for account"""
        proxy_info = self.proxy_cache.get(account_username)
        if proxy_info:
            return proxy_info['proxy']
        return None
    
    def remove_proxy(self, account_username: str):
        """Remove proxy from account"""
        if account_username in self.proxy_cache:
            del self.proxy_cache[account_username]
            logger.info(f"Proxy removed for account {account_username}")
    
    def mark_proxy_failure(self, account_username: str):
        """Mark proxy as failed"""
        if account_username in self.proxy_cache:
            self.proxy_cache[account_username]['failures'] += 1
            
            # If proxy fails more than 3 times, mark as bad
            if self.proxy_cache[account_username]['failures'] >= 3:
                logger.warning(f"Proxy for {account_username} has failed 3 times")
                self.remove_proxy(account_username)
    
    def test_all_proxies(self) -> Dict:
        """Test all assigned proxies"""
        results = {}
        for username, proxy_info in self.proxy_cache.items():
            proxy = proxy_info['proxy']
            if proxy:
                is_working = self.proxy_test.test_proxy(proxy)
                results[username] = is_working
                if not is_working:
                    self.mark_proxy_failure(username)
        return results
    
    def get_proxy_dict(self, account_username: str) -> Optional[Dict]:
        """Get proxy dict for requests"""
        proxy = self.get_proxy(account_username)
        if proxy:
            return {
                'http': proxy,
                'https': proxy
            }
        return None
    
    def rotate_proxy(self, account_username: str, new_proxy: str) -> bool:
        """Rotate to a new proxy"""
        return self.assign_proxy(account_username, new_proxy)
