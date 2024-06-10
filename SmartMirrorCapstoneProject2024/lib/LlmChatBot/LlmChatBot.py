import subprocess
import json
api_key_gema_free="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"
api_key_gemini="AIzaSyChdoecMVqbGW7e9Qseuj51fV5Fz3Ejm0c"


class AskChatBot:
    def __init__(self, model = "gemini") -> None:
        self.model = model
    def setNotifier(self, notifier):
        self.notifier = notifier
    def ask(self, msg):
        cmd =""
        try:
            if self.model == "gema free":
                cmd =  '''curl https://openrouter.ai/api/v1/chat/completions \\
                        -H "Content-Type: application/json" \\
                        -H "Authorization: Bearer ''' + api_key_gema_free + '''" \\
                        -d \'{
                        "model": "google/gemma-7b-it:free",
                        "messages": [
                            {"role": "user", "content": "''' + msg + '''"}
                        ]
                        }\''''
                
            elif self.model == "gemini":
                cmd = '''curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=''' + api_key_gemini + '''" \\
                    -H 'Content-Type: application/json' \\
                    -X POST \\
                    -d '{
                    "contents": [{
                        "parts":[{
                        "text": "'''+ msg +'''"}]}]}'

                '''
            output = subprocess.check_output(cmd, shell=True)     

            if self.model == "gema free":
                self.notifier(json.loads(output.decode("utf-8"))["choices"][0]["message"]["content"])
            elif self.model == "gemini":
                self.notifier(json.loads(output.decode("utf-8"))["candidates"][0]["content"]["parts"][0]["text"])
        except:
            import traceback
            traceback.print_exc()
if __name__== "__main__":
    a = AskChatBot()
    def b(msg):
        print(msg)
    a.setNotifier(b)
    a.ask(" cách nấu canh chua")

