"""
Services layer — the fan-in point.
All business logic converges here. Routers import from this package.

Usage in routers:
    from src.services import buyer, inventory, purchase, sale, shop, work_order
"""
from src.services import (
    buyer,
    inventory,
    purchase,
    sale,
    shop,
    work_order,
)

__all__ = [
    "buyer",
    "inventory",
    "purchase",
    "sale",
    "shop",
    "work_order",
]

