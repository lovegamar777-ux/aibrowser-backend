from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            header {
                background-color: #007bff;
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
            }
            #chat-container {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .message {
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 80%;
                line-height: 1.4;
            }
            .user-message {
                background-color: #007bff;
                color: white;
                align-self: flex-end;
            }
            .ai-message {
                background-color: white;
                color: #333;
                align-self: flex-start;
                border: 1px solid #ddd;
            }
            #input-container {
                display: flex;
                padding: 10px;
                background-color: white;
                border-top: 1px solid #ddd;
            }
            #user-input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                outline: none;
                font-size: 16px;
            }
            #send-btn {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                margin-left: 10px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <header>🤖 AiBrowser AI Assistant</header>
        
        <div id="chat-container">
            <div class="message ai-message">नमस्ते रूगनाथ! मैं आपका अपना AI असिस्टेंट हूँ। बताइए, आज आपकी क्या मदद करूँ?</div>
        </div>

        <div id="input-container">
            <input type="text" id="user-input" placeholder="यहाँ अपना सवाल लिखें..." />
            <button id="send-btn" onclick="sendMessage()">भेजें</button>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('user-input');
                const text = input.value.trim();
                if (!text) return;

                const chatContainer = document.getElementById('chat-container');

                // यूजर का मैसेज जोड़ें
                const userMsg = document.createElement('div');
                userMsg.className = 'message user-message';
                userMsg.innerText = text;
                chatContainer.appendChild(userMsg);

                input.value = '';
                chatContainer.scrollTop = chatContainer.scrollHeight;

                // अभी के लिए डमी रिस्पॉन्स (बाद में इसे AI API से जोड़ेंगे)
                setTimeout(() => {
                    const aiMsg = document.createElement('div');
                    aiMsg.className = 'message ai-message';
                    aiMsg.innerText = "सर्च सर्वर से जुड़ गया है! बहुत जल्द यहाँ असली AI जवाब देगा।";
                    chatContainer.appendChild(aiMsg);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }, 1000);
            }
        </script>
    </body>
    </html>
    """