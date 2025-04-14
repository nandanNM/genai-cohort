from openai import OpenAI
from dotenv import load_dotenv
client = OpenAI()

result = client.chat.completions.create(
    model="gpt-4",
   messages=[
     {"role": "user", "content": "Hay thare!"},
   ]
)

print(result.choices[0].message.content)
