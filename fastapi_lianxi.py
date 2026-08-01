from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,HTTPException
import asyncio
from fastapi.responses import StreamingResponse
from langchain_lianxi import rag_chain
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class queryrequest(BaseModel):
    query: str
async def rag_response(query):
    print("开始处理:", query)
    try:

        async for chunk in rag_chain.astream(query):
            text = (
                chunk.content
                if hasattr(chunk, "content")
                else chunk
            )

            yield f"data:{text}\n\n"


    except Exception as e:

        yield f"data:发生错误:{str(e)}\n\n"

@app.post("/chat")
async def chat(request:queryrequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")


    return StreamingResponse(
        rag_response(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        })
#uvicorn fastapi_lianxi:app --reload(启动后端)

#npm run dev（启动前端）(启动前端前先进入cd C:\Users\laixiaohan\PycharmProjects\rag_frontend)