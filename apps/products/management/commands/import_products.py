import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import Product


class Command(BaseCommand):
    help = "Import Product objects from a CSV file."

    required_columns = {"product_name", "price", "quantity", "category"}

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            nargs="?",
            default=str(settings.BASE_DIR / "MOCK_DATA.csv"),
            help="CSV path (defaults to MOCK_DATA.csv in the project root).",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"])
        products = self._read_products(csv_path)

        with transaction.atomic():
            Product.objects.bulk_create(products, batch_size=500)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {len(products)} products from {csv_path}."
            )
        )

    def _read_products(self, csv_path):
        try:
            csv_file = csv_path.open("r", encoding="utf-8-sig", newline="")
        except OSError as exc:
            raise CommandError(f"Could not open CSV file '{csv_path}': {exc}") from exc

        products = []
        with csv_file:
            reader = csv.DictReader(csv_file)
            headers = set(reader.fieldnames or [])
            missing_columns = self.required_columns - headers
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise CommandError(f"CSV is missing required columns: {missing}")

            for row_number, row in enumerate(reader, start=2):
                products.append(self._product_from_row(row, row_number))

        return products

    def _product_from_row(self, row, row_number):
        try:
            price = Decimal(row["price"].strip())
            quantity = int(row["quantity"].strip())
        except (AttributeError, InvalidOperation, TypeError, ValueError) as exc:
            raise CommandError(
                f"Invalid numeric value on CSV row {row_number}."
            ) from exc

        product = Product(
            product_name=(row["product_name"] or "").strip(),
            product_price=price,
            product_quentity=quantity,
            product_category=(row["category"] or "").strip(),
        )

        try:
            product.full_clean()
        except ValidationError as exc:
            raise CommandError(
                f"Invalid product on CSV row {row_number}: {exc.message_dict}"
            ) from exc

        return product
