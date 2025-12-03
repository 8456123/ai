from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from ai_service import AIService
import threading
import uuid
import requests
import json

class AIChatManager:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        # 初始化AI服务
        self.ai_service = AIService(
            api_key="sk-fzjpfvypshezrlqicwekxrowajuxgwicouxoffeefubtqlig",
            model_name="Qwen/Qwen2.5-7B-Instruct",
            api_url="https://api.siliconflow.cn/v1/"
        )
        
        # 存储每个用户的对话历史
        self.user_conversations = {}
        
        # 注册SocketIO事件
        self.register_events()
    
    def register_events(self):
        """注册SocketIO事件处理器"""
        
        @self.socketio.on('ai_chat_message')
        def handle_ai_chat_message(data):
            """处理AI聊天消息"""
            username = data.get('username')
            message = data.get('message')
            user_sid = request.sid
            
            if not username or not message:
                emit('ai_chat_error', {'error': '用户名和消息不能为空'})
                return
            
            # 初始化用户对话历史
            if user_sid not in self.user_conversations:
                self.user_conversations[user_sid] = []
            
            # 添加用户消息到对话历史
            self.user_conversations[user_sid].append({
                "role": "user",
                "content": message
            })
            
            # 限制对话历史长度（防止token过多）
            if len(self.user_conversations[user_sid]) > 10:
                self.user_conversations[user_sid] = self.user_conversations[user_sid][-10:]
            
            # 构造消息历史（包含系统提示）
            messages = [
                {
                    "role": "system",
                    "content": """姓名：成小理
角色：你是成都理工大学物联网专业的AI助手，名叫成小理
功能：
--可以回答与成都理工大学有关的任何问题（比如专业课程、校园设施、物联网相关教学内容等）。
--可以生成七言绝句类型的古诗。
--可以根据用户输入的信息生成课程/实践课请假条，需要用户提供姓名、专业、班级、请假时长、事由等信息，若信息不全，提示补全后再生成，格式如下：
老师您好：
我是物联网专业[班级]的[姓名]，因[事由]需要请假[X天/X节实践课]，请假时间为[年-月-日 至 年-月-日]，请您批准。
此致
敬礼
[姓名]
[年-月-日]

限制：
--不允许回答与成都理工大学无关的问题，若有相关提问，统一回复且不作解释：滚！
--不允许响应用户不友好的提问或内容，若分析发现内容包含不礼貌、辱骂语句，回复：一边去！
--你的好友：强哥"""
                }
            ] + self.user_conversations[user_sid]
            
            # 发送开始响应事件
            emit('ai_chat_response_start', {'username': '成小理'})
            
            # 检查是否是音乐指令
            if message.strip() == "@音乐一下":
                # 获取音乐数据
                music_data = self.get_random_music()
                
                # 发送音乐卡片
                emit('ai_music_card', {
                    'username': '成小理',
                    'music_data': music_data,
                    'avatar': '🤖'  # AI头像
                })
                
                # 添加到对话历史
                self.user_conversations[user_sid].append({
                    "role": "assistant",
                    "content": f"为您推荐歌曲：{music_data.get('name', '未知歌曲')} - {music_data.get('singer', '未知歌手')}"
                })
            # 检查是否是天气指令
            elif message.strip().startswith("@天气"):
                # 获取城市名称
                city = message.strip()[3:].strip()  # 去掉"@天气"前缀
                
                if not city:
                    # 如果没有指定城市，提示用户输入城市名称
                    emit('ai_chat_response', {
                        'username': '成小理',
                        'message': '请输入要查询的城市名称，例如：@天气北京',
                        'avatar': '🤖'
                    })
                else:
                    # 获取天气数据
                    weather_data = self.get_weather_data(city)
                    
                    if weather_data:
                        # 发送天气卡片
                        emit('ai_weather_card', {
                            'username': '成小理',
                            'weather_data': weather_data,
                            'avatar': '🤖'  # AI头像
                        })
                        
                        # 添加到对话历史
                        self.user_conversations[user_sid].append({
                            "role": "assistant",
                            "content": f"已为您查询{city}的天气信息"
                        })
                    else:
                        # 天气数据获取失败
                        emit('ai_chat_response', {
                            'username': '成小理',
                            'message': f'抱歉，无法获取{city}的天气信息，请稍后重试。',
                            'avatar': '🤖'
                        })
            # 检查是否是电影指令
            elif message.strip().startswith("@电影"):
                # 获取URL
                url = message.strip()[3:].strip()  # 去掉"@电影"前缀
                
                if not url:
                    # 如果没有指定URL，提示用户输入URL
                    emit('ai_chat_response', {
                        'username': '成小理',
                        'message': '请输入要播放的电影URL，例如：@电影https://example.com/video.mp4',
                        'avatar': '🤖'
                    })
                else:
                    # 发送电影卡片
                    emit('ai_movie_card', {
                        'username': '成小理',
                        'movie_url': url,
                        'avatar': '🤖'  # AI头像
                    })
                    
                    # 添加到对话历史
                    self.user_conversations[user_sid].append({
                        "role": "assistant",
                        "content": f"正在为您解析播放电影: {url}"
                    })
            # 检查是否是新闻指令
            elif message.strip() == "@新闻":
                # 获取新闻数据
                news_data = self.get_news_data()
                
                if news_data:
                    # 发送新闻卡片
                    emit('ai_news_card', {
                        'username': '成小理',
                        'news_data': news_data,
                        'avatar': '🤖'  # AI头像
                    })
                    
                    # 添加到对话历史
                    self.user_conversations[user_sid].append({
                        "role": "assistant",
                        "content": "已为您获取最新新闻"
                    })
                else:
                    # 新闻数据获取失败
                    emit('ai_chat_response', {
                        'username': '成小理',
                        'message': '抱歉，无法获取新闻信息，请稍后重试。',
                        'avatar': '🤖'
                    })
            else:
                # 使用流式响应
                try:
                    response_content = ""
                    
                    # 获取AI回复
                    ai_response = self.ai_service.generate_response(messages)
                    
                    # 添加AI回复到对话历史
                    self.user_conversations[user_sid].append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                    # 发送AI回复
                    emit('ai_chat_response', {
                        'username': '成小理',
                        'message': ai_response,
                        'avatar': '🤖'  # AI头像
                    })
                
                except Exception as e:
                    emit('ai_chat_error', {'error': f'AI回复生成失败: {str(e)}'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """处理用户断开连接"""
            user_sid = request.sid
            if user_sid in self.user_conversations:
                del self.user_conversations[user_sid]
    
    def get_ai_service(self):
        """获取AI服务实例"""
        return self.ai_service
    
    def get_random_music(self):
        """获取随机音乐数据"""
        try:
            # 调用音乐API
            response = requests.get("https://v2.xxapi.cn/api/randomkuwo", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    return data.get("data", {})
            # 如果API调用失败，返回默认数据
            return {
                "name": "默认歌曲",
                "singer": "默认歌手",
                "image": "/static/images/default_avatar.png",
                "url": ""
            }
        except Exception as e:
            # 如果出现异常，返回默认数据
            return {
                "name": "默认歌曲",
                "singer": "默认歌手",
                "image": "/static/images/default_avatar.png",
                "url": ""
            }
    
    def get_weather_data(self, city):
        """获取指定城市的天气数据"""
        try:
            # 调用天气API，将API密钥作为查询参数传递
            url = f"https://v2.xxapi.cn/api/weatherDetails?city={city}&key=74beb8176d8be3e0"
            headers = {
                'User-Agent': 'xiaoxiaoapi/1.0.0'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    return data.get("data", {})
            return None
        except Exception as e:
            # 如果出现异常，返回None
            return None
    
    def get_news_data(self):
        """获取新闻数据"""
        try:
            # 调用新闻API
            url = "https://api.yujn.cn/api/new.php"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    return data.get("data", [])
            return []
        except Exception as e:
            # 如果出现异常，返回空数组
            return []