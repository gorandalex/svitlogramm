import openai

import uvicorn

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = 'OPENAI_API_KEY'

    class Config:
        env_file = '.env'


settings = Settings()
openai.api_key = settings.OPENAI_API_KEY


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def index(request: Request, tag: str = Form(...)):
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=generate_prompt(tag),
        temperature=0.6,
    )
    result = response.choices[0].text
    return templates.TemplateResponse("index.html", {"request": request, "result": result})


def generate_prompt(tag):
    return """Suggest three possible tags for a photo.

Photo: Summer landscape of Ukrainian village.
Tags: summer_vibes, lovely_nature, ukrainian_beauty
Photo: Family walking in the park holding hands
Tags: family_time, happy_moments, love_them
Photo: {}
Tags:""".format(
        tag.lowercase()
    )


if __name__ == "__main__":
    uvicorn.run('app:app', host="localhost", port=5001, reload=True)
