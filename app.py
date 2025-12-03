from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
from config import Config
from ai_chat import AIChatManager

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化AI聊天管理器
ai_chat_manager = AIChatManager(app, socketio)

# 存储在线用户信息，包括用户名和头像
online_users = {}

@app.route('/')
def index():
    """登录页面"""
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """处理登录请求"""
    username = request.form['username']
    password = request.form['password']
    server = request.form['server']
    avatar = request.form.get('avatar', '😀')  # 默认头像为😀
    
    # 验证密码
    if password != Config.FIXED_PASSWORD:
        return render_template('login.html', error='密码错误')
    
    # 验证服务器地址是否在配置中
    if server not in Config.WEBSOCKET_SERVERS:
        return render_template('login.html', error='无效的服务器地址')
    
    # 登录成功，保存会话
    session['username'] = username
    session['server'] = server
    session['avatar'] = avatar
    
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    """聊天室页面"""
    if 'username' not in session:
        return redirect(url_for('index'))
    
    return render_template('chat.html', username=session['username'])

@app.route('/logout')
def logout():
    """退出登录"""
    username = session.get('username')
    if username and username in online_users:
        del online_users[username]
    
    session.clear()
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    username = session.get('username')
    avatar = session.get('avatar', '😀')  # 默认头像
    if username:
        # 存储用户的SID和头像信息
        online_users[username] = {
            'sid': request.sid,
            'avatar': avatar
        }
        # 广播用户上线消息
        emit('user_joined', {'username': username}, broadcast=True)
        # 发送在线用户列表（包含头像信息）
        user_list = [{'username': user, 'avatar': info['avatar']} for user, info in online_users.items()]
        emit('online_users', user_list, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    username = session.get('username')
    if username and username in online_users:
        del online_users[username]
        # 广播用户离线消息
        emit('user_left', {'username': username}, broadcast=True)
        # 更新在线用户列表（包含头像信息）
        user_list = [{'username': user, 'avatar': info['avatar']} for user, info in online_users.items()]
        emit('online_users', user_list, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    """处理消息发送"""
    username = session.get('username')
    avatar = session.get('avatar', '😀')  # 获取用户头像
    if username:
        message_data = {
            'username': username,
            'message': data['message'],
            'timestamp': data.get('timestamp', ''),
            'avatar': avatar  # 添加头像信息
        }
        # 广播消息给所有用户
        emit('receive_message', message_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)