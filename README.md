1. You must be authenticated with the azure CLI
2. You need the env variable `AZURE_SUBSCRIPTION_ID` to be configured
3. You need the env variable `GPTSCRIPT_AZURE_RESOURCE_GROUP` to be configured

```
az login
export AZURE_SUBSCRIPTION_ID=<your-subscription-key>
export GPTSCRIPT_AZURE_RESOURCE_GROUP=<your-resource-group>
```

## Usage Example

```
gptscript --default-model='gpt-4 from github.com/gptscript-ai/azure-openai-provider' examples/helloworld.gpt
```

## Development

Run using the following commands

```
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
./run.sh
```

```
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export GPTSCRIPT_DEBUG=true
gptscript --default-model=gpt-4 examples/bob.gpt
```
