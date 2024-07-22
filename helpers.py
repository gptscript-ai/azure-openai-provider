import json
import os
import sys
from dataclasses import dataclass

from openai import AzureOpenAI

DEFAULT_API_VERSION = '2024-02-01'
DEFAULT_MODEL_NAME = 'gpt-4'

endpoint: str
api_key: str
deployment_name: str
api_version: str

@dataclass
class AzureConfig:
    endpoint: str
    deployment_name: str
    api_key: str
    api_version: str

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True)


async def get_azure_config(
        model_name: str | None = None,
        azure_api_key: str | None = None,
        azure_endpoint: str | None = None,
        azure_api_version: str | None = None
        ) -> AzureConfig | None:
    global endpoint
    global api_key
    global deployment_name
    global api_version

    if azure_api_key is not None :
        api_key = azure_api_key
    elif 'GPTSCRIPT_AZURE_API_KEY' in os.environ:
        api_key = os.environ['GPTSCRIPT_AZURE_API_KEY']

    if azure_endpoint is not None:
        endpoint = azure_endpoint
    elif 'GPTSCRIPT_AZURE_ENDPOINT' in os.environ:
        endpoint = os.environ['GPTSCRIPT_AZURE_ENDPOINT']

    if model_name is not None and model_name.strip() != '.':
        deployment_name = model_name
    elif 'GPTSCRIPT_AZURE_DEPLOYMENT_NAME' in os.environ:
        deployment_name = os.environ['GPTSCRIPT_AZURE_DEPLOYMENT_NAME']
    elif 'GPTSCRIPT_AZURE_MODEL_NAME' in os.environ:
        deployment_name = os.environ['GPTSCRIPT_AZURE_MODEL_NAME']
    else:
        deployment_name = DEFAULT_MODEL_NAME

    if azure_api_version is not None:
        api_version = azure_api_version
    elif 'GPTSCRIPT_AZURE_API_VERSION' in os.environ:
        api_version = os.environ['GPTSCRIPT_AZURE_API_VERSION']
    else:
        api_version = DEFAULT_API_VERSION

    if 'endpoint' in globals() and 'api_key' in globals() and 'deployment_name' in globals() and 'api_version' in globals():
        return AzureConfig(
            endpoint=endpoint,
            api_key=api_key,
            deployment_name=deployment_name,
            api_version=api_version
        )

    return None


def client(endpoint: str, deployment_name: str, api_key: str, api_version: str) -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment_name,
        api_key=api_key,
        api_version=api_version
    )


if __name__ == "__main__":
    import asyncio

    config = asyncio.run(get_azure_config())

    if config is None:
        from gptscript.gptscript import GPTScript
        from gptscript.opts import Options

        gptscript = GPTScript()

        async def prompt(tool_input) -> dict:
            run = gptscript.run(
                tool_path="sys.prompt",
                opts=Options(
                    input=json.dumps(tool_input),
                )
            )
            output = await run.text()
            return json.loads(output)

        # get Azure API key
        tool_input = {
            "message": "Please provide your Azure API key:",
            "fields": "id",
            "sensitive": "false",
        }
        result = asyncio.run(prompt(tool_input))
        azure_api_key = result["id"]

        # get Azure endpoint
        tool_input = {
            "message": "Please provide your Azure endpoint:",
            "fields": "name",
            "sensitive": "false",
        }
        result = asyncio.run(prompt(tool_input))
        azure_endpoint = result["name"]

        # get model name
        tool_input = {
            "message": "Please provide your Azure model or deployment name:",
            "fields": "name",
            "sensitive": "false",
        }
        result = asyncio.run(prompt(tool_input))
        model_name = result["name"]

        config = asyncio.run(get_azure_config(
            model_name=model_name,
            azure_api_key=azure_api_key,
            azure_endpoint=azure_endpoint))

        gptscript.close()


    if config is None:
        print("Azure config not found. Please ensure you have configured the environment variables correctly.")
        sys.exit(1)

    env = {
        "env": {
            "GPTSCRIPT_AZURE_API_KEY": config.api_key,
            "GPTSCRIPT_AZURE_ENDPOINT": config.endpoint,
            "GPTSCRIPT_AZURE_DEPLOYMENT_NAME": config.deployment_name,
            "GPTSCRIPT_AZURE_API_VERSION": config.api_version
        }
    }
    print(json.dumps(env))
