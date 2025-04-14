import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv()

client = OpenAI()

api_key = "6QA5BEYQ5U5D9XM5"

def get_stock_price(symbol:str):
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={api_key}"
  response = requests.get(url)
  if response.status_code == 200:
    return f"The stock price for {symbol} is {response.text}."
  return "Something went wrong"

def get_stock_news(symbol:str):
  url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&sort=LATEST&limit=20&apikey={api_key}"
  print("🔨 Tool Called: get_stock_news", symbol)
  response = requests.get(url)
  if response.status_code == 200:
    return f"The stock news for {symbol} is {response.text}."
  return "Something went wrong"


avaiable_tools = {
    "get_stock_price": {
        "fn": get_stock_price,
        "description": "Takes a stock symbol as an input and returns the current stock price for the symbol"
    },
    "run_command": {
        "fn": get_stock_news,
        "description": "Takes a stock symbol as an input and returns the current news for the symbol"
    }
}

system_prompt = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, resarch, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - get_stock_price: Takes a stock symbol as an input and returns the current stock price for the symbol
    - get_stock_news: Takes a stock symbol as an input and returns the current news for the symbol
    
    Example:
    User Query: It is right time to buy IBM stock?
    Output: {{ "step": "plan", "content": "The user is interseted in stock data of IBM" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_stock_price" }}
    Output: {{ "step": "action", "function": "get_stock_price", "input": "IBM" }}
    Output: {{ "step": "observe", "output": "The IBM stock historycal daly data is lower than past 5 years " }}
    Output: {{ "step": "observe", "output": "The stock price for IBM is 123.45." }}
    Output: {{ "step": "output", "content": "This is a good time to buy IBM stock as the stock price is lower than past 5 years and current stock price is 123.45 and stock news is positive" }}
"""

messages = [
    { "role": "system", "content": system_prompt }
]


while True:
    user_query = input('> ')
    messages.append({ "role": "user", "content": user_query })

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({ "role": "assistant", "content": json.dumps(parsed_output) })

        if parsed_output.get("step") == "plan":
            print(f"🧠: {parsed_output.get("content")}")
            continue
        
        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if avaiable_tools.get(tool_name, False) != False:
                output = avaiable_tools[tool_name].get("fn")(tool_input)
                messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output":  output}) })
                continue
        
        if parsed_output.get("step") == "output":
            print(f"🤖: {parsed_output.get("content")}")
            break


  

