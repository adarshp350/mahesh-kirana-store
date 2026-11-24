
from decimal import Decimal

from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add common kirana store products"

    def handle(self, *args, **kwargs):

        products = [
            # Loose grains
            ("Rice", "Grains", 65, "loose", "kg", 1),
            ("Wheat", "Grains", 40, "loose", "kg", 1),
            ("Rava", "Grains", 45, "loose", "kg", 1),
            ("Poha", "Grains", 50, "loose", "kg", 1),

            # Loose pulses
            ("Toor Dal", "Pulses", 150, "loose", "kg", 1),
            ("Moong Dal", "Pulses", 120, "loose", "kg", 1),
            ("Chana Dal", "Pulses", 85, "loose", "kg", 1),
            ("Urad Dal", "Pulses", 110, "loose", "kg", 1),
            ("Masoor Dal", "Pulses", 100, "loose", "kg", 1),

            # Loose daily essentials
            ("Sugar", "Daily Essentials", 48, "loose", "kg", 1),
            ("Salt", "Daily Essentials", 25, "loose", "kg", 1),
            ("Jaggery", "Daily Essentials", 60, "loose", "kg", 1),
            ("Peanuts", "Daily Essentials", 120, "loose", "kg", 1),

            # Packed groceries
            ("Sunflower Oil", "Oil", 145, "packed", "litre", 1),
            ("Tea Powder", "Beverages", 120, "packed", "g", 250),
            ("Coffee", "Beverages", 90, "packed", "g", 100),
            ("Milk", "Dairy", 30, "packed", "ml", 500),
            ("Curd", "Dairy", 35, "packed", "g", 500),

            # Packed snacks
            ("Parle-G Biscuits", "Snacks", 10, "packed", "packet", 1),
            ("Maggi Noodles", "Snacks", 14, "packed", "packet", 1),

            # Loose vegetables
            ("Potato", "Vegetables", 35, "loose", "kg", 1),
            ("Onion", "Vegetables", 40, "loose", "kg", 1),
            ("Tomato", "Vegetables", 30, "loose", "kg", 1),
            ("Green Chilli", "Vegetables", 60, "loose", "kg", 1),
            ("Carrot", "Vegetables", 50, "loose", "kg", 1),

            # Loose fruits
            ("Banana", "Fruits", 50, "loose", "kg", 1),
            ("Apple", "Fruits", 120, "loose", "kg", 1),
            ("Orange", "Fruits", 80, "loose", "kg", 1),

            # Packed personal care and cleaning
            ("Bath Soap", "Personal Care", 35, "packed", "piece", 1),
            ("Toothpaste", "Personal Care", 55, "packed", "piece", 1),
            ("Detergent Powder", "Cleaning", 90, "packed", "kg", 1),
            ("Red Chilli Powder", "Spices", 45, "packed", "g", 200),
            ("Turmeric Powder", "Spices", 35, "packed", "g", 100),
        ]

        added = 0
        existing = 0

        for name, category_name, price, product_type, unit, pack_size in products:

            category, _ = Category.objects.get_or_create(
                name=category_name
            )

            product, created = Product.objects.get_or_create(
                name=name,
                category=category,
                defaults={
                    "description": name,
                    "price": Decimal(str(price)),
                    "stock": 50,
                    "product_type": product_type,
                    "unit": unit,
                    "pack_size": Decimal(str(pack_size)),
                    "is_available": True,
                }
            )

            if created:
                added += 1
            else:
                existing += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Products added: {added}. "
                f"Existing products preserved: {existing}."
            )
        )
