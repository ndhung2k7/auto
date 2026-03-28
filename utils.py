"""
Utility functions for auto comment tool
"""
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/activity.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = 'config/settings.json'):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "default_delay": {
                "between_comments": 200,
                "between_accounts": 60,
                "random_range": 30
            },
            "scheduler": {
                "enabled": False,
                "schedule_time": "09:00",
                "daily_comments": 50
            },
            "anti_detect": {
                "random_user_agent": True,
                "random_mouse_movement": True,
                "human_behavior_delay": True
            },
            "retry": {
                "max_attempts": 3,
                "delay_on_fail": 120
            },
            "log_level": "INFO"
        }
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value


class DataManager:
    """Manage data files (accounts, tasks)"""
    
    def __init__(self):
        self.accounts_file = 'accounts.json'
        self.tasks_file = 'tasks.json'
        self.ensure_files()
    
    def ensure_files(self):
        """Ensure data files exist"""
        for file in [self.accounts_file, self.tasks_file]:
            if not Path(file).exists():
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
    
    def load_accounts(self) -> Dict:
        """Load accounts from file"""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            return {}
    
    def save_accounts(self, accounts: Dict):
        """Save accounts to file"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, indent=2, ensure_ascii=False)
            logger.info("Accounts saved")
        except Exception as e:
            logger.error(f"Error saving accounts: {e}")
    
    def load_tasks(self) -> Dict:
        """Load tasks from file"""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            return {}
    
    def save_tasks(self, tasks: Dict):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            logger.info("Tasks saved")
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")


def random_delay(base_delay: int, random_range: int = 30) -> int:
    """Generate random delay"""
    return base_delay + random.randint(0, random_range)


def get_random_user_agent() -> str:
    """Get random user agent"""
    try:
        ua = UserAgent()
        return ua.random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def human_like_delay(min_seconds: float = 1, max_seconds: float = 3):
    """Simulate human-like delay"""
    time.sleep(random.uniform(min_seconds, max_seconds))


def format_timestamp() -> str:
    """Format current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def spin_text(text: str) -> str:
    """
    Simple text spinner for random content
    Example: "Hello {world|everyone|there}" -> "Hello world"
    """
    import re
    
    def replace_spin(match):
        options = match.group(1).split('|')
        return random.choice(options)
    
    pattern = r'\{([^}]+)\}'
    return re.sub(pattern, replace_spin, text)


class ProxyTest:
    """Test proxy functionality"""
    
    @staticmethod
    def test_proxy(proxy: str, timeout: int = 10) -> bool:
        """Test if proxy is working"""
        try:
            import requests
            proxies = {
                'http': proxy,
                'https': proxy
            }
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Proxy test failed: {e}")
            return False
