from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def home(request):
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    categories = Category.objects.all()
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    query = request.GET.get('q')
    sort = request.GET.get('sort', 'newest')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'query': query or '',
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })
