# BrowserBot - OpenClaw Python 浏览器控制器

> 让 OpenClaw 通过 Python Selenium 控制浏览器，实现自动化浏览和数据采集

## 概述

这是一个基于 Flask + Selenium 的 HTTP API 服务，允许 OpenClaw（或任何能发送 HTTP 请求的工具）通过发送指令来控制浏览器执行各种操作。

### 工作架构

```
OpenClaw (大脑) 
    ↓ HTTP POST
Python Flask API (控制器)
    ↓ Selenium
Chrome 浏览器 (执行器)
    ↓
返回页面内容 → OpenClaw 分析
```

## 安装

### 1. 安装依赖

```bash
pip install flask selenium flask-cors requests
```

### 2. 启动服务

```bash
python browserbot.py
```

服务启动后会：
- 打开 Chrome 浏览器窗口
- 运行在 `http://localhost:8765`

### 3. 注意事项

- 确保已安装 Chrome 浏览器
- 首次运行时会自动启动浏览器
- 代理设置：代码已自动禁用代理（避免 502 错误）

## API 接口

### 健康检查

```bash
GET http://localhost:8765/health
```

响应：
```json
{"status": "ok", "browser": "connected"}
```

### 执行命令

```bash
POST http://localhost:8765/execute
Content-Type: application/json
```

## 支持的操作

### 1. 导航到网址

```json
{
  "action": "navigate",
  "url": "https://www.google.com"
}
```

响应：
```json
{
  "action": "navigate",
  "success": true,
  "url": "https://www.google.com",
  "title": "Google"
}
```

### 2. 获取页面 HTML

```json
{
  "action": "get_html"
}
```

响应：
```json
{
  "action": "get_html",
  "success": true,
  "html": "<html>...</html>"
}
```

### 3. 获取页面标题

```json
{
  "action": "get_title"
}
```

### 4. 获取当前网址

```json
{
  "action": "get_url"
}
```

### 5. 截图

```json
{
  "action": "screenshot"
}
```

响应（Base64 编码）：
```json
{
  "action": "screenshot",
  "success": true,
  "image": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### 6. 点击元素

```json
{
  "action": "click",
  "selector": "#submit-button"
}
```

### 7. 输入文本

```json
{
  "action": "type",
  "selector": "#search-input",
  "text": "hello world"
}
```

### 8. 滚动页面

```json
{
  "action": "scroll",
  "pixels": 500
}
```

### 9. 执行 JavaScript

```json
{
  "action": "evaluate",
  "script": "return document.title"
}
```

或执行更复杂的操作：
```json
{
  "action": "evaluate",
  "script": "return document.querySelector('h1').textContent"
}
```

### 10. 获取元素文本

```json
{
  "action": "get_text",
  "selector": "h1"
}
```

### 11. 前进/后退/刷新

```json
{"action": "back"}
```

```json
{"action": "forward"}
```

```json
{"action": "refresh"}
```

### 12. 关闭浏览器

```bash
POST http://localhost:8765/close
```

## Python 使用示例

```python
import requests

BASE_URL = "http://localhost:8765"
PROXIES = {"http": None, "https": None}

# 健康检查
r = requests.get(f"{BASE_URL}/health", proxies=PROXIES)
print(r.json())

# 搜索新闻
r = requests.post(
    f"{BASE_URL}/execute",
    json={"action": "navigate", "url": "https://www.google.com/search?q=OpenClaw+news"},
    proxies=PROXIES
)

# 获取页面标题
r = requests.post(
    f"{BASE_URL}/execute",
    json={"action": "get_title"},
    proxies=PROXIES
)
print(r.json())

# 获取特定元素内容
r = requests.post(
    f"{BASE_URL}/execute",
    json={
        "action": "evaluate",
        "script": "return document.querySelector('h1').textContent"
    },
    proxies=PROXIES
)
print(r.json())
```

## OpenClaw 集成

在 OpenClaw 中，可以通过 exec 工具调用 Python 脚本：

```python
import subprocess
import json

# 发送指令的函数
def send_browser_command(action, **kwargs):
    cmd = [
        "python", "-c",
        f"""
import requests
r = requests.post(
    'http://localhost:8765/execute',
    json={json.dumps({'action': action, **kwargs})},
    proxies={{'http': None, 'https': None}}
)
print(r.json())
"""
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

## 实际使用案例

### 案例 1：搜索新闻

```python
# 导航到 Google 新闻并搜索
requests.post(
    "http://localhost:8765/execute",
    json={
        "action": "navigate",
        "url": "https://www.google.com/search?q=OpenClaw+news&tbm=nws"
    },
    proxies={"http": None, "https": None}
)

# 获取搜索结果标题
requests.post(
    "http://localhost:8765/execute",
    json={
        "action": "evaluate",
        "script": "return document.querySelector('h3').textContent"
    },
    proxies={"http": None, "https": None}
)
```

### 案例 2：抓取网页内容

```python
# 导航到目标页面
requests.post(
    "http://localhost:8765/execute",
    json={"action": "navigate", "url": "https://x.com/user/status/123"},
    proxies={"http": None, "https": None}
)

# 获取完整 HTML
r = requests.post(
    "http://localhost:8765/execute",
    json={"action": "get_html"},
    proxies={"http": None, "https": None}
)
html = r.json()["html"]
```

### 案例 3：社交媒体交互

```python
# 点击按钮
requests.post(
    "http://localhost:8765/execute",
    json={"action": "click", "selector": ".like-button"},
    proxies={"http": None, "https": None}
)

# 输入评论
requests.post(
    "http://localhost:8765/execute",
    json={
        "action": "type",
        "selector": "textarea.comment-input",
        "text": "Great post!"
    },
    proxies={"http": None, "https": None}
)
```

## 常见问题

### 1. 浏览器未启动

确保 Chrome 已安装，路径默认：`C:\Program Files\Google\Chrome\Application\chrome.exe`

### 2. 502 Bad Gateway

这是代理问题。代码中已设置 `proxies={"http": None, "https": None}` 绕过代理。

### 3. 中文显示乱码

代码中使用 UTF-8 编码保存文件，Windows 终端可能需要设置编码：
```bash
chcp 65001
```

## 文件结构

```
openclaw-workspace/
├── browserbot.py           # 主程序
├── cmd.py                   # 测试脚本
├── output.json             # 输出结果
└── BROWSERBOT.md          # 本文档
```

## 进阶功能

### 自定义 Chrome 选项

编辑 `browser_controller.py` 中的 `chrome_options`：

```python
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1280,720")
chrome_options.add_argument("--start-maximized")
# 添加自定义选项
chrome_options.add_argument("--incognito")  # 隐身模式
chrome_options.add_argument("--headless")   # 无头模式
```

### 添加更多 API 端点

在 `execute` 函数中添加新的 action 处理：

```python
elif action == 'new_action':
    # 处理新功能
    result['data'] = "..."
```

## 许可

MIT License

---

*由 TacticBot 为 OpenClaw 社区编写*
