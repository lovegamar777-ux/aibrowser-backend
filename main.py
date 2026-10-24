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
    image_data = data.get("image", None) # अगर यूजर ने फोटो भेजी हो
    
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
        {"role": "system", "content": "आप AiBrowser के एडवांस एआई असिस्टेंट हैं। उपयोगकर्ता का नाम रूगनाथ है। हमेशा हिंदी में मदद करें।"}
    ]

    if image_data:
        # अगर इमेज है तो विजन फॉर्मेट में भेजेंगे
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AiBrowser AI Chat</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #e9ecef; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            #chat-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
            .message { padding: 12px 18px; border-radius: 15px; max-width: 80%; line-height: 1.5; word-wrap: break-word; font-size: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
            .user-message { background-color: #007bff; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
            .ai-message { background-color: white; color: #333; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #ddd; }
            
            #input-container { display: flex; align-items: center; padding: 12px; background-color: white; border-top: 1px solid #ddd; gap: 10px; }
            #user-input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 25px; outline: none; font-size: 16px; transition: border 0.3s; }
            #user-input:focus { border-color: #007bff; }
            
            .action-btn { background-color: #f8f9fa; border: 1px solid #ccc; color: #333; padding: 10px 14px; border-radius: 50%; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
            .action-btn:hover { background-color: #e2e6ea; }
            #send-btn { background-color: #007bff; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: bold; }
            #send-btn:hover { background-color: #0056b3; }
            
            #image-preview { max-width: 100px; max-height: 100px; display: none; border-radius: 8px; margin-bottom: 5px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <header>🚀 AiBrowser AI Assistant</header>
        
        <div id="chat-container">
            <div class="message ai-message">नमस्ते रूगनाथ! मैं आपका AiBrowser एआई असिस्टेंट हूँ। अब आप मुझसे बोलकर, लिखकर या फोटो भेजकर बात कर सकते हैं। बताइए, आज क्या मदद करूँ?</div>
        </div>

        <div style="padding: 0 15px;">
            <img id="image-preview" src="" alt="Preview" />
        </div>

        <div id="input-container">
            <!-- फोटो अपलोड बटन -->
            <label class="action-btn" title="फोटो अपलोड करें">
                📷 <input type="file" id="image-file" accept="image/*" style="display: none;" onchange="previewImage(event)">
            </label>
            
            <!-- वॉयस इनपुट (बोलकर टाइप करने के लिए) -->
            <button class="action-btn" onclick="startVoiceInput()" title="बोलकर टाइप करें">🎙️</button>

            <input type="text" id="user-input" placeholder="यहाँ अपना सवाल लिखें..." onkeypress="if(event.key==='Enter') sendMessage()" />
            
            <button id="send-btn" onclick="sendMessage()">भेजें</button>
        </div>

        <script>
            let base64Image = null;

            function previewImage(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        base64Image = e.target.result;
                        const preview = document.getElementById('image-preview');
                        preview.src = base64Image;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }

            // बोलकर टाइप करने का फीचर (Speech to Text)
            function startVoiceInput() {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {
                    alert("आपका ब्राउज़र वॉइस रिकग्निशन सपोर्ट नहीं करता है।");
                    return;
                }
                const recognition = new SpeechRecognition();
                recognition.lang = 'hi-IN'; // हिंदी भाषा
                recognition.start();

                recognition.onresult = function(event) {
                    const speechText = event.results[0][0].transcript;
                    document.getElementById('user-input').value = speechText;
                };
            }

            // एआई की आवाज में बोलकर बताने का फीचर (Text to Speech)
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

                // यूजर का मैसेज स्क्रीन पर दिखाएं
                const userMsg = document.createElement('div');
                userMsg.className = 'message user-message';
                userMsg.innerText = text + (base64Image ? " [फोटो संलग्न]" : "");
                chatContainer.appendChild(userMsg);

                const currentImage = base64Image;
                input.value = '';
                base64Image = null;
                document.getElementById('image-preview').style.display = 'none';
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
                    
                    // एआई का जवाब बोलकर भी सुनाएगा
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