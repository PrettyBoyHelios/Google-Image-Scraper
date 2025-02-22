import os
import sys
from typing import Optional

import patch
import re
from os.path import join
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
from bs4 import BeautifulSoup

from services.gspread_service import GoogleSheetsService
from services.openai_service import OpenAIService
from yaab.inventory_models.models import YaabProduct, output_to_csv
import json


class GoogleAISiteScrapper:
    def __init__(
        self,
        webdriver_path,
        description_path,
        sku,
        product,
        search_key="",
        number_of_results=1,
        headless=True,
        use_brave=False,
    ):
        # check parameter types
        output_path = os.path.join(
            description_path, sku
        )  # todo check if this value is the sku
        if type(number_of_results) != int:
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(output_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(output_path)

        # check if chromedriver is installed
        if not os.path.isfile(webdriver_path):
            is_patched = patch.download_latest_chromedriver()
            if not is_patched:
                exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads"
                )

        for i in range(1):
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            if use_brave:
                if sys.platform not in ["darwin", "win32"]:
                    raise ValueError(
                        "this script is unsupported for {}".format(sys.platform)
                    )

                brave_platform_default_locations = {
                    "win32": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                    "darwin": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                    "win64": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                }

                options.binary_location = brave_platform_default_locations[sys.platform]

            service = webdriver.ChromeService(executable_path=webdriver_path)

            self.driver = webdriver.Chrome(service=service, options=options)

            # driver = webdriver.Chrome(options=options, executable_path=webdriver_path)
            self.driver.set_window_size(1400, 1050)
            self.driver.get("https://www.google.com")
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "APjFqb"))
                ).click()
            except Exception as e:
                logging.warning(e)
                logging.warning("timeout detected, ids and xpaths may have changed")
                continue
            except Exception as e:
                # update chromedriver
                print(e)
                pattern = "(\d+\.\d+\.\d+\.\d+)"
                version = list(set(re.findall(pattern, str(e))))[0]
                is_patched = patch.download_latest_chromedriver(version)
                if not is_patched:
                    exit(
                        "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads"
                    )
                raise e

        self.search_key = search_key
        self.number_of_results = number_of_results
        self.webdriver_path = webdriver_path
        self.description_path = output_path
        self.url = "https://www.google.com/search?q={}".format(search_key)
        self.headless = headless
        self.product: YaabProduct = product

    def find_product_description(
        self,
        openai_service: OpenAIService,
        google_sheets_service: Optional[GoogleSheetsService] = None,
    ):
        """
        This function search and return a list of image urls based on the search key.
        Example:
            google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
            image_urls = google_image_scraper.find_image_urls()

        """
        self.driver.get(self.url)
        count = 0
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        while self.number_of_results > count:
            results = self.driver.find_elements(
                by=By.XPATH, value="//h3[contains(@class,'LC20lb MBeuO DKV0Md')]"
            )
            _ = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//h3[contains(@class,'LC20lb MBeuO DKV0Md')]")
                )
            )
            for result in results:
                result.click()

                logging.info(
                    "waiting for {} to load...".format(self.driver.current_url)
                )
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState")
                    == "complete"
                )
                logging.info("loaded site {}".format(self.driver.current_url))

                url = self.driver.page_source
                website_data = BeautifulSoup(url, "html.parser")
                for tag in website_data(
                    ["script", "style", "button", "nav", "footer", "header", "aside"]
                ):
                    tag.decompose()  # Remove the tag from the parsed HTML
                str_repr = website_data.get_text()

                # Replace multiple line breaks with a single one
                str_repr = re.sub(r"\n+", "\n", str_repr)

                description = openai_service.get_product_description(
                    self.search_key, str_repr
                )
                print(description)
                self.driver.quit()
                if google_sheets_service:
                    google_sheets_service.update_description(
                        self.search_key,
                        description.description,
                        "Nombre del artículo",
                        "AI Description",
                    )
                description.url = self.url
                output_path = join(self.description_path, "description.json")
                with open(
                    join(self.description_path, "description.json"),
                    "w",
                    encoding="utf8",
                ) as f:
                    json_str = description.model_dump_json(indent=4)
                    f.write(json_str)
                print(f"description written to {output_path}")
                self.product.dimensions = description.dimensions
                self.product.ai_description = description.description
                output_to_csv([self.product])
                return description
