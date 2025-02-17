import logging

from dotenv import load_dotenv
from openai import OpenAI
from os import getenv

from utils.utils import load_prompt, Prompt
from yaab.gpt_models.models import GPTDescriptionResponse


class OpenAIService:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

    def get_product_description(
        self, product: str, website_content: str
    ) -> GPTDescriptionResponse:
        """
        This gets a product's description by analyzing the webpage, and also attempts to find product dimensions.
        :param product:
        :param website_content:
        :return:
        """
        prompt = load_prompt(Prompt.INFO_DESCRIPCION)
        chat_completion = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": "Producto: {}\n{}".format(product, website_content),
                },
            ],
            model="gpt-4o-mini",
            response_format=GPTDescriptionResponse,
        )
        try:
            return chat_completion.choices[0].message.parsed
        except Exception as e:
            print(chat_completion.choices)
            raise Exception("error on chatgpt parsed output")
