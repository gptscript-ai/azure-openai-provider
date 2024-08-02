# Azure OpenAI Provider

## Pre-requisites

- Azure CLI installed to use this provider.
- An Azure OpenAI model deployment.

You will need to provide the following information when first setting up the provider:

- Azure Subscription ID
- Azure Resource Group
- Azure OpenAI model name

## Usage Example

To override the default model for a run, you can use this command:

```
gptscript --default-model='gpt-4o from github.com/gptscript-ai/azure-openai-provider' examples/helloworld.gpt
```

See the official [GPTScript documentation](https://docs.gptscript.ai/alternative-model-providers#usage) for more information on how to setup and use alternative model providers within GPTScript.

## Troubleshooting

### I'm getting 429 errors due to rate limiting

 You need to increase the rate limit of your Azure OpenAI deployment [quota](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/quota?tabs=rest).

## Advanced Usage

If you want to bypass the need for the Azure CLI or authentication to Azure in general, you can set `GPTSCRIPT_AZURE_ENDPOINT`, `GPTSCRIPT_AZURE_API_KEY`, `GPTSCRIPT_AZURE_DEPLOYMENT_NAME` as environment variables before using the provider for the first time. Note that these values will still be saved as a GPTScript credential, so changing the environment variables later will not effect GPTScript until you delete that saved credential.

## Development

Run using the following commands

```
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
./run.sh
```

```
# Optionally for more debug output from gptscript
export GPTSCRIPT_DEBUG=true

gptscript --default-model="gpt-4o from http://127.0.0.1:8000/v1" examples/bob.gpt
```
