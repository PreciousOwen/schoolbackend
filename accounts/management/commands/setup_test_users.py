# accounts/management/commands/setup_test_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users with different roles for testing the role-based system'

    def handle(self, *args, **options):
        # Test users data
        test_users = [
            {
                'username': 'admin',
                'email': 'admin@restaurant.com',
                'password': 'admin123',
                'first_name': 'John',
                'last_name': 'Manager',
                'role': 'admin',
                'phone': '+255 123 456 789',
                'address': 'Dar es Salaam, Tanzania'
            },
            {
                'username': 'chef',
                'email': 'chef@restaurant.com',
                'password': 'chef123',
                'first_name': 'Maria',
                'last_name': 'Rodriguez',
                'role': 'chef',
                'phone': '+255 987 654 321',
                'address': 'Dar es Salaam, Tanzania'
            },
            {
                'username': 'server1',
                'email': 'alice@restaurant.com',
                'password': 'server123',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': 'server',
                'phone': '+255 555 123 456',
                'address': 'Dar es Salaam, Tanzania'
            },
            {
                'username': 'server2',
                'email': 'bob@restaurant.com',
                'password': 'server123',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'role': 'server',
                'phone': '+255 444 789 012',
                'address': 'Dar es Salaam, Tanzania'
            }
        ]

        self.stdout.write(self.style.SUCCESS('Creating test users...'))

        for user_data in test_users:
            # Extract role and other profile data
            role = user_data.pop('role')
            phone = user_data.pop('phone')
            address = user_data.pop('address')
            
            # Create or get user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'✅ Created user: {user.username}')
            else:
                self.stdout.write(f'👤 User already exists: {user.username}')
            
            # Create or update profile
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': role,
                    'phone': phone,
                    'address': address,
                    'hire_date': date.today(),
                    'is_active': True
                }
            )
            
            if not profile_created:
                # Update existing profile
                profile.role = role
                profile.phone = phone
                profile.address = address
                if not profile.hire_date:
                    profile.hire_date = date.today()
                profile.is_active = True
                profile.save()
                self.stdout.write(f'🔄 Updated profile for: {user.username}')
            else:
                self.stdout.write(f'📝 Created profile for: {user.username}')

        self.stdout.write(self.style.SUCCESS('\n🎉 Test users setup complete!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now login with:'))
        self.stdout.write(self.style.SUCCESS('👑 Admin: username=admin, password=admin123'))
        self.stdout.write(self.style.SUCCESS('👨‍🍳 Chef: username=chef, password=chef123'))
        self.stdout.write(self.style.SUCCESS('🍽️ Server: username=server1, password=server123'))
        self.stdout.write(self.style.SUCCESS('🍽️ Server: username=server2, password=server123'))
        self.stdout.write(self.style.SUCCESS('\nEach user will see a different dashboard based on their role!'))
