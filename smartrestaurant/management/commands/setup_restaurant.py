# smartrestaurant/management/commands/setup_restaurant.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the restaurant with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating sample users',
        )
        parser.add_argument(
            '--skip-menu',
            action='store_true',
            help='Skip creating sample menu items',
        )
        parser.add_argument(
            '--skip-tables',
            action='store_true',
            help='Skip creating sample tables',
        )
        parser.add_argument(
            '--skip-notifications',
            action='store_true',
            help='Skip creating notification templates',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up SmartRestaurant...')
        )

        with transaction.atomic():
            if not options['skip_users']:
                self.create_users()
            
            if not options['skip_menu']:
                self.create_menu()
            
            if not options['skip_tables']:
                self.create_tables()
            
            if not options['skip_notifications']:
                self.create_notification_templates()

        self.stdout.write(
            self.style.SUCCESS('SmartRestaurant setup completed successfully!')
        )

    def create_users(self):
        """Create sample users"""
        self.stdout.write('Creating sample users...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@smartrestaurant.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: {admin.username}')

        # Create staff users
        staff_users = [
            {
                'username': 'chef1',
                'email': 'chef1@smartrestaurant.com',
                'password': 'chef123',
                'first_name': 'John',
                'last_name': 'Chef',
                'is_staff': True
            },
            {
                'username': 'server1',
                'email': 'server1@smartrestaurant.com',
                'password': 'server123',
                'first_name': 'Jane',
                'last_name': 'Server',
                'is_staff': True
            },
            {
                'username': 'manager1',
                'email': 'manager1@smartrestaurant.com',
                'password': 'manager123',
                'first_name': 'Mike',
                'last_name': 'Manager',
                'is_staff': True
            }
        ]

        for user_data in staff_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                self.stdout.write(f'Created staff user: {user.username}')

        # Create sample customers
        customer_users = [
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'password': 'customer123',
                'first_name': 'Alice',
                'last_name': 'Customer'
            },
            {
                'username': 'customer2',
                'email': 'customer2@example.com',
                'password': 'customer123',
                'first_name': 'Bob',
                'last_name': 'Customer'
            }
        ]

        for user_data in customer_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                self.stdout.write(f'Created customer user: {user.username}')

    def create_menu(self):
        """Create sample menu items"""
        self.stdout.write('Creating sample menu...')
        
        from menu.models import Category, MenuItem

        # Create categories
        categories_data = [
            {'name': 'Appetizers', 'description': 'Start your meal right'},
            {'name': 'Main Courses', 'description': 'Hearty main dishes'},
            {'name': 'Desserts', 'description': 'Sweet endings'},
            {'name': 'Beverages', 'description': 'Drinks and refreshments'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create menu items
        menu_items_data = [
            # Appetizers
            {
                'category': 'Appetizers',
                'name': 'Caesar Salad',
                'description': 'Fresh romaine lettuce with caesar dressing',
                'price': Decimal('12.99'),
                'stock': 50
            },
            {
                'category': 'Appetizers',
                'name': 'Chicken Wings',
                'description': 'Spicy buffalo wings with blue cheese',
                'price': Decimal('14.99'),
                'stock': 30
            },
            # Main Courses
            {
                'category': 'Main Courses',
                'name': 'Grilled Salmon',
                'description': 'Fresh Atlantic salmon with vegetables',
                'price': Decimal('24.99'),
                'stock': 20
            },
            {
                'category': 'Main Courses',
                'name': 'Ribeye Steak',
                'description': 'Premium ribeye steak cooked to perfection',
                'price': Decimal('32.99'),
                'stock': 15
            },
            {
                'category': 'Main Courses',
                'name': 'Chicken Parmesan',
                'description': 'Breaded chicken with marinara and mozzarella',
                'price': Decimal('19.99'),
                'stock': 25
            },
            # Desserts
            {
                'category': 'Desserts',
                'name': 'Chocolate Cake',
                'description': 'Rich chocolate cake with vanilla ice cream',
                'price': Decimal('8.99'),
                'stock': 40
            },
            {
                'category': 'Desserts',
                'name': 'Tiramisu',
                'description': 'Classic Italian dessert',
                'price': Decimal('9.99'),
                'stock': 20
            },
            # Beverages
            {
                'category': 'Beverages',
                'name': 'House Wine',
                'description': 'Red or white wine selection',
                'price': Decimal('7.99'),
                'stock': 100
            },
            {
                'category': 'Beverages',
                'name': 'Craft Beer',
                'description': 'Local craft beer selection',
                'price': Decimal('5.99'),
                'stock': 80
            },
            {
                'category': 'Beverages',
                'name': 'Fresh Juice',
                'description': 'Orange, apple, or cranberry juice',
                'price': Decimal('3.99'),
                'stock': 60
            }
        ]

        for item_data in menu_items_data:
            category_name = item_data.pop('category')
            category = categories[category_name]
            
            item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                category=category,
                defaults={**item_data, 'category': category}
            )
            if created:
                self.stdout.write(f'Created menu item: {item.name}')

    def create_tables(self):
        """Create sample tables"""
        self.stdout.write('Creating sample tables...')
        
        from reservations.models import Table

        tables_data = [
            {'number': 1, 'seats': 2, 'description': 'Intimate table for two'},
            {'number': 2, 'seats': 2, 'description': 'Window table for two'},
            {'number': 3, 'seats': 4, 'description': 'Family table for four'},
            {'number': 4, 'seats': 4, 'description': 'Corner table for four'},
            {'number': 5, 'seats': 6, 'description': 'Large table for six'},
            {'number': 6, 'seats': 8, 'description': 'Party table for eight'},
            {'number': 7, 'seats': 2, 'description': 'Bar seating for two'},
            {'number': 8, 'seats': 4, 'description': 'Patio table for four'},
        ]

        for table_data in tables_data:
            table, created = Table.objects.get_or_create(
                number=table_data['number'],
                defaults=table_data
            )
            if created:
                self.stdout.write(f'Created table: Table {table.number}')

    def create_notification_templates(self):
        """Create notification templates"""
        self.stdout.write('Creating notification templates...')
        
        from notifications.models import NotificationTemplate

        templates_data = [
            # Email templates
            {
                'name': 'Order Confirmed Email',
                'event_type': NotificationTemplate.ORDER_CONFIRMED,
                'notification_type': NotificationTemplate.EMAIL,
                'subject': 'Order Confirmed - {{ restaurant_name }}',
                'html_template': '''
                <h2>Order Confirmed!</h2>
                <p>Hi {{ user.first_name }},</p>
                <p>Your order #{{ order_id }} has been confirmed.</p>
                <p>Total: ${{ order_total }}</p>
                <p>Thank you for choosing {{ restaurant_name }}!</p>
                ''',
                'text_template': '''
                Order Confirmed!
                Hi {{ user.first_name }},
                Your order #{{ order_id }} has been confirmed.
                Total: ${{ order_total }}
                Thank you for choosing {{ restaurant_name }}!
                '''
            },
            {
                'name': 'Order Ready Email',
                'event_type': NotificationTemplate.ORDER_READY,
                'notification_type': NotificationTemplate.EMAIL,
                'subject': 'Your Order is Ready - {{ restaurant_name }}',
                'html_template': '''
                <h2>Your Order is Ready!</h2>
                <p>Hi {{ user.first_name }},</p>
                <p>Your order #{{ order_id }} is ready for pickup/serving.</p>
                <p>Thank you for your patience!</p>
                ''',
                'text_template': '''
                Your Order is Ready!
                Hi {{ user.first_name }},
                Your order #{{ order_id }} is ready for pickup/serving.
                Thank you for your patience!
                '''
            },
            # SMS templates
            {
                'name': 'Order Ready SMS',
                'event_type': NotificationTemplate.ORDER_READY,
                'notification_type': NotificationTemplate.SMS,
                'sms_template': 'Hi {{ user.first_name }}, your order #{{ order_id }} is ready! - {{ restaurant_name }}'
            },
            # Reservation templates
            {
                'name': 'Reservation Confirmed Email',
                'event_type': NotificationTemplate.RESERVATION_CONFIRMED,
                'notification_type': NotificationTemplate.EMAIL,
                'subject': 'Reservation Confirmed - {{ restaurant_name }}',
                'html_template': '''
                <h2>Reservation Confirmed!</h2>
                <p>Hi {{ user.first_name }},</p>
                <p>Your reservation for {{ party_size }} people on {{ start_time }} at Table {{ table_number }} has been confirmed.</p>
                <p>We look forward to seeing you!</p>
                ''',
                'text_template': '''
                Reservation Confirmed!
                Hi {{ user.first_name }},
                Your reservation for {{ party_size }} people on {{ start_time }} at Table {{ table_number }} has been confirmed.
                We look forward to seeing you!
                '''
            }
        ]

        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                event_type=template_data['event_type'],
                notification_type=template_data['notification_type'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created notification template: {template.name}')

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
