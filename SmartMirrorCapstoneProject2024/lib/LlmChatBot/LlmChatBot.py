from openai import OpenAI
from os import getenv

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

class AskChatBot:
    def __init__(self) -> None:
        pass
    def setNotifier(self, notifier):
        self.notifier = notifier
    def ask(self, msg):
        completion = client.chat.completions.create(
        model="google/gemma-7b-it:free",
        messages=[
            {
            "role": "user",
            "content": ""+ str(msg),
            },
        ],
        )
        self.notifier(str(completion.choices[0].message.content))
# if __name__== "__main__":
#     a = AskChatBot()
#     def b(msg):
#         print(msg)
#     a.setNotifier(b)
#     a.ask(" how many legs does an ant have")

