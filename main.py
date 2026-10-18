import os
import subprocess
import sys

ASSISTANT_FOLDER = r"C:\Users\gkgup\Desktop\Ai_Assistant"

def register_globally():
    """यह फंक्शन आपके टूल को पूरे कंप्यूटर के CMD में हमेशा के लिए सेव कर देगा"""
    bat_path = os.path.join(ASSISTANT_FOLDER, "fix.bat")
    
    # अगर fix.bat नहीं बनी है, तो कोड खुद इसे बना देगा
    if not os.path.exists(bat_path):
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(f'@echo off\npython "{os.path.join(ASSISTANT_FOLDER, "main.py")}" %*\n')
        print("⚡ [SYSTEM] जादुई शॉर्टकट बैकग्राउंड में तैयार कर दिया गया है।")

    # विंडोज के PATH में इस फोल्डर को ऑटो-रजिस्टर करना
    current_path = os.environ.get("PATH", "")
    if ASSISTANT_FOLDER.lower() not in current_path.lower():
        print("⚙ [SYSTEM] टूल को पूरे कंप्यूटर के लिए परमानेंट सेव कर रहे हैं...")
        # विंडोज रजिस्ट्री में पाथ जोड़ना
        subprocess.run(f'setx PATH "%PATH%;{ASSISTANT_FOLDER}"', shell=True, stdout=subprocess.DEVNULL)
        print("✅ [SYSTEM] टool पूरे कंप्यूटर में सेव हो चुका है भाई! (बदलाव लागू करने के लिए CMD को एक बार बंद करके दोबारा खोलें)")

def run_script(script_name):
    script_path = os.path.join(ASSISTANT_FOLDER, script_name)
    if not os.path.exists(script_path):
        print(f"❌ Error: {script_name} फाइल नहीं मिली।")
        return "NOT_FOUND"
        
    print(f"\n🚀 [MAIN] {script_name} को रन कर रहे हैं...")
    result = subprocess.run(["python", script_path], shell=True)
    return result.returncode

if __name__ == "__main__":
    # सबसे पहले टूल को कंप्यूटर में हमेशा के लिए रजिस्टर करेंगे
    register_globally()

    print("\n==============================================")
    print("🤖 AI ASSISTANT: यूनिवर्सल ऑटो-बिल्ड सिस्टम शुरू 🤖")
    print("==============================================")
    
    # करंट फोल्डर में एरर चेक करना
    builder_status = run_script("builder.py")
    
    error_log_file = os.path.join(ASSISTANT_FOLDER, "error_log.txt")
    
    if os.path.exists(error_log_file):
        print("\n⚠ [MAIN] बिल्ड फेल हुआ है। ऑटो-फिक्सर चालू कर रहे हैं...")
        run_script("fixer.py")
        print("\n🔄 [MAIN] एरर ठीक करने की कोशिश की गई है। दोबारा टेस्ट करने के लिए फिर से 'fix' चलाएं।")
    else:
        print("\n🎉 [MAIN] सब कुछ परफेक्ट है भाई! कोई एरर नहीं मिला और ऐप का बिल्ड तैयार है।")