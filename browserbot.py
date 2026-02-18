"""
OpenClaw Browser Controller
AI-controlled browser automation

Usage:
  python browser_controller.py

Server runs on http://localhost:8765
"""

import os
# Disable proxy for localhost
os.environ['no_proxy'] = 'localhost,127.0.0.1'

from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import uuid
import time

app = Flask(__name__)
CORS(app)

# Configure Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,720")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--profile-directory=Default")

# Initialize driver
driver = None

def get_driver():
    global driver
    if driver is None:
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            raise
    return driver

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok", 
        "browser": "connected" if driver else "disconnected"
    })

@app.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.json
        action = data.get('action', '')
        
        result = {"action": action, "success": True}
        
        # Most actions require browser
        if action not in ['health', 'get_status']:
            d = get_driver()
        
        if action == 'navigate':
            url = data.get('url', '')
            d.get(url)
            time.sleep(1)  # Wait for page load
            result['url'] = d.current_url
            result['title'] = d.title
            
        elif action == 'get_html':
            result['html'] = d.page_source
            
        elif action == 'get_text':
            selector = data.get('selector', 'body')
            try:
                element = d.find_element(By.CSS_SELECTOR, selector)
                result['text'] = element.text
            except:
                result['text'] = ""
                
        elif action == 'screenshot':
            filename = f"screenshot_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(os.path.dirname(__file__), filename)
            d.save_screenshot(filepath)
            with open(filepath, 'rb') as f:
                result['image'] = base64.b64encode(f.read()).decode()
            os.remove(filepath)
            
        elif action == 'click':
            selector = data.get('selector', '')
            wait = WebDriverWait(d, 10)
            element = wait.until(EC.element_to_be_clickable(By.CSS_SELECTOR, selector))
            element.click()
            
        elif action == 'type':
            selector = data.get('selector', '')
            text = data.get('text', '')
            element = d.find_element(By.CSS_SELECTOR, selector)
            element.clear()
            element.send_keys(text)
            
        elif action == 'scroll':
            pixels = data.get('pixels', 300)
            d.execute_script(f"window.scrollBy(0, {pixels})")
            
        elif action == 'evaluate':
            script = data.get('script', '')
            result['result'] = d.execute_script(script)
            
        elif action == 'get_title':
            result['title'] = d.title
            
        elif action == 'get_url':
            result['url'] = d.current_url
            
        elif action == 'back':
            d.back()
            result['url'] = d.current_url
            
        elif action == 'forward':
            d.forward()
            result['url'] = d.current_url
            
        elif action == 'refresh':
            d.refresh()
            result['url'] = d.current_url
            
        else:
            result['success'] = False
            result['error'] = f"Unknown action: {action}"
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/close', methods=['POST'])
def close_browser():
    global driver
    if driver:
        driver.quit()
        driver = None
    return jsonify({"status": "closed"})

if __name__ == '__main__':
    print("Browser Controller running on http://localhost:8765")
    print("Ready to receive commands from OpenClaw")
    app.run(port=8765, debug=False)
