from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import List

router = APIRouter(prefix="/openai/chat", tags=["Chat"])


class ChatInput(BaseModel):
    question: str
    answer: str


@router.post("/chat", response_model=ChatInput, tags=["Chat"])
async def chat(chat_input: ChatInput):
    # Here you can implement the logic to interact with OpenAI or any other chatbot model
    # For simplicity, this example will echo the input question and answer
    return chat_input


@router.get("/docs", include_in_schema=False)
async def get_documentation():
    from fastapi import FastAPI
    import shutil

    app = FastAPI()
    app.include_router(router)

    # Generate Swagger documentation
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi():
        return app.openapi()

    # Serve Swagger UI
    @app.get("/", include_in_schema=False)
    async def get_swagger_ui():
        swagger_ui_path = shutil.which("swagger-ui")
        if swagger_ui_path is None:
            raise Exception("Swagger UI not found.")
        return RedirectResponse(url="/docs")

    return app
