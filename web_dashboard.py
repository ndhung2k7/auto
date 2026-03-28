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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .status-bar {
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }
        
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-running {
            background: #10b981;
            color: white;
        }
        
        .status-stopped {
            background: #ef4444;
            color: white;
        }
        
        .btn {
            padding: 8px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a67d8;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            margin-bottom: 15px;
            color: #333;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        
        th {
            background: #f9fafb;
            font-weight: bold;
            color: #374151;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #374151;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .form-group textarea {
            min-height: 80px;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .close {
            cursor: pointer;
            font-size: 24px;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #667eea;
            transition: width 0.3s;
        }
        
        .log-container {
            background: #1f2937;
            color: #10b981;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .loading {
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Auto Comment Tool Dashboard</h1>
            <div class="status-bar">
                <div id="toolStatus" class="status-badge status-stopped">
                    ⚫ Đã dừng
                </div>
                <button id="startBtn" class="btn btn-success">▶️ Bắt đầu</button>
                <button id="stopBtn" class="btn btn-danger">⏹️ Dừng</button>
                <button id="refreshBtn" class="btn btn-primary">🔄 Làm mới</button>
            </div>
        </div>
        
        <div class="grid-2">
            <div class="card">
                <h2>📊 Thống kê</h2>
                <div id="stats">
                    <p>Tổng tài khoản: <strong id="totalAccounts">0</strong></p>
                    <p>Tài khoản hoạt động: <strong id="activeAccounts">0</strong></p>
                    <p>Tài khoản lỗi: <strong id="errorAccounts">0</strong></p>
                    <p>Tổng comment: <strong id="totalComments">0</strong></p>
                    <p>Tasks đang chạy: <strong id="runningTasks">0</strong></p>
                </div>
            </div>
            
            <div class="card">
                <h2>⚙️ Điều khiển nhanh</h2>
                <button id="addAccountBtn" class="btn btn-primary">➕ Thêm tài khoản</button>
                <button id="addTaskBtn" class="btn btn-primary">📝 Thêm task comment</button>
                <button id="testProxyBtn" class="btn btn-primary">🌐 Test proxy</button>
            </div>
        </div>
        
        <div class="card">
            <h2>👤 Danh sách tài khoản</h2>
            <table id="accountsTable">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Platform</th>
                        <th>Status</th>
                        <th>Proxy</th>
                        <th>Comments</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="accountsBody">
                    <tr><td colspan="6">Đang tải...</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>📋 Tasks đang chạy</h2>
            <table id="tasksTable">
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>Status</th>
                        <th>Progress</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="tasksBody">
                    <tr><td colspan="4">Chưa có task nào</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>📝 Log hoạt động</h2>
            <div class="log-container" id="logContainer">
                <div>Tool đã sẵn sàng...</div>
            </div>
        </div>
    </div>
    
    <!-- Modal Add Account -->
    <div id="addAccountModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Thêm tài khoản mới</h3>
                <span class="close">&times;</span>
            </div>
            <form id="addAccountForm">
                <div class="form-group">
                    <label>Username *</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Platform *</label>
                    <select name="platform" required>
                        <option value="facebook">Facebook</option>
                        <option value="tiktok">TikTok</option>
                        <option value="instagram">Instagram</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Email/Username</label>
                    <input type="text" name="email">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password">
                </div>
                <div class="form-group">
                    <label>Proxy (format: http://ip:port or http://user:pass@ip:port)</label>
                    <input type="text" name="proxy" placeholder="http://127.0.0.1:8080">
                </div>
                <button type="submit" class="btn btn-primary">Thêm tài khoản</button>
            </form>
        </div>
    </div>
    
    <!-- Modal Add Task -->
    <div id="addTaskModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Thêm task comment mới</h3>
                <span class="close">&times;</span>
            </div>
            <form id="addTaskForm">
                <div class="form-group">
                    <label>Link bài viết/Video (mỗi link 1 dòng)</label>
                    <textarea name="links" required placeholder="https://facebook.com/post/1&#10;https://tiktok.com/@user/video/1"></textarea>
                </div>
                <div class="form-group">
                    <label>Nội dung comment (mỗi nội dung 1 dòng, hỗ trợ spin: {a|b|c})</label>
                    <textarea name="comments" required placeholder="Hay quá!&#10;Tuyệt vời {lắm|quá|đấy}!"></textarea>
                </div>
                <div class="form-group">
                    <label>Delay giữa các comment (giây)</label>
                    <input type="number" name="delay" value="200">
                </div>
                <div class="form-group">
                    <label>Random range (giây)</label>
                    <input type="number" name="random_range" value="30">
                </div>
                <button type="submit" class="btn btn-primary">Tạo task</button>
            </form>
        </div>
    </div>
    
    <script>
        let refreshInterval = null;
        
        async function fetchData() {
            try {
                const [statusRes, accountsRes, tasksRes] = await Promise.all([
                    fetch('/api/status'),
                    fetch('/api/accounts'),
                    fetch('/api/tasks')
                ]);
                
                const status = await statusRes.json();
                const accounts = await accountsRes.json();
                const tasks = await tasksRes.json();
                
                updateStatus(status);
                updateAccountsTable(accounts);
                updateTasksTable(tasks);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        function updateStatus(status) {
            const toolStatus = document.getElementById('toolStatus');
            if (status.running) {
                toolStatus.className = 'status-badge status-running';
                toolStatus.innerHTML = '🟢 Đang chạy';
            } else {
                toolStatus.className = 'status-badge status-stopped';
                toolStatus.innerHTML = '⚫ Đã dừng';
            }
            
            document.getElementById('totalAccounts').textContent = status.accounts.total;
            document.getElementById('activeAccounts').textContent = status.accounts.active;
            document.getElementById('errorAccounts').textContent = status.accounts.error;
            document.getElementById('totalComments').textContent = status.accounts.total_comments;
            document.getElementById('runningTasks').textContent = status.tasks;
        }
        
        function updateAccountsTable(accounts) {
            const tbody = document.getElementById('accountsBody');
            if (Object.keys(accounts).length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">Chưa có tài khoản nào</td></tr>';
                return;
            }
            
            tbody.innerHTML = '';
            for (const [username, acc] of Object.entries(accounts)) {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = username;
                row.insertCell(1).textContent = acc.platform;
                row.insertCell(2).innerHTML = `<span class="status-badge status-${acc.status}">${acc.status}</span>`;
                row.insertCell(3).textContent = acc.proxy || 'Không có';
                row.insertCell(4).textContent = acc.comments_made || 0;
                
                const actions = row.insertCell(5);
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Xóa';
                deleteBtn.className = 'btn btn-danger';
                deleteBtn.style.padding = '4px 12px';
                deleteBtn.onclick = () => deleteAccount(username);
                actions.appendChild(deleteBtn);
            }
        }
        
        function updateTasksTable(tasks) {
            const tbody = document.getElementById('tasksBody');
            if (Object.keys(tasks).length === 0) {
                tbody.innerHTML = '<tr><td colspan="4">Chưa có task nào</td></tr>';
                return;
            }
            
            tbody.innerHTML = '';
            for (const [taskId, task] of Object.entries(tasks)) {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = taskId;
                row.insertCell(1).innerHTML = `<span class="status-badge status-${task.status}">${task.status}</span>`;
                
                const progress = task.total > 0 ? (task.progress / task.total * 100) : 0;
                row.insertCell(2).innerHTML = `
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <small>${task.progress}/${task.total}</small>
                `;
                
                const actions = row.insertCell(3);
                if (task.status === 'running') {
                    const stopBtn = document.createElement('button');
                    stopBtn.textContent = 'Dừng';
                    stopBtn.className = 'btn btn-danger';
                    stopBtn.style.padding = '4px 12px';
                    stopBtn.onclick = () => stopTask(taskId);
                    actions.appendChild(stopBtn);
                }
            }
        }
        
        async function startTool() {
            const response = await fetch('/api/start', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                addLog('Tool đã được bắt đầu');
                fetchData();
            }
        }
        
        async function stopTool() {
            const response = await fetch('/api/stop', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                addLog('Tool đã được dừng');
                fetchData();
            }
        }
        
        async function deleteAccount(username) {
            if (confirm(`Xóa tài khoản ${username}?`)) {
                const response = await fetch(`/api/accounts/${username}`, { method: 'DELETE' });
                const data = await response.json();
                if (data.success) {
                    addLog(`Đã xóa tài khoản ${username}`);
                    fetchData();
                }
            }
        }
        
        async function stopTask(taskId) {
            const response = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
            const data = await response.json();
            if (data.success) {
                addLog(`Đã dừng task ${taskId}`);
                fetchData();
            }
        }
        
        function addLog(message) {
            const logContainer = document.getElementById('logContainer');
            const logEntry = document.createElement('div');
            logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Modal handling
        const addAccountModal = document.getElementById('addAccountModal');
        const addTaskModal = document.getElementById('addTaskModal');
        
        document.getElementById('addAccountBtn').onclick = () => {
            addAccountModal.style.display = 'flex';
        };
        
        document.getElementById('addTaskBtn').onclick = () => {
            addTaskModal.style.display = 'flex';
        };
        
        document.querySelectorAll('.close').forEach(close => {
            close.onclick = () => {
                addAccountModal.style.display = 'none';
                addTaskModal.style.display = 'none';
            };
        });
        
        document.getElementById('addAccountForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                username: formData.get('username'),
                platform: formData.get('platform'),
                auth_data: {
                    email: formData.get('email'),
                    password: formData.get('password')
                },
                proxy: formData.get('proxy')
            };
            
            const response = await fetch('/api/accounts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                addLog(`Đã thêm tài khoản ${data.username}`);
                addAccountModal.style.display = 'none';
                fetchData();
                e.target.reset();
            } else {
                alert('Thêm tài khoản thất bại: ' + result.message);
            }
        };
        
        document.getElementById('addTaskForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const links = formData.get('links').split('\\n').filter(l => l.trim());
            const comments = formData.get('comments').split('\\n').filter(c => c.trim());
            const data = {
                links: links,
                comments: comments,
                delay: parseInt(formData.get('delay')),
                random_range: parseInt(formData.get('random_range')),
                accounts: [] // Get from active accounts
            };
            
            // Get active accounts
            const accountsRes = await fetch('/api/accounts');
            const accounts = await accountsRes.json();
            data.accounts = Object.keys(accounts).filter(username => accounts[username].status === 'active');
            
            if (data.accounts.length === 0) {
                alert('Không có tài khoản hoạt động nào!');
                return;
            }
            
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                addLog(`Đã tạo task mới: ${result.task_id}`);
                addTaskModal.style.display = 'none';
                fetchData();
                e.target.reset();
            } else {
                alert('Tạo task thất bại');
            }
        };
        
        document.getElementById('startBtn').onclick = startTool;
        document.getElementById('stopBtn').onclick = stopTool;
        document.getElementById('refreshBtn').onclick = fetchData;
        
        // Auto refresh every 5 seconds
        refreshInterval = setInterval(fetchData, 5000);
        fetchData();
        
        // Fetch logs periodically
        setInterval(async () => {
            try {
                const response = await fetch('/api/logs');
                if (response.ok) {
                    const logs = await response.json();
                    const logContainer = document.getElementById('logContainer');
                    logContainer.innerHTML = logs.map(log => `<div>${log}</div>`).join('');
                }
            } catch (e) {
                // Ignore errors
            }
        }, 2000);
    </script>
</body>
</html>
"""
