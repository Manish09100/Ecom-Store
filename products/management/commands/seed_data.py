from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Seed the database with sample categories and products'

    def handle(self, *args, **kwargs):
        # Categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Clothing', 'slug': 'clothing'},
            {'name': 'Books', 'slug': 'books'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'], defaults={'name': cat_data['name']}
            )
            categories[cat_data['slug']] = cat
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {cat.name}')

        # Products
        products_data = [
            {
                'category': 'electronics', 'name': 'Wireless Bluetooth Headphones',
                'slug': 'wireless-bluetooth-headphones',
                'description': 'Premium wireless headphones with noise cancellation, 30-hour battery life, and crystal-clear sound quality.',
                'price': 2999, 'discount_price': 1999, 'stock': 50, 'featured': True,
                'image': 'products/wireless-bluetooth-headphones.jfif',
            },
            {
                'category': 'electronics', 'name': 'Smartphone 128GB',
                'slug': 'smartphone-128gb',
                'description': 'Latest smartphone with 128GB storage, 48MP camera, and AMOLED display.',
                'price': 15999, 'discount_price': 13999, 'stock': 30, 'featured': True,
                'image': 'products/smartphone-128gb.jpg',
            },
            {
                'category': 'electronics', 'name': 'USB-C Laptop Charger 65W',
                'slug': 'usb-c-laptop-charger-65w',
                'description': 'Universal 65W USB-C fast charger compatible with all laptops and devices.',
                'price': 1499, 'stock': 100,
                'image': 'products/usb-c-laptop-charger.jfif',
            },
            {
                'category': 'electronics', 'name': 'Portable Power Bank 20000mAh',
                'slug': 'portable-power-bank-20000mah',
                'description': 'High-capacity power bank with dual USB ports and fast charging support.',
                'price': 1299, 'discount_price': 999, 'stock': 75,
                'image': 'products/portable-power-bank.jfif',
            },
            {
                'category': 'clothing', 'name': 'Cotton Casual T-Shirt',
                'slug': 'cotton-casual-tshirt',
                'description': 'Comfortable 100% cotton t-shirt, available in multiple colors. Perfect for everyday wear.',
                'price': 599, 'discount_price': 399, 'stock': 200, 'featured': True,
                'image': 'products/cotton-casual-tshirt.jfif',
            },
            {
                'category': 'clothing', 'name': 'Slim Fit Denim Jeans',
                'slug': 'slim-fit-denim-jeans',
                'description': 'Classic slim fit denim jeans with stretch fabric for maximum comfort.',
                'price': 1499, 'discount_price': 1199, 'stock': 100,
                'image': 'products/slim-fit-denim-jeans.jfif',
            },
            {
                'category': 'clothing', 'name': 'Running Sports Shoes',
                'slug': 'running-sports-shoes',
                'description': 'Lightweight running shoes with cushioned sole and breathable mesh upper.',
                'price': 2499, 'discount_price': 1899, 'stock': 60, 'featured': True,
                'image': 'products/running-sports-shoes.jfif',
            },
            {
                'category': 'clothing', 'name': 'Winter Jacket',
                'slug': 'winter-jacket',
                'description': 'Warm and stylish winter jacket with water-resistant outer shell.',
                'price': 3499, 'stock': 40,
                'image': 'products/winter-jacket.jfif',
            },
            {
                'category': 'books', 'name': 'Learn Python Programming',
                'slug': 'learn-python-programming',
                'description': 'An in-depth introduction to the fundamentals of Python (Third Edition).',
                'price': 699, 'discount_price': 499, 'stock': 150, 'featured': True,
                'image': 'products/manish1.jpg',
            },
            {
                'category': 'books', 'name': 'Data Structures and Algorithms Made Easy',
                'slug': 'data-structures-algorithms-made-easy',
                'description': 'Essential textbook covering all major data structures and algorithmic puzzles with examples.',
                'price': 899, 'stock': 80,
                'image': 'products/dsa-made-easy-new.jfif',
            },
            {
                'category': 'books', 'name': 'Fundamentals of Software Development',
                'slug': 'fundamentals-software-development',
                'description': 'Comprehensive guide to the core principles of software engineering for students.',
                'price': 599, 'discount_price': 449, 'stock': 120,
                'image': 'products/fundamentals-software-dev-new.jfif',
            },
            {
                'category': 'home-kitchen', 'name': 'Stainless Steel Water Bottle 1L',
                'slug': 'stainless-steel-water-bottle',
                'description': 'Double-wall insulated stainless steel water bottle that keeps drinks cold for 24 hours.',
                'price': 799, 'discount_price': 599, 'stock': 200, 'featured': True,
                'image': 'products/stainless-steel-water-bottle.jfif',
            },
            {
                'category': 'home-kitchen', 'name': 'Non-Stick Cooking Pan Set',
                'slug': 'non-stick-cooking-pan-set',
                'description': '3-piece non-stick cooking pan set with ergonomic handles and even heat distribution.',
                'price': 1999, 'discount_price': 1499, 'stock': 45,
                'image': 'products/non-stick-cooking-pan-set.jfif',
            },
            {
                'category': 'home-kitchen', 'name': 'LED Desk Lamp',
                'slug': 'led-desk-lamp',
                'description': 'Adjustable LED desk lamp with 3 brightness levels and USB charging port.',
                'price': 999, 'stock': 90, 'featured': True,
                'image': 'products/led-desk-lamp.jfif',
            },
            {
                'category': 'home-kitchen', 'name': 'Ceramic Coffee Mug Set',
                'slug': 'ceramic-coffee-mug-set',
                'description': 'Set of 4 elegant ceramic coffee mugs with modern minimalist design.',
                'price': 699, 'discount_price': 549, 'stock': 110,
                'image': 'products/ceramic-coffee-mug-set.jfif',
            },
        ]

        for prod_data in products_data:
            category = categories[prod_data.pop('category')]
            prod, created = Product.objects.update_or_create(
                slug=prod_data['slug'],
                defaults={**prod_data, 'category': category, 'available': True},
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {prod.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {Category.objects.count()} categories, {Product.objects.count()} products.'
        ))
