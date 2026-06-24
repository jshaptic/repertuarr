import yaml
from openai import OpenAI

with open("config.yaml") as f:
    config = yaml.safe_load(f)

llms = config.get('llms', [])
print(llms)
