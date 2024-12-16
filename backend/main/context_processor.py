from .models import Products


from collections import defaultdict

def main_context_processor(request):
    products = Products.objects.filter(is_active=True)

    # Group products by type
    grouped_products = defaultdict(list)
    for product in products:
        grouped_products[product.get_type_display()].append(product)


    return {
        'products_by_type': dict(grouped_products),
        'products_type': dict(Products.TypeChoices.choices)
    }
