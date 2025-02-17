from os.path import exists, join

from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, List, Dict, Type
import csv
import re

from yaab.gpt_models.models import Dimensions


class YaabProduct(BaseModel):
    sku: str
    name: str
    category: str
    min_price: Decimal
    price: Decimal
    stock: int
    status: str
    description: str
    colors: List[str]
    ai_description: Optional[str] = None
    dimensions: Optional[Dimensions] = None

    @staticmethod
    def get_product_from_row(row: Dict) -> "YaabProduct":
        """
        Esto convierte la tabla de inventario a un formato que puede ser entendido por el programa
        :param row: excel/googlesheet row data, represented as a dict
        :return:
        """
        min_price = Decimal(re.sub(r"[^\d.,]", "", row["Precio Minimo"]))
        price = Decimal(re.sub(r"[^\d.,]", "", row["Precio"]))
        stock_amount = int(re.sub(r"[^\d]", "", row["Stock"]))
        colors = row["Colores"].replace(", ", ",").split(",")

        return YaabProduct(
            sku=row["SKU"],
            name=row["Nombre del artículo"],
            category=row["Tipo"],
            min_price=min_price,
            price=price,
            stock=stock_amount,
            status=row["Estado"],
            description=row["Descripcion"],
            colors=colors,
        )


headers = [
    [
        "SKU",
        "Name",
        "Category",
        "MinPrice",
        "Price",
        "Stock",
        "Status",
        "Description",
        "Colors",
        "AIDescription",
        "Width",
        "Length",
        "Depth",
        "Unit",
        "Weight",
        "WeightUnit"
    ]
]


def output_to_csv(products: List[YaabProduct]):
    try:
        output_path = join("output", "yaab.csv")
        if not exists(output_path):
            with open(output_path, "w", newline="\n") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(headers)
        with open(output_path, "a", newline="\n") as csvfile:
            writer = csv.writer(csvfile)
            for product in products:
                product_data = [
                    [
                        str(product.sku),
                        str(product.name),
                        str(product.category),
                        str(product.min_price),
                        str(product.price),
                        str(product.stock),
                        str(product.status),
                        str(product.description),
                        str(product.colors),
                        str(product.ai_description),
                        str(
                            getattr(product.dimensions, "width", "")
                            if product.dimensions
                            else ""
                        ),
                        str(
                            getattr(product.dimensions, "length", "")
                            if product.dimensions
                            else ""
                        ),
                        str(
                            getattr(product.dimensions, "depth", "")
                            if product.dimensions
                            else ""
                        ),
                        str(
                            getattr(product.dimensions, "units", "")
                            if product.dimensions
                            else ""
                        ),
                        str(
                            getattr(product.dimensions, "weight", "")
                            if product.dimensions
                            else ""
                        ),
                        str(
                            getattr(product.dimensions, "weight_units", "")
                            if product.dimensions
                            else ""
                        ),
                    ]
                ]
                writer.writerows(product_data)
    except Exception as e:
        print(e)
        raise e
