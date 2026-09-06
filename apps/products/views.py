from elastic_transport import ConnectionError as ElasticsearchConnectionError
from elasticsearch import ApiError
from django.http import JsonResponse
from django.shortcuts import render

from .selectors import get_product, search_product_suggestions


def product_search(request):
    return render(request, "products/search.html")


def product_suggestions(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    try:
        results = search_product_suggestions(query)
    except (ApiError, ElasticsearchConnectionError):
        return JsonResponse(
            {"results": [], "error": "Search is temporarily unavailable."},
            status=503,
        )

    return JsonResponse({"results": results})


def product_detail(request, product_id):
    return render(
        request,
        "products/detail.html",
        {"product": get_product(product_id)},
    )

# Create your views here.
