
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add pulses products"

    def handle(self, *args, **kwargs):

        category = Category.objects.filter(
            name__icontains="Pulses"
        ).first()

        if not category:
            category = Category.objects.create(
                name="Pulses – ಬೇಳೆಕಾಳುಗಳು"
            )

        pulses = [
            ("Toor Dal – ತೊಗರಿ ಬೇಳೆ", 160),
            ("Chana Dal – ಕಡಲೆ ಬೇಳೆ", 100),
            ("Moong Dal – ಹೆಸರು ಬೇಳೆ", 130),
            ("Urad Dal – ಉದ್ದಿನ ಬೇಳೆ", 140),
            ("Masoor Dal – ಮಸೂರ ಬೇಳೆ", 100),
            ("Green Gram – ಹೆಸರು ಕಾಳು", 120),
            ("Black Chana – ಕಪ್ಪು ಕಡಲೆ", 90),
            ("White Chana – ಬಿಳಿ ಕಡಲೆ", 110),
            ("White Peas – ಬಿಳಿ ಬಟಾಣಿ", 90),
            ("Roasted Gram – ಹುರಿಗಡಲೆ", 100),
            ("Horse Gram – ಹುರುಳಿ ಕಾಳು", 100),
            ("Cowpea – ಅಲಸಂದೆ ಕಾಳು", 120),
            ("Green Peas – ಹಸಿರು ಬಟಾಣಿ", 110),
            ("Matki – ಮಡಿಕೆ ಕಾಳು", 130),
        ]

        added = 0

        for name, price in pulses:

            product, created = Product.objects.get_or_create(
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
                }
            )

            if created:
                added += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{added} pulses products added successfully!"
            )
        )
