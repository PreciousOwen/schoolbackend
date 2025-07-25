from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@restaurant.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: admin/admin123')
        else:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Updated admin user password: admin/admin123')
        
        # Ensure profile exists
        profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        
        # Create chef user
        chef_user, created = User.objects.get_or_create(
            username='chef',
            defaults={
                'email': 'chef@restaurant.com',
                'first_name': 'Chef',
                'last_name': 'User',
            }
        )
        if created:
            chef_user.set_password('chef123')
            chef_user.save()
            self.stdout.write(f'Created chef user: chef/chef123')
        else:
            chef_user.set_password('chef123')
            chef_user.save()
            self.stdout.write(f'Updated chef user password: chef/chef123')
            
        # Ensure profile exists
        profile, created = UserProfile.objects.get_or_create(
            user=chef_user,
            defaults={'role': 'chef'}
        )
        
        self.stdout.write(self.style.SUCCESS('Test users created/updated successfully!'))