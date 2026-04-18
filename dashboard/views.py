from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product, Category
from accounts.models import User


@staff_member_required
def dashboard_home(request):
    now = timezone.now()
    today = now.date()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # === Basic KPIs ===
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0
    total_users = User.objects.count()
    total_products = Product.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    recent_orders = Order.objects.all()[:10]

    # === Today's Quick Stats ===
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(is_paid=True, created_at__date=today).aggregate(
        total=Sum('total_amount'))['total'] or 0
    new_customers_today = User.objects.filter(date_joined__date=today).count()

    # === 30-day stats & percentage change ===
    monthly_revenue = Order.objects.filter(
        is_paid=True, created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()

    prev_revenue = Order.objects.filter(
        is_paid=True, created_at__gte=sixty_days_ago, created_at__lt=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    prev_orders = Order.objects.filter(
        created_at__gte=sixty_days_ago, created_at__lt=thirty_days_ago
    ).count()
    prev_users = User.objects.filter(
        date_joined__gte=sixty_days_ago, date_joined__lt=thirty_days_ago
    ).count()
    cur_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()

    def pct_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    revenue_change = pct_change(monthly_revenue, prev_revenue)
    orders_change = pct_change(monthly_orders, prev_orders)
    users_change = pct_change(cur_users, prev_users)

    # === Monthly Revenue Bar Chart (last 6 months) ===
    six_months_ago = now - timedelta(days=180)
    monthly_data_qs = (
        Order.objects.filter(is_paid=True, created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )
    monthly_chart = []
    max_monthly = 0
    for entry in monthly_data_qs:
        total = float(entry['total'] or 0)
        if total > max_monthly:
            max_monthly = total
        monthly_chart.append({
            'month': entry['month'].strftime('%b'),
            'total': total,
        })
    for item in monthly_chart:
        item['height_pct'] = int((item['total'] / max_monthly) * 100) if max_monthly > 0 else 0
        item['total_display'] = int(item['total'])

    # === Order Status Distribution (donut chart) ===
    status_colors = {
        'pending': '#FFB020',
        'confirmed': '#1B2A4A',
        'shipped': '#4285F4',
        'delivered': '#00C9A7',
        'cancelled': '#EF4444',
    }
    status_qs = Order.objects.values('status').annotate(count=Count('id'))
    status_data = []
    total_for_donut = sum(s['count'] for s in status_qs) or 1
    cumulative = 0
    conic_parts = []
    for entry in status_qs:
        pct = round((entry['count'] / total_for_donut) * 100, 1)
        color = status_colors.get(entry['status'], '#ccc')
        start = cumulative
        cumulative += pct
        conic_parts.append(f'{color} {start}% {cumulative}%')
        status_data.append({
            'status': entry['status'].capitalize(),
            'count': entry['count'],
            'pct': pct,
            'color': color,
        })
    conic_gradient_css = ', '.join(conic_parts) if conic_parts else '#E2E8F0 0% 100%'

    # === Top Selling Products ===
    top_products_qs = (
        OrderItem.objects.values('product__name')
        .annotate(total_qty=Sum('quantity'), total_sales=Sum(F('price') * F('quantity')))
        .order_by('-total_qty')[:5]
    )
    top_products = list(top_products_qs)
    max_qty = top_products[0]['total_qty'] if top_products else 1
    for p in top_products:
        p['bar_pct'] = int((p['total_qty'] / max_qty) * 100)
        p['total_sales'] = int(p['total_sales'] or 0)

    # === Recent Customers ===
    avatar_colors = ['#FF6B35', '#00C9A7', '#4285F4', '#FFB020', '#8E24AA']
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_customers = []
    for i, user in enumerate(recent_users):
        initial = (user.first_name or user.username or '?')[0].upper()
        recent_customers.append({
            'user': user,
            'initial': initial,
            'color': avatar_colors[i % len(avatar_colors)],
        })

    # === Payment Method Breakdown ===
    payment_qs = Order.objects.values('payment_method').annotate(count=Count('id'))
    razorpay_count = 0
    cod_count = 0
    for p in payment_qs:
        if p['payment_method'] == 'razorpay':
            razorpay_count = p['count']
        elif p['payment_method'] == 'cod':
            cod_count = p['count']
    payment_total = razorpay_count + cod_count or 1
    razorpay_pct = round((razorpay_count / payment_total) * 100, 1)
    cod_pct = round((cod_count / payment_total) * 100, 1)

    # === Low Stock Alerts ===
    low_stock_products = Product.objects.filter(stock__lt=10, available=True).order_by('stock')[:8]

    return render(request, 'dashboard/home.html', {
        # Basic KPIs
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'pending_orders': pending_orders,
        'monthly_revenue': monthly_revenue,
        'monthly_orders': monthly_orders,
        # Today
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'new_customers_today': new_customers_today,
        # Changes
        'revenue_change': revenue_change,
        'revenue_change_up': revenue_change >= 0,
        'orders_change': orders_change,
        'orders_change_up': orders_change >= 0,
        'users_change': users_change,
        'users_change_up': users_change >= 0,
        # Charts
        'monthly_chart': monthly_chart,
        'conic_gradient_css': conic_gradient_css,
        'status_data': status_data,
        # Top products
        'top_products': top_products,
        # Customers
        'recent_customers': recent_customers,
        # Payment
        'razorpay_count': razorpay_count,
        'cod_count': cod_count,
        'razorpay_pct': razorpay_pct,
        'cod_pct': cod_pct,
        # Low stock
        'low_stock_products': low_stock_products,
    })


@staff_member_required
def dashboard_orders(request):
    orders = Order.objects.all()
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/orders.html', {'orders': orders, 'status_filter': status_filter})


@staff_member_required
def dashboard_order_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}.')
    return redirect('dashboard_orders')


@staff_member_required
def dashboard_products(request):
    products = Product.objects.all()
    return render(request, 'dashboard/products.html', {'products': products})
