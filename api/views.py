from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Count
from products.models import Product, Category
from orders.models import Order, OrderItem
from .serializers import (
    ProductSerializer, CategorySerializer,
    OrderSerializer, UserSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        if category:
            qs = qs.filter(category__slug=category)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def product_recommendations(request, product_id):
    """Products in same category + frequently bought together."""
    try:
        product = Product.objects.get(id=product_id, available=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    # Same category
    same_category = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]

    # Frequently bought together: find products ordered with this product
    order_ids = OrderItem.objects.filter(product=product).values_list('order_id', flat=True)
    bought_together = Product.objects.filter(
        orderitem__order_id__in=order_ids, available=True
    ).exclude(id=product.id).annotate(
        times_bought=Count('id')
    ).order_by('-times_bought')[:4]

    return Response({
        'same_category': ProductSerializer(same_category, many=True).data,
        'bought_together': ProductSerializer(bought_together, many=True).data,
    })
