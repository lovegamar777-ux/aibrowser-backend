from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os
import requests

app = FastAPI()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def get_active_groq_model(headers):
    try:
        models_url = "https://api.groq.com/openai/v1/models"
        res = requests.get(models_url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            model_list = [m['id'] for m in data.get('data', [])]
            for preferred in ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
                if preferred in model_list:
                    return preferred
            if model_list:
                return model_list[0]
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")
    image_data = data.get("image", None)
    
    if not user_prompt and not image_data:
        return JSONResponse({"response": "कृपया कोई सवाल पूछें या फोटो अपलोड करें।", "status": "error"})

    if not GROQ_API_KEY:
        return JSONResponse({"response": "Groq API Key सेट नहीं है।", "status": "error"})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    active_model = get_active_groq_model(headers)
    url = "https://api.groq.com/openai/v1/chat/completions"

    messages = [
        {"role": "system", "content": "आप Jarvis हैं, AiBrowser के पर्सनल एआई असिस्टेंट। उपयोगकर्ता का नाम रूगनाथ है। हमेशा हिंदी में मदद करें।"}
    ]

    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt if user_prompt else "इस फोटो में क्या है बताएं।"},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        })
    else:
        messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": active_model,
        "messages": messages
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        if res.status_code == 200:
            res_data = res.json()
            ai_text = res_data['choices'][0]['message']['content']
            return JSONResponse({"response": ai_text})
        else:
            return JSONResponse({"response": f"API एरर ({res.status_code}): {res.text}"})
    except Exception as e:
        return JSONResponse({"response": f"कनेक्शन एरर: {str(e)}"})

@app.get("/", response_class=HTMLResponse)
async def chat_home():
    return """
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Jarvis AI Chat</title>
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { font-family: 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            #chat-container { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
            .message { padding: 12px 18px; border-radius: 18px; max-width: 85%; line-height: 1.5; word-wrap: break-word; font-size: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.08); }
            .user-message { background-color: #007bff; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
            .ai-message { background-color: white; color: #333; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #e0e0e0; }
            
            .input-wrapper { padding: 10px 15px; background: transparent; display: flex; justify-content: center; position: relative; }
            #input-container { display: flex; align-items: center; background-color: white; border: 1px solid #dcdcdc; border-radius: 30px; padding: 6px 12px; width: 100%; max-width: 700px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); gap: 8px; }
            
            #user-input { flex: 1; border: none; outline: none; font-size: 16px; background: transparent; color: #333; padding: 8px 0; }
            
            .icon-btn { background: none; border: none; font-size: 22px; cursor: pointer; color: #555; display: flex; align-items: center; justify-content: center; padding: 6px; border-radius: 50%; width: 40px; height: 40px; }
            .icon-btn:active { background-color: #f0f0f0; }
            
            #send-btn { background-color: #007bff; color: white; border: none; width: 38px; height: 38px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
            
            /* अति-प्रीमियम पॉपअप कार्ड डिज़ाइन */
            #upload-menu {
                display: none;
                position: absolute;
                bottom: 75px;
                left: 16px;
                right: 16px;
                background: rgba(255, 255, 255, 0.96);
                backdrop-filter: blur(12px);
                border: 1px solid #e2e8f0;
                border-radius: 22px;
                box-shadow: 0 14px 36px rgba(0, 0, 0, 0.15);
                padding: 16px;
                display: flex;
                justify-content: space-around;
                align-items: center;
                z-index: 100;
            }
            .menu-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 12px 22px;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                font-weight: 600;
                color: #1e293b;
                gap: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            }
            .menu-item span {
                font-size: 26px;
            }
            .menu-item:active {
                background: #e2e8f0;
                transform: scale(0.95);
            }

            #image-preview-container { padding: 0 20px; display: none; margin-bottom: 5px; }
            #image-preview { max-width: 80px; max-height: 80px; border-radius: 8px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <header>🤖 Jarvis AI Assistant</header>
        
        <div id="chat-container">
            <div class="message ai-message">नमस्ते रूगनाथ! मैं आपका Jarvis एआई असिस्टेंट हूँ। बताइए, आज आपकी क्या मदद करूँ?</div>
        </div>

        <div id="image-preview-container">
            <img id="image-preview" src="" alt="Preview" />
        </div>

        <div class="input-wrapper">
            <!-- प्लस बटन दबाने पर दिखने वाला प्रीमियम पॉपअप मेनू -->
            <div id="upload-menu" style="display: none;">
                <div class="menu-item" onclick="triggerPhoto()">
                    <span>🖼️</span> फ़ोटो
                </div>
                <div class="menu-item" onclick="triggerCamera()">
                    <span>📷</span> कैमरा
                </div>
                <div class="menu-item" onclick="triggerFile()">
                    <span>📁</span> फ़ाइलें
                </div>
            </div>

            <div id="input-container">
                <!-- बाईं तरफ प्लस (+) बटन -->
                <button type="button" class="icon-btn" onclick="toggleUploadMenu(event)" title="जोड़ें">➕</button>
                
                <!-- हिडन फाइल इनपुट्स -->
                <input type="file" id="file-photo" accept="image/*" style="display: none;" onchange="previewImage(event)">
                <input type="file" id="file-camera" accept="image/*" capture="environment" style="display: none;" onchange="previewImage(event)">
                <input type="file" id="file-any" accept="*/*" style="display: none;" onchange="previewImage(event)">

                <input type="text" id="user-input" placeholder="Jarvis से पूछें..." onkeypress="if(event.key==='Enter') sendMessage()" />

                <button type="button" class="icon-btn" id="mic-btn" onclick="startVoiceInput()" title="बोलकर टाइप करें">🎙️</button>
                <button type="button" id="send-btn" onclick="sendMessage()" title="भेजें">➤</button>
            </div>
        </div>

        <script>
            let base64Image = null;

            function toggleUploadMenu(event) {
                event.stopPropagation();
                const menu = document.getElementById('upload-menu');
                menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
            }

            window.onclick = function() {
                const menu = document.getElementById('upload-menu');
                if (menu) menu.style.display = 'none';
            }

            function triggerPhoto() { document.getElementById('file-photo').click(); }
            function triggerCamera() { document.getElementById('file-camera').click(); }
            function triggerFile() { document.getElementById('file-any').click(); }

            function previewImage(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        base64Image = e.target.result;
                        const previewContainer = document.getElementById('image-preview-container');
                        const preview = document.getElementById('image-preview');
                        preview.src = base64Image;
                        previewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }

            function startVoiceInput() {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {
                    alert("आपके ब्राउज़र में वॉइस इनपुट सपोर्ट नहीं है।");
                    return;
                }
                try {
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'hi-IN';
                    const micBtn = document.getElementById('mic-btn');
                    micBtn.style.color = 'red';

                    recognition.onresult = function(event) {
                        const speechText = event.results[0][0].transcript;
                        document.getElementById('user-input').value = speechText;
                        micBtn.style.color = '#555';
                    };
                    recognition.onerror = function() { micBtn.style.color = '#555'; };
                    recognition.onend = function() { micBtn.style.color = '#555'; };
                    recognition.start();
                } catch(e) {
                    alert("माइक्रोफोन एरर: " + e.message);
                }
            }

            function speakText(text) {
                if ('speechSynthesis' in window) {
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = 'hi-IN';
                    window.speechSynthesis.speak(utterance);
                }
            }

            async function sendMessage() {
                const input = document.getElementById('user-input');
                const text = input.value.trim();
                if (!text && !base64Image) return;

                const chatContainer = document.getElementById('chat-container');

                const userMsg = document.createElement('div');
                userMsg.className = 'message user-message';
                userMsg.innerText = text + (base64Image ? " [फाइल/फोटो संलग्न]" : "");
                chatContainer.appendChild(userMsg);

                const currentImage = base64Image;
                input.value = '';
                base64Image = null;
                document.getElementById('image-preview-container').style.display = 'none';
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
                        body: JSON.stringify({ prompt: text, image: currentImage })
                    });
                    const data = await response.json();
                    loadingMsg.innerText = data.response;
                    speakText(data.response);
                } catch (err) {
                    loadingMsg.innerText = "माफ कीजिये, सर्वर से जवाब नहीं मिल सका।";
                }
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
    </body>
    </html>
    """