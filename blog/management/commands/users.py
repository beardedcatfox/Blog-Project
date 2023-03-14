from blog.models import Author, Comment, Post

from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker


class Command(BaseCommand):
    help = 'Generate fake data for the Author, Post, and Comment models'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--posts', type=int, default=5, help='Number of posts for each user')
        parser.add_argument('--comments', type=int, default=3, help='Number of comments for each post')

    def handle(self, *args, **options):
        fake = Faker()
        users_count = options['users']
        posts_per_user = options['posts']
        comments_per_post = options['comments']

        for i in range(users_count):
            user = Author.objects.create_user(
                username=fake.user_name(),
                password=fake.password(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text(),
                birth_date=fake.date_of_birth(),
                location=fake.city(),
            )

            for j in range(posts_per_user):
                post = Post.objects.create(
                    owner=user,
                    title=fake.sentence(),
                    short_description=fake.sentence(),
                    full_description=fake.paragraphs(nb=3),
                    image=None,
                    is_published=True,
                    published_date=timezone.now(),
                )

                for k in range(comments_per_post):
                    Comment.objects.create(
                        post=post,
                        author=fake.name(),
                        text=fake.paragraph(),
                        is_published=True,
                        published_date=timezone.now(),
                    )

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {users_count} users, '
                                             f'{users_count * posts_per_user} posts, '
                                             f'and {users_count * posts_per_user * comments_per_post} comments'))
