from .cart import Cart
from products.models import Category


def cart_total_items(request):
    cart = Cart(request)
    return {
        'cart_items_count': len(cart),
        'nav_categories': Category.objects.all(),
    }
