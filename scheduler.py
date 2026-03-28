"""
Task scheduler module
"""
import time
import threading
import queue
from typing import Dict, List
from datetime import datetime
import schedule
from utils import logger, random_delay, spin_text


class TaskScheduler:
    """Handle task scheduling and execution"""
    
    def __init__(self, comment_engine, account_manager, config):
        self.comment_engine = comment_engine
        self.account_manager = account_manager
        self.config = config
        self.running = False
        self.task_queue = queue.Queue()
        self.active_tasks = {}
        self.task_thread = None
    
    def add_task(self, task_data: Dict) -> str:
        """Add a new comment task"""
        try:
            task_id = f"task_{int(time.time())}_{len(self.active_tasks)}"
            
            task = {
                'id': task_id,
                'links': task_data.get('links', []),
                'comments': task_data.get('comments', []),
                'accounts': task_data.get('accounts', []),
                'delay': task_data.get('delay', self.config.get('default_delay.between_comments', 200)),
                'random_range': task_data.get('random_range', self.config.get('default_delay.random_range', 30)),
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'progress': 0,
                'total': 0
            }
            
            # Calculate total comments
            task['total'] = len(task['links']) * len(task['comments']) * len(task['accounts'])
            
            self.active_tasks[task_id] = task
            self.task_queue.put(task_id)
            
            logger.info(f"Task {task_id} added with {task['total']} comments")
            return task_id
            
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return None
    
    def execute_task(self, task_id: str):
        """Execute a single task"""
        task = self.active_tasks.get(task_id)
        if not task:
            return
        
        try:
            task['status'] = 'running'
            logger.info(f"Starting task {task_id}")
            
            total_comments = 0
            comments_made = 0
            
            # Get active accounts
            accounts = [
                acc for acc in self.account_manager.get_all_accounts().values()
                if acc['username'] in task['accounts'] and acc['status'] == 'active'
            ]
            
            if not accounts:
                logger.warning(f"No active accounts for task {task_id}")
                task['status'] = 'failed'
                return
            
            # Execute comments
            for account in accounts:
                for link in task['links']:
                    for comment_template in task['comments']:
                        # Check if task was stopped
                        if not self.running:
                            logger.info(f"Task {task_id} stopped by user")
                            task['status'] = 'stopped'
                            return
                        
                        # Spin text for variation
                        comment_text = spin_text(comment_template)
                        
                        # Perform comment
                        success = self.comment_engine.comment(account, link, comment_text)
                        
                        if success:
                            comments_made += 1
                            task['progress'] = comments_made
                            logger.info(f"Task {task_id} progress: {comments_made}/{task['total']}")
                        else:
                            logger.warning(f"Failed to comment with {account['username']}")
                        
                        # Delay between comments
                        if comments_made < task['total']:
                            delay = random_delay(task['delay'], task['random_range'])
                            logger.info(f"Waiting {delay} seconds before next comment")
                            time.sleep(delay)
            
            task['status'] = 'completed'
            logger.info(f"Task {task_id} completed. Made {comments_made} comments")
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            task['status'] = 'failed'
    
    def worker(self):
        """Worker thread to process tasks"""
        while self.running:
            try:
                # Get task from queue with timeout
                task_id = self.task_queue.get(timeout=1)
                self.execute_task(task_id)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.task_thread = threading.Thread(target=self.worker, daemon=True)
        self.task_thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.task_thread:
            self.task_thread.join(timeout=5)
        self.comment_engine.cleanup()
        logger.info("Scheduler stopped")
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        return self.active_tasks.get(task_id, {})
    
    def get_all_tasks(self) -> Dict:
        """Get all tasks"""
        return self.active_tasks
    
    def stop_task(self, task_id: str) -> bool:
        """Stop a specific task"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = 'stopping'
            logger.info(f"Stopping task {task_id}")
            return True
        return False
