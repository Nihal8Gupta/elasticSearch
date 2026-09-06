from django.shortcuts import get_object_or_404

from .documents import ProductDocument
from .models import Product


def search_product_suggestions(query, limit=8):
    search = (
        ProductDocument.search()
        .query(
            "multi_match",
            query=query,
            fields=["product_name^2", "product_category"],
            type="phrase_prefix",
        )
        .source(["product_name", "product_price", "product_category"])
    )

    response = search[:limit].execute()
    return [
        {
            "id": str(hit.meta.id),
            "name": hit.product_name,
            "price": hit.product_price,
            "category": hit.product_category,
        }
        for hit in response
    ]


def get_product(product_id):
    return get_object_or_404(Product, pk=product_id)
