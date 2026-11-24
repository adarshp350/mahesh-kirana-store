
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add spices with 4 different pack sizes"

    def handle(self, *args, **kwargs):

        category, created = Category.objects.get_or_create(
            name="Spices – ಮಸಾಲೆ ಪದಾರ್ಥಗಳು"
        )

        spices = [
            "Turmeric Powder – ಅರಿಶಿನ ಪುಡಿ",
            "Chilli Powder – ಮೆಣಸಿನ ಪುಡಿ",
            "Coriander Powder – ಧನಿಯಾ ಪುಡಿ",
            "Cumin Seeds – ಜೀರಿಗೆ",
            "Mustard Seeds – ಸಾಸಿವೆ",
            "Black Pepper – ಕರಿಮೆಣಸು",
            "Cardamom – ಏಲಕ್ಕಿ",
            "Cloves – ಲವಂಗ",
            "Cinnamon – ದಾಲ್ಚಿನ್ನಿ",
            "Fenugreek Seeds – ಮೆಂತ್ಯ",
            "Fennel Seeds – ಸೋಂಪು",
            "Dry Ginger Powder – ಒಣ ಶುಂಠಿ ಪುಡಿ",
            "Garam Masala – ಗರಂ ಮಸಾಲಾ",
            "Biryani Masala – ಬಿರಿಯಾನಿ ಮಸಾಲಾ",
            "Sambar Powder – ಸಾಂಬಾರ್ ಪುಡಿ",
        ]

        sizes = [50, 100, 250, 500]

        count = 0

        for spice in spices:
            for size in sizes:

                product_name = f"{spice} ({size} gm)"

                Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        "category": category,
                        "description": spice,
                        "product_type": "packed",
                        "unit": "g",
                        "pack_size": size,
                        "price": 0,
                        "stock": 50,
                        "is_available": True,
                    }
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} spice-size products processed successfully!"
            )
        )
