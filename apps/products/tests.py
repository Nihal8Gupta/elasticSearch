from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product
from apps.products.documents import ProductDocument


class ImportProductsCommandTests(TestCase):
    def _csv_file(self, contents):
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        csv_path = Path(temporary_directory.name) / "products.csv"
        csv_path.write_text(contents, encoding="utf-8")
        return csv_path

    def test_imports_products_from_csv(self):
        csv_path = self._csv_file(
            "product_name,price,quantity,category\n"
            "Coffee,12.50,3,Groceries\n"
        )

        call_command("import_products", str(csv_path))

        product = Product.objects.get()
        self.assertEqual(product.product_name, "Coffee")
        self.assertEqual(product.product_price, Decimal("12.50"))
        self.assertEqual(product.product_quentity, 3)
        self.assertEqual(product.product_category, "Groceries")

    def test_rejects_missing_required_column(self):
        csv_path = self._csv_file(
            "product_name,price,quantity\nCoffee,12.50,3\n"
        )

        with self.assertRaisesMessage(CommandError, "category"):
            call_command("import_products", str(csv_path))

        self.assertFalse(Product.objects.exists())

    def test_invalid_row_does_not_partially_import(self):
        csv_path = self._csv_file(
            "product_name,price,quantity,category\n"
            "Coffee,12.50,3,Groceries\n"
            "Tea,invalid,2,Groceries\n"
        )

        with self.assertRaisesMessage(CommandError, "CSV row 3"):
            call_command("import_products", str(csv_path))

        self.assertFalse(Product.objects.exists())


class ProductDocumentTests(TestCase):
    def test_prepare_serializes_product_fields(self):
        product = Product(
            product_name="Coffee",
            product_price=Decimal("12.50"),
            product_quentity=3,
            product_category="Groceries",
        )

        self.assertEqual(
            ProductDocument().prepare(product),
            {
                "product_name": "Coffee",
                "product_price": 12.5,
                "product_category": "Groceries",
            },
        )


class ProductSearchViewTests(TestCase):
    def test_search_page_loads(self):
        response = self.client.get(reverse("products:search"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find a product")

    @patch("apps.products.views.search_product_suggestions")
    def test_short_query_does_not_call_elasticsearch(self, search_mock):
        response = self.client.get(
            reverse("products:suggestions"),
            {"q": "c"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"results": []})
        search_mock.assert_not_called()

    @patch("apps.products.views.search_product_suggestions")
    def test_suggestions_are_returned_as_json(self, search_mock):
        search_mock.return_value = [
            {
                "id": "7",
                "name": "Coffee Beans",
                "price": 12.5,
                "category": "groceries",
            }
        ]

        response = self.client.get(
            reverse("products:suggestions"),
            {"q": "coffee"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["id"], "7")
        search_mock.assert_called_once_with("coffee")

    def test_product_detail_loads(self):
        product = Product.objects.create(
            product_name="Coffee Beans",
            product_price=Decimal("12.50"),
            product_quentity=4,
            product_category="groceries",
        )

        response = self.client.get(
            reverse("products:detail", args=[product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coffee Beans")
        self.assertContains(response, "12.50")

    def test_missing_product_detail_returns_404(self):
        response = self.client.get(reverse("products:detail", args=[999999]))

        self.assertEqual(response.status_code, 404)
