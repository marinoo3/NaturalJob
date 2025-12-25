from mistralai import Mistral
import json
import os




class LLM:

    model_small = "mistral-small-latest"

    def __init__(self):
        api_key = os.environ["MISTRAL_API_KEY"]
        self.client = Mistral(api_key=api_key)

    def request_json(self, prompt:str, json_template:dict) -> dict:
        query_prompt = prompt + '\nRépond au format JSON.\n\n' + json.dumps(json_template)
        chat_response = self.client.chat.complete(
            model = self.model_small,
            response_format = {'type': 'json_object'},
            messages = [
                {
                    "role": "user",
                    "content": query_prompt,
                },
            ]
        )
        response = chat_response.choices[0].message.content
        return json.loads(response)