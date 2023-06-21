from fastapi import APIRouter, Depends
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from fastapi_limiter.depends import RateLimiter
from config import settings
import openai

router = APIRouter(prefix="/openai", tags=["Chat"])
loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor()


openai.api_key = settings.OPENAI_API_KEY


async def start_chat(prompt):
    assistant = "You are a helpful and creative assistant."
    """prompt = Reply to a question in a fun and creative way. 
    The answer has to be in English. The answer has to be no longer than 100 symbols. 
    No recommendations or additional explanations."""
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt="Q: {}?\nA:".format(prompt),
        max_tokens=200,
        n=1,
        temperature=0.8,
    )
    return response["choices"][0]["text"].strip()


<<<<<<< HEAD
@router.get("/", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def generate_response(prompt):
    response = await start_chat(prompt)
=======
@router.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def generate_response(data: str):
    response = await loop.run_in_executor(executor, functools.partial(start_chat, data))
>>>>>>> 49b267301190ca4369de5487f955505ed080889d
    return response
