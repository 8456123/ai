# OODaiP聊天室

这是一个基于Python Flask和WebSocket的在线聊天室应用。

## 功能特性

- 用户登录验证（固定密码：123456）
- 多人实时聊天
- WebSocket通信
- 在线用户显示
- 支持Emoji表情
- 响应式设计
- 特殊功能指令（@成小理 @音乐一下 @电影 @天气 @新闻 @小视频）

## 技术栈

- Python 3
- Flask
- Flask-SocketIO
- HTML5
- CSS3
- JavaScript
- jQuery

## 安装与运行

1. 创建虚拟环境：
   ```
   python -m venv venv
   ```

2. 激活虚拟环境：
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 运行应用：
   ```
   python app.py
   ```

5. 访问应用：
   打开浏览器访问 `http://localhost:5000`

## 使用说明

1. 登录页面输入昵称和密码（123456）
2. 选择服务器地址
3. 进入聊天室开始聊天
4. 使用底部功能按钮触发特殊功能
5. 点击右上角退出按钮退出聊天室

## 目录结构

```
├── app.py              # Flask应用主文件
├── config.py           # 配置文件
├── requirements.txt    # 依赖包列表
├── README.md           # 项目说明文档
├── templates/          # HTML模板目录
│   ├── login.html      # 登录页面
│   └── chat.html       # 聊天室页面
└── static/             # 静态资源目录
    └── js/             # JavaScript文件目录
        └── jquery-3.7.1.min.js  # jQuery库文件（需手动添加）
```

## 注意事项

- 需要手动将 jQuery 3.7.1 minified 版本文件拷贝到 `static/js/` 目录下
- 默认运行端口为 5000
- 支持多用户同时在线聊天