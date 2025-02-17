# Google Image Scraper
A library created to scrape Google Images.<br>
If you are looking for other image scrapers, JJLimmm has created image scrapers for Gettyimages, Shutterstock, and Bing. <br>
Visit their repo here: https://github.com/JJLimmm/Website-Image-Scraper

## Pre-requisites
1. Google Chrome or Brave Browser Installed in default paths
2. [uv](https://docs.astral.sh/uv/)

## Setup
1. Open command prompt
2. Clone this repository (or [download](https://github.com/ohyicong/Google-Image-Scraper/archive/refs/heads/master.zip))
    ```
    git clone https://github.com/ohyicong/Google-Image-Scraper
    ```
3. Install Dependencies
    ```
    uv sync
    ```
4. Edit your desired parameters in main.py
    ```
    search_keys         = Strings that will be searched for
    number of images    = Desired number of images
    headless            = Chrome GUI behaviour. If True, there will be no GUI
    min_resolution      = Minimum desired image resolution
    max_resolution      = Maximum desired image resolution
    max_missed          = Maximum number of failed image grabs before program terminates. Increase this number to ensure large queries do not exit.
    number_of_workers   = Number of sectioned jobs created. Restricted to one worker per search term and thread.
    ```
5. Run the program
    ```
    uv run python main.py
    ```

## Usage:
This project was created to bypass Google Chrome's new restrictions on web scraping from Google Images. 
To use it, define your desired parameters in main.py and run through the command line:
```
uv run python main.py
```
## Yaab Instructions
1. Descargar
2. Para buscar descripciones e información de precio
```
uv run python main.py
```
3. Para descargar 5 imágenes por producto
```
uv run python images.py -q 5
```

# Consideraciones
El archivo que contiene la información de entrada de los productos tiene que tener las siguientes columnas.
- SKU: ID o SKU del producto, tiene que coincidir con las especificaciones de Lions Intel para la cargar masiva de imágenes.
- Nombre de Producto

# Precaución!
Hay un par de cosas que podrían faltar para hacer que el script funcionara 1:1 con la carga masiva de productos con csv. Sólo sería cuestion de verificar que estamos mandando toda la información requerida y en el orden esperado.
Además sería cuestión de 

Configurar gspread credentials!
