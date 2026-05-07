"""
飞书机器人 - 接入 MiniMax 大模型
"""
import os
import json
import hmac
import hashlib
import base64
import time
from functools import wraps

import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# ============== 配置 ==============
# MiniMax API 配置
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-dOEd8lQxEp40X_rhvQEFuwzxZzbunrDzJ9_3JVdWMx44W7Idl0j9Ji2vJqk91GzjdBZWwNLidiKiHW8ypYU7gvsuTpUd0nYM3yXzNAXH8K2UaWxSvGld5ug")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"

# 飞书配置
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a976187522781cce")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "WAutLLgLBXs5aYSILQYNefJ6xO7kQJHj")

# ============== 飞书 API ==============
def get_feishu_access_token():
    """获取飞书 access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("tenant_access_token")

def send_feishu_message(access_token, receive_id, msg_type, content):
    """发送飞书消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id": receive_id}
    data = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": json.dumps(content)
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    return response.json()

# ============== MiniMax API ==============
def chat_with_minimax(user_message, history=None):
    """调用 MiniMax API 进行对话"""
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构建消息
    messages = []
    if history:
        messages.extend(history)
    messages.append({
        "role": "user", 
        "content": user_message
    })
    
    data = {
        "model": "MiniMax-Text-01",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(MINIMAX_API_URL, headers=headers, json=data, timeout=60)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"抱歉，MiniMax 返回了错误：{result['error']}"
        else:
            return f"抱歉，我遇到了一些问题，请稍后再试。响应：{result}"
    except requests.exceptions.Timeout:
        return "抱歉，AI 处理超时了，请稍后再试。"
    except Exception as e:
        return f"抱歉，发生了错误：{str(e)}"

# ============== 飞书事件处理 ==============
@app.route("/", methods=["GET"])
def index():
    return "飞书 AI 机器人运行中！"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """飞书事件 webhook"""
    # 处理 URL 验证（飞书配置时会发送 GET 请求验证）
    if request.method == "GET":
        challenge = request.args.get("challenge")
        print(f"[DEBUG] GET request received, challenge={challenge}")
        if challenge:
            response_data = json.dumps({"challenge": challenge})
            print(f"[DEBUG] Returning response: {response_data}")
            return Response(
                response_data,
                status=200,
                mimetype="application/json"
            )
        return "OK"
    
    data = request.json
    
    # 忽略非消息事件
    if data.get("header", {}).get("event_type") != "im.message.receive_v1":
        return "", 200
    
    # 获取消息内容
    message = data.get("event", {}).get("message", {})
    msg_type = message.get("msg_type")
    message_id = message.get("message_id")
    chat_id = message.get("chat_id")
    sender = data.get("event", {}).get("sender", {})
    sender_id = sender.get("sender_id", {}).get("open_id", "unknown")
    
    # 只处理文本消息
    if msg_type != "text":
        return "", 200
    
    # 获取消息内容
    content = json.loads(message.get("content", "{}"))
    user_text = content.get("text", "").strip()
    
    # 跳过空消息
    if not user_text:
        return "", 200
    
    # 获取 access_token
    access_token = get_feishu_access_token()
    if not access_token:
        return "", 200
    
    # 调用 AI
    ai_response = chat_with_minimax(user_text)
    
    # 发送回复
    send_feishu_message(
        access_token, 
        sender_id,  # 回复发送者
        "text", 
        {"text": ai_response}
    )
    
    return "", 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
