
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add Daily Essentials products"

    def handle(self, *args, **kwargs):

        category, created = Category.objects.get_or_create(
            name="Daily Essentials – ದಿನಸಿ ಅಗತ್ಯ ವಸ್ತುಗಳು"
        )

        products = [
            {"name": "Sugar – ಸಕ್ಕರೆ", "price": 45},
            {"name": "Upma Rava – ಉಪ್ಪಿಟ್ಟು ರವೆ", "price": 50},
            {"name": "Chiroti Rava – ಚಿರೋಟಿ ರವೆ", "price": 60},
            {"name": "Thin Avalakki – ತೆಳು ಅವಲಕ್ಕಿ", "price": 60},
            {"name": "Medium Avalakki – ಮಧ್ಯಮ ಅವಲಕ್ಕಿ", "price": 55},
            {"name": "Thick Avalakki – ದಪ್ಪ ಅವಲಕ್ಕಿ", "price": 55},
            {"name": "Red Avalakki – ಕೆಂಪು ಅವಲಕ್ಕಿ", "price": 70},
            {"name": "Wheat Flour – ಗೋಧಿ ಹಿಟ್ಟು", "price": 50},
            {"name": "Rice Flour – ಅಕ್ಕಿ ಹಿಟ್ಟು", "price": 55},
            {"name": "Jowar Flour – ಜೋಳದ ಹಿಟ್ಟು", "price": 60},
            {"name": "Ragi Flour – ರಾಗಿ ಹಿಟ್ಟು", "price": 55},
            {"name": "Besan Flour – ಕಡಲೆ ಹಿಟ್ಟು", "price": 90},
            {"name": "Roasted Gram Flour – ಹುರಿಗಡಲೆ ಹಿಟ್ಟು", "price": 100},
            {"name": "Maida – ಮೈದಾ", "price": 45},
            {"name": "Corn Flour – ಕಾರ್ನ್ ಫ್ಲೋರ್", "price": 70},
        ]

        count = 0

        # Add loose products
        for item in products:
            Product.objects.update_or_create(
                name=item["name"],
                defaults={
                    "category": category,
                    "description": item["name"],
                    "product_type": "loose",
                    "unit": "kg",
                    "pack_size": 1,
                    "price": item["price"],
                    "stock": 50,
                    "is_available": True,
                }
            )
            count += 1

        # Add only 1 KG packed Godi Hittu
        Product.objects.update_or_create(
            name="Wheat Flour Packet (1 kg) – ಗೋಧಿ ಹಿಟ್ಟು",
            defaults={
                "category": category,
                "description": "Wheat Flour Packet – ಗೋಧಿ ಹಿಟ್ಟು",
                "product_type": "packed",
                "unit": "kg",
                "pack_size": 1,
                "price": 50,
                "stock": 50,
                "is_available": True,
            }
        )

        count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} Daily Essentials products added successfully!"
            )
        )
