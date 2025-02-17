from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from enum import Enum

class DimensionalUnit(Enum):
    # International Metric System (SI)
    MILLIMETER = "mm"       # 1 mm = 0.001 meters
    CENTIMETER = "cm"       # 1 cm = 0.01 meters
    METER = "m"             # Base unit: 1 meter

    # U.S. Customary Units
    INCH = "in"             # 1 inch = 2.54 centimeters
    FOOT = "ft"             # 1 foot = 12 inches (or 0.3048 meters)
    YARD = "yd"             # 1 yard = 3 feet (or 0.9144 meters)

class WeightUnit(Enum):
    MILLIGRAM = "mg"
    GRAM = "g"
    KILOGRAM = "kg"
    OUNCE = "oz"
    POUND = "lb"


class Dimensions(BaseModel):
    width: Optional[int]
    length: Optional[int]
    height: Optional[int]
    dim_units: Optional[DimensionalUnit]
    weight: Optional[Decimal]
    weight_units: Optional[WeightUnit]


class GPTDescriptionResponse(BaseModel):
    description: str
    dimensions: Dimensions
    url: Optional[str]
