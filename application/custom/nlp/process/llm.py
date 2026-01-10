from mistralai import Mistral
import json
import os
from datetime import date

from ...db.offer.models import Offer



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
    
    def email_from_offer(self, email_template:str, offer:Offer) -> str:
        system_prompt = """
        Tu écris un email pour une candidature spontanée basée UNIQUEMENT sur des faits fournis et en t'appuiyant sur le model fournis.
        INTERDICTION d'inventer des expériences, entreprises, technologies, chiffres ou diplômes.

        Tu as accès uniquement à:
        - model d'email
        - infos de l'annonce structurée

        Si une info est manquante:
        - ne l'invente pas
        - n'en parle pas

        Sortie STRICT (Corps du email uniquement)

        Contraintes:
        - Style: professionnel, naturel, sans exagération.
        """

        payload = {
            'template': email_template,
            'offer_title': offer.title,
            'offer_description': offer.description.offer_description,
            'offer_skills': offer.skills,
            'offer_contract': offer.contract_type,
            'company_name': offer.company.name,
            'today_date': date.today().isoformat()
        }

        chat_response = self.client.chat.complete(
            model = self.model_small,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": json.dumps(payload)
                }
            ]
        )

        return chat_response.choices[0].message.content
    
    def coverletter_from_offer(self, coverletter_template:str, resume:str, offer:Offer) -> str:
        system_prompt = """
        Tu écris une lettre de motivation basée UNIQUEMENT sur des faits fournis et en t'appuiyant sur le model fournis.
        INTERDICTION d'inventer des expériences, entreprises, technologies, chiffres ou diplômes.

        Tu as accès uniquement à:
        - model de lettre de motivation
        - contenu du cv
        - infos de l'annonce structurée

        Si une info est manquante:
        - ne l'invente pas
        - n'en parle pas

        Sortie STRICT (Markdown uniquement)

        Contraintes:
        - Style: professionnel, naturel, sans exagération.
        """

        payload = {
            'template': coverletter_template,
            'resume': resume,
            'offer_title': offer.title,
            'offer_description': offer.description.offer_description,
            'offer_skills': offer.skills,
            'offer_contract': offer.contract_type,
            'company_name': offer.company.name,
            'today_date': date.today().isoformat()
        }

        chat_response = self.client.chat.complete(
            model = self.model_small,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": json.dumps(payload)
                }
            ]
        )

        return chat_response.choices[0].message.content