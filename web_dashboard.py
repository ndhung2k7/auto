"""
Web dashboard using Flask
"""
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import threading
import json
from typing import Dict
from utils import logger, DataManager, Config


class WebDashboard:
    """Web dashboard for managing the tool"""
    
    def __init__(self, account_manager, proxy_manager, scheduler, config):
        self.app = Flask(__name__)
        CORS(self.app)
        self.account_manager = account_manager
        self.proxy_manager = proxy_manager
        self.scheduler = scheduler
        self.config = config
        self.data_manager = DataManager()
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @self.app.route('/api/accounts', methods=['GET'])
        def get_accounts():
            accounts = self.account_manager.get_all_accounts()
            return jsonify(accounts)
        
        @self.app.route('/api/accounts', methods=['POST'])
        def add_account():
            data = request.json
            success = self.account_manager.add_account(data)
            if success:
                # Assign proxy if provided
                if data.get('proxy'):
                    self.proxy_manager.assign_proxy(data['username'], data['proxy'])
                return jsonify({'success': True, 'message': 'Account added'})
            return jsonify({'success': False, 'message': 'Failed to add account'})
        
        @self.app.route('/api/accounts/<username>', methods=['PUT'])
        def update_account(username):
            data = request.json
            success = self.account_manager.update_account(username, data)
            if success and data.get('proxy'):
                self.proxy_manager.assign_proxy(username, data['proxy'])
            return jsonify({'success': success})
        
        @self.app.route('/api/accounts/<username>', methods=['DELETE'])
        def delete_account(username):
            success = self.account_manager.delete_account(username)
            self.proxy_manager.remove_proxy(username)
            return jsonify({'success': success})
        
        @self.app.route('/api/tasks', methods=['GET'])
        def get_tasks():
            tasks = self.scheduler.get_all_tasks()
            return jsonify(tasks)
        
        @self.app.route('/api/tasks', methods=['POST'])
        def add_task():
            data = request.json
            task_id = self.scheduler.add_task(data)
            if task_id:
                return jsonify({'success': True, 'task_id': task_id})
            return jsonify({'success': False})
        
        @self.app.route('/api/tasks/<task_id>', methods=['DELETE'])
        def stop_task(task_id):
            success = self.scheduler.stop_task(task_id)
            return jsonify({'success': success})
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            stats = self.account_manager.get_statistics()
            return jsonify({
                'running': self.scheduler.running,
                'accounts': stats,
                'tasks': len(self.scheduler.active_tasks)
            })
        
        @self.app.route('/api/start', methods=['POST'])
        def start_tool():
            self.scheduler.start()
            return jsonify({'success': True})
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_tool():
            self.scheduler.stop()
            return jsonify({'success': True})
        
        @self.app.route('/api/proxies/test', methods=['POST'])
        def test_proxy():
            proxy = request.json.get('proxy')
            from utils import ProxyTest
            test = ProxyTest()
            is_working = test.test_proxy(proxy)
            return jsonify({'working': is_working})
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            return jsonify(self.config.config)
        
        @self.app.route('/api/config', methods=['PUT'])
        def update_config():
            data = request.json
            self.config.config.update(data)
            self.config.save()
            return jsonify({'success': True})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web dashboard"""
        self.app.run(host=host, port=port, debug=debug, threaded=True)


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Comment Tool Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Rob
