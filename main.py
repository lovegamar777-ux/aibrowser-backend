from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

# Render से आपकी GROQ_API_KEY उठाएगा
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")
    
    if not user_prompt:
        return JSONResponse({"response": "कृपया कोई सवाल पूछें।", "status": "error"})

    if not GROQ_API_KEY:
        return JSONResponse({"response": "Groq API Key सेट नहीं है।", "status": "error"})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "आप AiBrowser के एआई असिस्टेंट हैं। उपयोगकर्ता का नाम रूगनाथ है। हमेशा हिंदी में मदद करें।"},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        
        try:
            res_data = res.json()
        except Exception:
            res_data = res.text

        if res.status_code == 200:
            if isinstance(res_data, dict) and 'choices' in res_data:
                ai_text = res_data['choices'][0]['message']['content']
                return JSONResponse({"response": ai_text})
            else:
                return JSONResponse({"response": f"अमान्य रिस्पॉन्स: {res_data}"})
        else:
            error_msg = str(res_data)
            if isinstance(res_data, dict):
                err_obj = res_data.get('error')
                if isinstance(err_obj, dict):
                    error_msg = err_obj.get('message', str(res_data))
                elif isinstance(err_obj, str):
                    error_msg = err_obj
            
            return JSONResponse({"response": f"Groq API एरर ({res.status_code}): {error_msg}"})
            
    except Exception as e:
        return JSONResponse({"response": f"कनेक्शन एरर: {str(e)}"})

@app.get("/", response_class=HTMLResponse)
async def chat_home():
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AiBrowser AI Chat</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background-color: #007bff; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; }
            #chat-container { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
            .message { padding: 10px 15px; border-radius: 10px; max-width: 80%; line-height: 1.4; word-wrap: break-word; }
            .user-message { background-color: #007bff; color: white; align-self: flex-end; }
            .ai-message { background-color: white; color: #333; align-self: flex-start; border: 1px solid #ddd; }
            #input-container { display: flex; padding: 10px; background-color: white; border-top: 1px solid #ddd; }
            #user-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; outline: none; font-size: 16px; }
            #send-btn { background-color: #007bff; color: white; border: none; padding: 10px 20px; margin-left: 10px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        </style>
    </head>
    <body>
        <header>🤖 AiBrowser AI Assistant</header>
        
        <div id="chat-container">
            <div class="message ai-message">नमस्ते रूगनाथ! मैं आपका AiBrowser AI असिस्टेंट हूँ। बताइए, आज आपकी क्या मदद करूँ?</div>
        </div>

        <div id="input-container">
            <input type="text" id="user-input" placeholder="यहाँ अपना सवाल लिखें..." onkeypress="if(event.key==='Enter') sendMessage()" />
            <button id="send-btn" onclick="sendMessage()">भेजें</button>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('user-input');
                const text = input.value.trim();
                if (!text) return;

                const chatContainer = document.getElementById('chat-container');

                const userMsg = document.createElement('div');
                userMsg.className = 'message user-message';
                userMsg.innerText = text;
                chatContainer.appendChild(userMsg);

                input.value = '';
                chatContainer.scrollTop = chatContainer.scrollHeight;

                const loadingMsg = document.createElement('div');
                loadingMsg.className = 'message ai-message';
                loadingMsg.innerText = 'सोच रहा हूँ... 🤔';
                chatContainer.appendChild(loadingMsg);
                chatContainer.scrollTop = chatContainer.scrollHeight;

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: text })
                    });
                    const data = await response.json();
                    loadingMsg.innerText = data.response;
                } catch (err) {
                    loadingMsg.innerText = "माफ कीजिये, सर्वर से जवाब नहीं मिल सका।";
                }
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
    </body>
    </html>
    """