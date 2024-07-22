# Simplified configuration of Azure OpenAI provider for GPTScript

1. You need the env variable `GPTSCRIPT_AZURE_API_KEY` to be configured
2. You need the env variable `GPTSCRIPT_AZURE_ENDPOINT` to be configured
3. You might set env variable `GPTSCRIPT_AZURE_DEPLOYMENT_NAME` as default model name
4. You might set env variable `GPTSCRIPT_AZURE_API_VERSION` as API version, default is `2024-02-01` used

```shell
export GPTSCRIPT_AZURE_API_KEY=<your-api-key>
export GPTSCRIPT_AZURE_ENDPOINT=<your-endpoint>

export GPTSCRIPT_AZURE_DEPLOYMENT_NAME=<your-deployment-name>
# or
export GPTSCRIPT_AZURE_MODEL_NAME=<your-deployment-name>

export GPTSCRIPT_AZURE_API_VERSION=<your-api-version>
```

## Usage Example

```shell
gptscript --default-model='gpt-4 from github.com/gptscript-ai/azure-openai-provider' examples/bob.gpt
```

## Development

Run using the following commands

```shell
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
./run.sh
```

```shell
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export GPTSCRIPT_DEBUG=true
gptscript --default-model=gpt-4 examples/bob.gpt
```
