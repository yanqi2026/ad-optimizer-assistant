# Streamlit Cloud 部署指南

## 快速部署步骤

### 方式一：GitHub 部署（推荐）

1. **创建 GitHub 仓库**
   - 登录 GitHub，点击 "New repository"
   - 仓库名称：`optimization-assistant`（或自定义）
   - 选择 Public（Streamlit Cloud 免费版要求Public仓库）

2. **上传项目文件**
   ```
   optimization-assistant/
   ├── app.py
   ├── requirements.txt
   ├── coze_api.py
   ├── demo_data.py
   ├── pages/
   │   ├── 0_Home.py
   │   └── 1_优化工作台.py
   └── .streamlit/
       └── config.toml
   ```

3. **部署到 Streamlit Cloud**
   - 访问 https://share.streamlit.io
   - 点击 "New app"
   - 选择你的 GitHub 仓库
   - 设置：
     - Repository: `your-username/optimization-assistant`
     - Branch: `main`
     - Main file path: `app.py`
   - 点击 "Deploy!"

### 方式二：直接上传 ZIP

1. 将项目打包成 ZIP 文件
2. 访问 https://share.streamlit.io
3. 点击 "New app" → "Upload"

## 配置 Secrets（敏感信息）

Streamlit Cloud 部署时，需要配置 Coze PAT Token：

1. 在 Streamlit Cloud 你的 App 页面
2. 点击右上角 "Settings"
3. 选择 "Secrets"
4. 添加：
   ```
   COZE_PAT_TOKEN = "pat_xxxxxxxxxxxx"
   ```

## 获取 Coze PAT Token

1. 访问 https://www.coze.cn
2. 登录后进入个人中心
3. 点击 "API Keys" → "创建"
4. 复制生成的 PAT Token

## 常见问题

### Q: 部署后显示 404 错误
A: 确保 Main file path 正确设置为 `app.py`

### Q: Bot 对话无响应
A: 检查 Secrets 中的 COZE_PAT_TOKEN 是否正确配置

### Q: 如何更新部署的版本？
A: 推送代码到 GitHub 后，Streamlit Cloud 会自动重新部署

## 自定义域名（可选）

Streamlit Cloud 支持自定义域名：
1. 在 App 设置中添加自定义域名
2. 配置 DNS CNAME 记录指向 `streamlit.io`

## 监控和维护

- Streamlit Cloud Dashboard 可查看日志和性能
- 设置 email alerts 接收错误通知
