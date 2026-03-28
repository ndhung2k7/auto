"""
Main application entry point
"""
import os
import sys
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import logger, Config, DataManager
from account_manager import AccountManager
from proxy_manager import ProxyManager
from comment_engine import CommentEngine
from scheduler import TaskScheduler
from web_dashboard import WebDashboard


class AutoCommentTool:
    """Main application class"""
    
    def __init__(self):
        """Initialize all components"""
        logger.info("Initializing Auto Comment Tool...")
        
        # Load configuration
        self.config = Config()
        
        # Initialize managers
        self.account_manager = AccountManager()
        self.proxy_manager = ProxyManager()
        self.comment_engine = CommentEngine(self.account_manager, self.proxy_manager)
        self.scheduler = TaskScheduler(
            self.comment_engine,
            self.account_manager,
            self.config
        )
        
        # Load accounts and assign proxies
        self.load_accounts_with_proxies()
        
        # Initialize web dashboard
        self.dashboard = WebDashboard(
            self.account_manager,
            self.proxy_manager,
            self.scheduler,
            self.config
        )
        
        logger.info("Tool initialized successfully")
    
    def load_accounts_with_proxies(self):
        """Load accounts and assign proxies"""
        accounts = self.account_manager.get_all_accounts()
        for username, account in accounts.items():
            proxy = account.get('proxy')
            if proxy:
                self.proxy_manager.assign_proxy(username, proxy)
                logger.info(f"Loaded proxy for {username}")
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the application"""
        logger.info(f"Starting web dashboard on http://{host}:{port}")
        
        try:
            # Run dashboard in main thread
            self.dashboard.run(host=host, port=port, debug=False)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"Error running application: {e}")
            self.stop()
    
    def stop(self):
        """Stop the application"""
        logger.info("Stopping application...")
        self.scheduler.stop()
        self.comment_engine.cleanup()
        logger.info("Application stopped")


if __name__ == '__main__':
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('config').mkdir(exist_ok=True)
    
    # Run application
    tool = AutoCommentTool()
    tool.run()
