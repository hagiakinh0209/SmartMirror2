import subprocess
import json
api_key="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"

class AskChatBot:
    def __init__(self) -> None:
        pass
    def setNotifier(self, notifier):
        self.notifier = notifier
    def ask(self, msg):
        cmd = '''curl https://openrouter.ai/api/v1/chat/completions \\
                -H "Content-Type: application/json" \\
                -H "Authorization: Bearer ''' + api_key + '''" \\
                -d \'{
                "model": "google/gemma-7b-it:free",
                "messages": [
                    {"role": "user", "content": "''' + msg + '''"}
                ]
                }\''''
        output = subprocess.check_output(cmd, shell=True)       
        self.notifier(json.loads(output.decode("utf-8"))["choices"][0]["message"]["content"])
if __name__== "__main__":
    a = AskChatBot()
    def b(msg):
        print(msg)
    a.setNotifier(b)
    a.ask(" how many legs does an ant have")

