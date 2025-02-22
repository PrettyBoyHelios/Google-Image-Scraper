# -*- coding: utf-8 -*-
"""
Created on Nov 11th 2024

@author: PrettyBoyHelios
"""
import base64

# import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)

import os
import requests
import io
from PIL import Image
import re
from typing import Tuple, Optional
from urllib.parse import urlparse


import patch
import logging

from services.gdrive_service import GoogleDriveService
from services.gspread_service import GoogleSheetsService


class GoogleImageScraper:
    def __init__(
        self,
        webdriver_path: str,
        image_path: str,
        sku: str,
        search_key: str,
        number_of_images: int = 1,
        headless: bool = True,
        min_resolution: Tuple[int, int] = (0, 0),
        max_resolution: Tuple[int, int] = (1920, 1080),
        max_missed: int = 10,
        use_brave: bool = False,
    ):
        # check parameter types
        image_path = os.path.join(image_path, sku)
        if type(number_of_images) != int:
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        # check if chromedriver is installed
        if not os.path.isfile(webdriver_path):
            is_patched = patch.download_latest_chromedriver()
            if not is_patched:
                exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads"
                )

        for i in range(1):
            try:
                # try going to www.google.com
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                if use_brave:
                    options.binary_location = (
                        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
                    )
                # options.binary_location = chrome_bin # todo need to fix for chrome bin

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

        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.sku = sku
        self.url = (
            "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"
            % search_key
        )
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.max_missed = max_missed
        self.use_brave = use_brave

    def update_product_images(
        self,
        folder_name: Optional[str] = None,
        google_sheets_service: Optional[GoogleSheetsService] = None,
        google_drive_service: Optional[GoogleDriveService] = None,
    ):
        if folder_name is None:
            raise ValueError("Upload folder not specifiedd")
        if google_sheets_service is None:
            google_sheets_service = GoogleSheetsService()
        if google_drive_service is None:
            google_drive_service = GoogleDriveService()

        folder_id = google_drive_service.get_folder_id(folder_name)

        for image in os.listdir(self.image_path):
            full_path = os.path.join(self.image_path, image)
            file_id = google_drive_service.upload_image_to_drive(full_path, folder_id)
            url = google_drive_service.set_file_public(file_id)
            google_sheets_service.update_product_image(
                self.search_key, url, "Nombre del artículo", "AI Image", "Processed"
            )
            break  # only uploads first image

    def find_image_urls(self):
        """
        This function search and return a list of image urls based on the search key.
        Example:
            google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
            image_urls = google_image_scraper.find_image_urls()

        """
        logging.info("[INFO] Gathering image links")
        self.driver.get(self.url)
        image_urls = []
        count = 0
        missed_count = 0

        _ = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'F0uyec')]"))
        )
        while self.number_of_images > count and missed_count < self.max_missed:
            img_results = self.driver.find_elements(
                by=By.XPATH, value="//div[contains(@class,'F0uyec')]"
            )

            total_images = len(img_results)

            count = 0

            for img_result in img_results:
                try:
                    img_result.click()

                    _ = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//img[contains(@class,'iPVvYb')]")
                        )
                    )

                    actual_imgs = self.driver.find_elements(
                        by=By.XPATH, value="//img[contains(@class,'iPVvYb')]"
                    )

                    src = ""

                    for actual_img in actual_imgs:
                        if "https://encrypted" in actual_img.get_attribute("src"):
                            pass
                        elif "http" in actual_img.get_attribute("src"):
                            src += actual_img.get_attribute("src")
                            break
                        else:
                            pass

                    for actual_img in actual_imgs:
                        if src == "" and "base" in actual_img.get_attribute("src"):
                            src += actual_img.get_attribute("src")

                    if "https://" in src:
                        image_name = self.sku.replace("/", " ")
                        image_name = re.sub(pattern=" ", repl="_", string=image_name)
                        file_path = f"{self.image_path}/{image_name}_{count}.jpeg"  # todo figure out image naming conventions for yaab
                        try:
                            result = requests.get(src, allow_redirects=True, timeout=10)
                            open(file_path, "wb").write(result.content)
                            img = Image.open(file_path)
                            img = img.convert("RGB")
                            img.save(file_path, "JPEG")
                            print(f"Image saved from https to path {file_path}")
                            image_urls.append(src)
                        except Exception as e:
                            print("Bad image.")
                            try:
                                os.unlink(file_path)
                            except Exception as e:
                                pass
                            count -= 1
                    else:
                        img_data = src.split(",")
                        image_name = self.sku.replace("/", " ")
                        image_name = re.sub(pattern=" ", repl="_", string=image_name)
                        file_path = f"{self.image_path}/{image_name}_{count}.jpeg"  # todo figure out image naming conventions for yaab
                        try:
                            img = Image.open(io.BytesIO(base64.b64decode(img_data[1])))
                            img = img.convert("RGB")
                            img.save(file_path, "JPEG")
                            print(f"Image saved from Base64 to path {file_path}")
                            image_urls.append(src)
                        except Exception as e:
                            print("Bad image.")
                            count -= 1
                except ElementClickInterceptedException as e:
                    count -= 1
                    print(e)
                    print("Image is not clickable.")
                    self.driver.quit()
                except Exception as e:
                    print(e)
                    self.driver.quit()

                count += 1
                if count >= total_images:
                    print("No more images to download.")
                    break
                if count == self.number_of_images:
                    break

        self.driver.quit()
        print("[INFO] Google search ended")
        return image_urls

    def save_images(self, image_urls, keep_filenames):
        print(keep_filenames)
        # save images into file directory
        """
            This function takes in an array of image urls and save it into the given image path/directory.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls=["https://example_1.jpg","https://example_2.jpg"]
                google_image_scraper.save_images(image_urls)

        """
        print("[INFO] Saving image, please wait...")
        for i, image_url in enumerate(image_urls):
            try:
                print("[INFO] Image url:%s" % (image_url))
                search_string = "".join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            if keep_filenames:
                                # extract filename without extension from URL
                                o = urlparse(image_url)
                                image_url = o.scheme + "://" + o.netloc + o.path
                                name = os.path.splitext(os.path.basename(image_url))[0]
                                # join filename and extension
                                filename = "%s.%s" % (
                                    name,
                                    image_from_web.format.lower(),
                                )
                            else:
                                filename = "%s%s.%s" % (
                                    search_string,
                                    str(i),
                                    image_from_web.format.lower(),
                                )

                            image_path = os.path.join(self.image_path, filename)
                            print(
                                f"[INFO] {self.search_key} \t {i} \t Image saved at: {image_path}"
                            )
                            image_from_web.save(image_path)
                        except OSError:
                            rgb_im = image_from_web.convert("RGB")
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution is not None:
                            if (
                                image_resolution[0] < self.min_resolution[0]
                                or image_resolution[1] < self.min_resolution[1]
                                or image_resolution[0] > self.max_resolution[0]
                                or image_resolution[1] > self.max_resolution[1]
                            ):
                                image_from_web.close()
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Download failed: ", e)
                pass
        print("--------------------------------------------------")
        print(
            "[INFO] Downloads completed. Please note that some photos were not downloaded as they were not in the correct format (e.g. jpg, jpeg, png)"
        )
