from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create test users for chat application'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=3, help='Number of test users to create')

    def handle(self, *args, **options):
        count = options['count']
        created_users = []
        
        for i in range(1, count + 1):
            username = f'testuser{i}'
            email = f'testuser{i}@example.com'
            password = 'testpass123'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=f'Test',
                    last_name=f'User {i}'
                )
                created_users.append(username)
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username} (password: {password})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists')
                )
        
        if created_users:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {len(created_users)} users')
            )
            self.stdout.write('You can now use these users to test the chat application:')
            for username in created_users:
                self.stdout.write(f'  Username: {username}, Password: testpass123')
        else:
            self.stdout.write(
                self.style.WARNING('No new users were created')
            )
