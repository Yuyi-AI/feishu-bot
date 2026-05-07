# 飞书 AI 机器人

一个接入 MiniMax 大模型的飞书机器人，可以通过私聊或群聊与 AI 对话。

## 功能

- 🤖 智能对话（基于 MiniMax 大模型）
- 💬 支持私聊和群聊
- 🔄 自动回复

## 部署

### Railway 部署

1. Fork 本仓库到你的 GitHub
2. 在 Railway 中创建新项目，选择 "Deploy from GitHub repo"
3. 连接你的 GitHub 账号，选择本仓库
4. 添加环境变量：
   - `MINIMAX_API_KEY`: 你的 MiniMax API Key
   - `FEISHU_APP_ID`: 飞书应用 App ID
   - `FEISHU_APP_SECRET`: 飞书应用 App Secret
5. 点击 Deploy

### 本地运行

```bash
pip install -r requirements.txt
export MINIMAX_API_KEY="你的API密钥"
export FEISHU_APP_ID="飞书AppID"
export FEISHU_APP_SECRET="飞书AppSecret"
python app.py
```

## 飞书应用配置

1. 在 [飞书开放平台](https://open.feishu.cn) 创建应用
2. 添加 "机器人" 能力
3. 配置消息事件订阅：
   - 事件：`im.message.receive_v1`
   - 请求地址：`https://你的Railway地址/webhook`
4. 发布应用

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| `MINIMAX_API_KEY` | MiniMax API 密钥 | 是 |
| `FEISHU_APP_ID` | 飞书应用 App ID | 是 |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret | 是 |
| `PORT` | 服务端口（默认 5000） | 否 |

## License

MIT
