import json
import os
from typing import AsyncIterable

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from openai._streaming import Stream
from openai._types import NOT_GIVEN
from openai.types.chat import ChatCompletion, ChatCompletionChunk

import helpers

debug = os.environ.get("GPTSCRIPT_DEBUG", "false") == "true"


def log(*args):
    if debug:
        print(*args)


app = FastAPI()


@app.middleware("http")
async def log_body(request: Request, call_next):
    body = await request.body()
    log("REQUEST BODY: ", body)
    return await call_next(request)


@app.get("/")
async def get_root():
    return "ok"


# Only needed when running standalone. With GPTScript, the `id` returned by this endpoint must match the model (deployment) you are passing in.
@app.get("/v1/models")
async def list_models() -> JSONResponse:
    return JSONResponse(content={"data": [{"id": "gpt-4", "name": "Your model"}]})


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.body()
    data = json.loads(data)

    tools = data.get("tools", NOT_GIVEN)

    if tools is not NOT_GIVEN:
        tool_choice = 'auto'
    else:
        tool_choice = NOT_GIVEN

    temperature = data.get("temperature", NOT_GIVEN)
    if temperature is not NOT_GIVEN:
        temperature = float(temperature)

    stream = data.get("stream", False)

    config = await helpers.get_azure_config(data["model"])

    client = helpers.client(
        endpoint=config.endpoint,
        deployment_name=config.deployment_name,
        api_key=config.api_key
    )
    try:
        res: Stream[ChatCompletionChunk] | ChatCompletion = client.chat.completions.create(model=data["model"],
                                                                                           messages=data["messages"],
                                                                                           tools=tools,
                                                                                           tool_choice=tool_choice,
                                                                                           temperature=temperature,
                                                                                           stream=stream
                                                                                           )
        if not stream:
            return JSONResponse(content=jsonable_encoder(res))

        return StreamingResponse(convert_stream(res), media_type="application/x-ndjson")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")


async def convert_stream(stream: Stream[ChatCompletionChunk]) -> AsyncIterable[str]:
    for chunk in stream:
        log("CHUNK: ", chunk.model_dump_json())
        yield "data: " + str(chunk.model_dump_json()) + "\n\n"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)
