from fastapi import APIRouter
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import List
import openai

router = APIRouter(prefix="/openai", tags=["Chat"])
loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor()

def start_chat():
    assistant = "You are a helpful and creative assistant."
    prompt = """Reply to a question in a fun and creative way. 
    The answer has to be in English. The answer has to be no longer than 100 symbols. 
    No recommendations or additional explanations."""
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": assistant},
        {"role": "user", "content": prompt}
    ],
    max_tokens = 100,
    n=1,
    temperature= 0.6,
)
    return response["choices"][0]["text"].strip()

async def generate_response(prompt):
    response = await loop.run_in_executor(executor, functools.partial(start_chat, prompt))
    return response
