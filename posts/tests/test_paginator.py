from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user_for_client = User.objects.create(username=('alexey'))
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_first_page_containse_ten_records(self):
        """Paginator правильно отображает заданное количество постов"""

        posts_list = []
        for i in range(0, 13):
            user = User.objects.create(
                username=(f'testuser{i}'),
            )
            group = Group.objects.create(
                id=i,
                title=(f'test title number {i}'),
                slug=(f'test_slug_post_{i}'),
                description=(f'test description post {i}'),
            )
            posts = Post.objects.create(
                id=i,
                text=(f'test text {i}'),
                author=user,
                group=group,
            )
            posts_list.append(posts)

        response = self.guest_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        """Paginator правильно отображает заданное количество постов"""

        posts_list = []
        for i in range(0, 13):
            user = User.objects.create(
                username=(f'testuser{i}'),
            )
            group = Group.objects.create(
                id=i,
                title=(f'test title number {i}'),
                slug=(f'test_slug_post_{i}'),
                description=(f'test description post {i}'),
            )
            posts = Post.objects.create(
                id=i,
                text=(f'test text {i}'),
                author=user,
                group=group,
            )
            posts_list.append(posts)

        response = self.guest_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_first_page_group_containse_ten_records(self):
        """Paginator правильно отображает заданное количество постов"""

        user = User.objects.create(
                username='testuser',
        )
        group = Group.objects.create(
                id=2,
                title='test title post',
                slug='test_slug_post',
                description='test description post',
        )
        posts_list = []
        for i in range(0, 13):
            posts = Post.objects.create(
                id=i,
                text=(f'test text {i}'),
                author=user,
                group=group,
            )
            posts_list.append(posts)

        response = self.guest_client.get(reverse(
            'group', args=('test_slug_post',)
            )
        )
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_group_containse_three_records(self):
        """Paginator правильно отображает заданное количество постов"""

        posts_list = []
        user = User.objects.create(
                username='testuser',
            )
        group = Group.objects.create(
            id=1,
            title='test title number',
            slug='test_slug_post',
            description='test description post',
        )
        for i in range(0, 13):
            posts = Post.objects.create(
                id=i,
                text=(f'test text {i}'),
                author=user,
                group=group,
            )
            posts_list.append(posts)

        response = self.guest_client.get(reverse(
            'group', args=('test_slug_post',)
            ) + '?page=2'
        )
        self.assertEqual(len(response.context.get('page').object_list), 3)
