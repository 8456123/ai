import os

class Config:
    # WebSocket服务器地址配置
    WEBSOCKET_SERVERS = [
        'ws://localhost:5001/socket.io',  # 本地服务器地址
        'http://jnafltkvc7xj.ngrok.xiaomiqiu123.top'  # 公网服务器地址
    ]
    
    # 固定密码配置
    FIXED_PASSWORD = '123456'
    
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-oodaichat'