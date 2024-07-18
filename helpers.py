import json
import os
from dataclasses import dataclass

from openai import AzureOpenAI

DEFAULT_API_VERSION = '2024-02-01'

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


async def get_azure_config(model_name: str | None = None) -> AzureConfig | None:
    global endpoint
    global api_key
    global deployment_name
    global api_version

    if 'GPTSCRIPT_AZURE_ENDPOINT' in os.environ and 'GPTSCRIPT_AZURE_API_KEY' in os.environ:
        endpoint = os.environ['GPTSCRIPT_AZURE_ENDPOINT']
        api_key = os.environ['GPTSCRIPT_AZURE_API_KEY']
        deployment_name = os.environ.get(['GPTSCRIPT_AZURE_DEPLOYMENT_NAME'], model_name)
        api_version = os.environ.get('GPTSCRIPT_AZURE_API_VERSION', DEFAULT_API_VERSION)

    if 'endpoint' in globals() and 'api_key' in globals() and 'deployment_name' in globals():
        return AzureConfig(
            endpoint=endpoint,
            api_key=api_key,
            deployment_name=deployment_name,
            api_version=api_version
        )

    return AzureConfig(endpoint,
                       deployment_name,
                       api_key,
                       api_version
                       )


def client(endpoint: str, deployment_name: str, api_key: str, api_version: str) -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment_name,
        api_key=api_key,
        api_version=api_version
    )


if __name__ == "__main__":
    env = {
        "env": {
            "GPTSCRIPT_AZURE_API_KEY": os.environ['GPTSCRIPT_AZURE_API_KEY'],
            "GPTSCRIPT_AZURE_ENDPOINT": os.environ['GPTSCRIPT_AZURE_ENDPOINT'],
            "GPTSCRIPT_AZURE_DEPLOYMENT_NAME": os.environ['GPTSCRIPT_AZURE_DEPLOYMENT_NAME'],
            "GPTSCRIPT_AZURE_API_VERSION": os.environ.get('GPTSCRIPT_AZURE_API_VERSION', DEFAULT_API_VERSION)
        }
    }
    print(json.dumps(env))
