from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .razorpay_utils import create_razorpay_order, verify_razorpay_signature


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.get_total_price()
            order.payment_method = request.POST.get('payment_method', 'razorpay')
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            # Handle payment based on selected method
            if order.payment_method == 'cod':
                order.status = 'confirmed'
                order.save()
                cart.clear()
                return render(request, 'orders/order_success.html', {'order': order})

            # Razorpay online payment
            razorpay_order = create_razorpay_order(
                amount=float(order.total_amount),
                receipt=f'order_{order.id}',
            )
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            return render(request, 'orders/payment.html', {
                'order': order,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': int(order.total_amount * 100),
                'currency': 'INR',
            })
    else:
        form = OrderCreateForm(initial={
            'full_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
            'email': request.user.email,
            'phone': request.user.phone,
            'address': request.user.address,
            'city': request.user.city,
            'state': request.user.state,
            'pincode': request.user.pincode,
        })

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        order = get_object_or_404(Order, razorpay_order_id=order_id)

        is_valid = verify_razorpay_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })

        if is_valid:
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.is_paid = True
            order.status = 'confirmed'
            order.save()

            # Clear cart
            cart = Cart(request)
            cart.clear()

            return render(request, 'orders/order_success.html', {'order': order})
        else:
            order.status = 'cancelled'
            order.save()
            messages.error(request, 'Payment verification failed.')
            return redirect('order_list')

    return redirect('home')


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
