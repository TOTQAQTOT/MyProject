from openai import OpenAI

client = OpenAI(
    api_key="sk-414f5b8d5c9445e9ae48681378014099", 
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat", 
    messages=[
        {"role": "system", "content": "你是一个有用的助手"},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=1.3,
    max_tokens=2048,
    stream=False,
)
print(response.choices[0].message.content)