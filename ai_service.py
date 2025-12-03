import requests
import json
from flask import Response
import threading
import queue

class AIService:
    def __init__(self, api_key, model_name, api_url):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def generate_response(self, messages, user_sid=None):
        """
        生成AI回复
        :param messages: 消息历史列表
        :param user_sid: 用户会话ID（用于跟踪）
        :return: AI回复内容
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_url}chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
        except Exception as e:
            return f"请求出错: {str(e)}"
    
    def generate_stream_response(self, messages, response_queue):
        """
        流式生成AI回复
        :param messages: 消息历史列表
        :param response_queue: 用于传输数据的队列
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.api_url}chat/completions",
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data = decoded_line[6:]  # 移除 'data: ' 前缀
                            if data != '[DONE]':
                                try:
                                    json_data = json.loads(data)
                                    if 'choices' in json_data and len(json_data['choices']) > 0:
                                        delta = json_data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            response_queue.put(content)
                                except json.JSONDecodeError:
                                    pass
            else:
                response_queue.put(f"API调用失败: {response.status_code} - {response.text}")
        except Exception as e:
            response_queue.put(f"请求出错: {str(e)}")
        finally:
            response_queue.put(None)  # 结束信号
    
    def stream_response(self, messages):
        """
        创建SSE流式响应
        :param messages: 消息历史列表
        """
        response_queue = queue.Queue()
        
        # 在单独的线程中生成响应
        thread = threading.Thread(
            target=self.generate_stream_response,
            args=(messages, response_queue)
        )
        thread.start()
        
        def generate():
            while True:
                try:
                    content = response_queue.get(timeout=1)
                    if content is None:  # 结束信号
                        break
                    yield f"data: {json.dumps({'content': content})}\n\n"
                except queue.Empty:
                    continue
            
            # 确保线程结束
            thread.join()
            yield "data: [DONE]\n\n"
        
        return Response(generate(), mimetype='text/event-stream')