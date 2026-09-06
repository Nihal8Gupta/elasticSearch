from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from .models import Product


@registry.register_document
class ProductDocument(Document):
    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Product
        fields = [
            'product_name',
            'product_price',
            'product_category',
        ]

    def prepare(self, instance):
        """Serialize model fields explicitly for Elasticsearch 9."""
        return {
            'product_name': instance.product_name,
            'product_price': float(instance.product_price),
            'product_category': instance.product_category,
        }
