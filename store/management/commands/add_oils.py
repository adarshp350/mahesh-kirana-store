
from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Add oil packet products"

    def handle(self, *args, **kwargs):

        # Use the existing Oil category
        category = Category.objects.filter(
            name__icontains="ಎಣ್ಣೆ"
        ).first()

        if not category:
            category = Category.objects.create(
                name="Oils – ಎಣ್ಣೆ"
            )

        brands = [
            "Ruchi Gold",
            "SOT",
            "Sunrich",
            "Fortune",
            "Gemini",
        ]

        pack_sizes = [
            ("500 ml", "ml", 500),
            ("1 L", "litre", 1),
            ("2 L", "litre", 2),
            ("5 L", "litre", 5),
        ]

        added = 0

        for brand in brands:
            for label, unit, size in pack_sizes:

                product_name = f"{brand} Oil {label}"

                product, created = Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        "category": category,
                        "description": f"{brand} cooking oil - {label}",
                        "product_type": "packed",
                        "unit": unit,
                        "pack_size": size,
                        "price": 0,
                        "stock": 50,
                        "is_available": True,
                    }
                )

                if created:
                    added += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{added} oil products added successfully!"
            )
        )
