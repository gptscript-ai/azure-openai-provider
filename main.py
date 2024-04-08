import json
import os
import sys
from typing import AsyncIterable

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.resource import ResourceManagementClient
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from openai import AzureOpenAI, OpenAI
from openai._streaming import Stream
from openai.types.chat import ChatCompletionChunk

debug = os.environ.get("GPTSCRIPT_DEBUG", "false") == "true"


def log(*args):
    if debug:
        print(*args)


app = FastAPI()
credential = DefaultAzureCredential()
if 'AZURE_SUBSCRIPTION_ID' not in os.environ:
    print("Set AZURE_SUBSCRIPTION_ID environment variable")
    sys.exit(1)
else:
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

token = credential.get_token("https://management.azure.com/.default")
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}


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

    try:
        tools = data["tools"]
    except Exception as e:
        log("No tools provided: ", e)
        tools = []
    client = await get_azure_config(data["model"])
    res = client.chat.completions.create(model=data["model"], messages=data["messages"], tools=tools,
                                         tool_choice="auto",
                                         stream=True)
    return StreamingResponse(convert_stream(res), media_type="application/x-ndjson")


async def convert_stream(stream: Stream[ChatCompletionChunk]) -> AsyncIterable[str]:
    for chunk in stream:
        log("CHUNK: ", chunk.json())
        yield "data: " + str(chunk.json()) + "\n\n"


async def list_resource_groups(client: ResourceManagementClient):
    group_list = client.resource_groups.list()

    column_width = 40
    print("Resource Group".ljust(column_width) + "Location")
    print("-" * (column_width * 2))
    for group in list(group_list):
        print(f"{group.name:<{column_width}}{group.location}")
    print()


async def list_openai(client: CognitiveServicesManagementClient, resource_group: str):
    accounts = client.accounts.list_by_resource_group(resource_group_name=resource_group, api_version="2023-05-01")

    column_width = 40
    print(f"OpenAI Endpoints in {resource_group}".ljust(column_width) + "Model Name")
    print("-" * (column_width * 2))
    for account in list(accounts):
        if account.kind == "OpenAI":
            deployments = client.deployments.list(resource_group_name=resource_group,
                                                  account_name=account.name, api_version="2023-05-01")
            deployments = list(deployments)
            model_id = deployments[0].properties.model.name
            print(f"{account.name:<{column_width}}{model_id}")
    print()


async def get_api_key(resource, resource_group: str,
                      client: CognitiveServicesManagementClient) -> str:
    keys = client.accounts.list_keys(resource_group, resource.name)
    return keys.key1


async def get_azure_config(model_name: str | None) -> OpenAI | AzureOpenAI:
    resource_client = ResourceManagementClient(credential=credential, subscription_id=subscription_id)
    cognitive_client = CognitiveServicesManagementClient(credential=credential, subscription_id=subscription_id)
    model_id: str
    endpoint: str
    api_key: str

    if "GPTSCRIPT_AZURE_RESOURCE_GROUP" in os.environ:
        resource_group = os.environ["GPTSCRIPT_AZURE_RESOURCE_GROUP"]
    else:
        await list_resource_groups(resource_client)
        print("Set GPTSCRIPT_AZURE_RESOURCE_GROUP environment variable")
        sys.exit(0)

    accounts = cognitive_client.accounts.list_by_resource_group(resource_group_name=resource_group,
                                                                api_version="2023-05-01")
    for account in list(accounts):
        selected_resource = account
        endpoint = account.properties.endpoint
        deployments = cognitive_client.deployments.list(resource_group_name=resource_group,
                                                        account_name=account.name, api_version="2023-05-01")
        deployments = list(deployments)
        deployment_name = deployments[0].name
        if deployments[0].properties.model.name == model_name:
            model_id = deployments[0].properties.model.name
            break

    if 'model_id' not in locals():
        print(f"Did not find any matches for model name {model_name}.")
        sys.exit(1)

    api_key = await get_api_key(client=cognitive_client, resource=selected_resource, resource_group=resource_group)
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment_name,
        api_key=api_key,
        api_version="2024-02-01"
    )

    return client


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)
