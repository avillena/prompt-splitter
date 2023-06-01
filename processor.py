# %%
def get_text_parts(text):
    lines = text.splitlines()
    current_part = None

    for line in lines:
        if line.startswith(f"{'#'*30} PART"):
            if current_part is not None:
                yield current_part.strip()
            current_part = ""
        else:
            if current_part is not None:
                current_part += line + "\n"

    if current_part is not None:
        yield current_part.strip()

# %%
from pathlib import Path
#filepath = Path("example_parts.txt")
filepath = Path("resumen_parts.txt")
with open(str(filepath), "r", encoding="utf-8") as file:
    text = file.read()
    for part in get_text_parts(text):
        print(part)
        print("--------------")

a_part = next(get_text_parts(text))

# %%
import openai

def ask_gpt(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message.strip()

from chromadb import ChromaDB

chromadb = ChromaDB(ask_gpt)

from chatgpt_wrapper import ApiBackend
from chatgpt_wrapper.core.config import Config

config = Config()
config.set('chat.model', 'gpt4')
bot = ApiBackend(config)

while True:
    user_input = input("User: ")
    bot_response = chromadb.get_response(user_input)
    print("Bot:", bot_response)
    chromadb.add_to_memory(user_input, bot_response)
    gpt_response = bot.ask(bot_response)
    print("GPT:", gpt_response)
    chromadb.add_to_memory(bot_response, gpt_response)
