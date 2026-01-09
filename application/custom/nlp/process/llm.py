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
    
    def offer_from_text(self, content:str) -> dict:
        """Call LLM to extract title, description, company and contract_type from an a text describing an offer

        Args:
            content (str): Text describing the offer

        Returns:
            Offer: Offer object
        """

        json_template = {
            'title': None,
            'description': None,
            'company_name': None,
            'contract_type': 'CDD | CDI | ALTERNANCE | STAGE | INDEPENDENT | INTERIM | None',
        }
        query_prompt = f"DESCRIPTION WEB:\n\n{content}\n\nRépond au format JSON\n\n{json.dumps(json_template)}"

        chat_response = self.client.chat.complete(
            model = self.model_small,
            response_format = {'type': 'json_object'},
            messages = [
                {
                    "role": "system",
                    "content": "Tu reçois le contenu d'une page web décrivant une offre d'emploi (DESCRIPTION WEB). Tu dois extraire les informations présentes dans ce texte"
                },
                {
                    "role": "user",
                    "content": query_prompt,
                },
            ]
        )

        response = chat_response.choices[0].message.content
        result = json.loads(response)

        offer_dict = {}
        for key in json_template.keys():
            offer_dict[key] = result.get(key)

        return offer_dict