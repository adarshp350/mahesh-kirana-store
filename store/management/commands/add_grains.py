
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add loose grain products"

    def handle(self, *args, **kwargs):

        category, created = Category.objects.get_or_create(
            name="Grains – ಧಾನ್ಯಗಳು"
        )

        grains = [
            ("Rice – ಅಕ್ಕಿ", 60),
            ("Sona Masoori Rice – ಸೋನಾ ಮಸೂರಿ ಅಕ್ಕಿ", 55),
            ("Brown Rice – ಕಂದು ಅಕ್ಕಿ", 70),
            ("Wheat – ಗೋಧಿ", 40),
            ("Jowar – ಜೋಳ", 45),
            ("Bajra – ಸಜ್ಜೆ", 40),
            ("Ragi – ರಾಗಿ", 50),
            ("Maize – ಮೆಕ್ಕೆಜೋಳ", 35),
            ("Foxtail Millet – ನವಣೆ", 100),
            ("Little Millet – ಸಾಮೆ", 100),
        ]

        for name, price in grains:
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "description": name,
                    "product_type": "loose",
                    "unit": "kg",
                    "pack_size": 1,
                    "price": price,
                    "stock": 50,
                    "is_available": True,
                    "image": f"products/grains/{name.split(' – ')[0].lower().replace(' ', '_')}.jpg",
                }
            )

        self.stdout.write(
            self.style.SUCCESS("10 grain products added successfully!")
        )
