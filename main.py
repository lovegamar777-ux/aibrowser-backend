from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AiBrowser Chat</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; text-align: center; padding-top: 50px; }
            h1 { color: #38bdf8; }
        </style>
    </head>
    <body>
        <h1>AiBrowser Backend Live Hai!</h1>
        <p>FastAPI server successfully chal raha hai.</p>
    </body>
    </html>
    """