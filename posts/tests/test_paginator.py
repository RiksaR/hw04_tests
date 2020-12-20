from django.urls import reverse
from django.test import TestCase, Client

from posts.models import Group, Post, User

USERNAME_FOR_CLIENT = 'alexey'
USERNAME = 'testuser'
GROUP_TITLE_FOR_POST = 'test title post'
GROUP_SLUG_FOR_POST = 'test_slug_post'
GROUP_DESCRIPTION_FOR_POST = 'test description post'
POST_TEXT = 'test text'

URL_FOR_INDEX = reverse('index')
URL_FOR_INDEX_SECOND_PAGE = reverse('index') + '?page=2'
URL_FOR_GROUP = (reverse('group', args=(GROUP_SLUG_FOR_POST,)))
URL_FOR_GROUP_SECOND_PAGE = (reverse(
            'group', args=(GROUP_SLUG_FOR_POST,)
            ) + '?page=2')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=USERNAME,
        )
        cls.group =  Group.objects.create(
            title=GROUP_TITLE_FOR_POST,
            slug=GROUP_SLUG_FOR_POST,
            description=GROUP_DESCRIPTION_FOR_POST,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_for_client = User.objects.create(
            username=USERNAME_FOR_CLIENT
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_first_page_containse_ten_records(self):
        """Paginator правильно отображает заданное количество постов"""
        posts_list = []
        for count in range(0, 13):
            user = User.objects.create(
                username=(f'testuser{count}'),
            )
            group = Group.objects.create(
                title=(f'test title number {count}'),
                slug=(f'test_slug_post_{count}'),
                description=(f'test description post {count}'),
            )
            posts = Post.objects.create(
                text=(f'test text {count}'),
                author=user,
                group=group,
            )
            posts_list.append(posts)
        response = self.guest_client.get(URL_FOR_INDEX)
        self.assertEqual(len(response.context['page']), 10)

    def test_second_page_containse_three_records(self):
        """Paginator правильно отображает заданное количество постов"""
        posts_list = []
        for count in range(0, 13):
            user = User.objects.create(
                username=(f'testuser{count}'),
            )
            group = Group.objects.create(
                title=(f'test title number {count}'),
                slug=(f'test_slug_post_{count}'),
                description=(f'test description post {count}'),
            )
            posts = Post.objects.create(
                text=(f'test text {count}'),
                author=user,
                group=group,
            )
            posts_list.append(posts)
        response = self.guest_client.get(URL_FOR_INDEX_SECOND_PAGE)
        self.assertEqual(len(response.context['page']), 3)

    def test_first_page_group_containse_ten_records(self):
        """Paginator правильно отображает заданное количество постов"""
        posts_list = []
        for count in range(0, 13):
            posts = Post.objects.create(
                text=(f'test text {count}'),
                author=self.user,
                group=self.group,
            )
            posts_list.append(posts)
        response = self.guest_client.get(URL_FOR_GROUP)
        self.assertEqual(len(response.context['page']), 10)

    def test_second_page_group_containse_three_records(self):
        """Paginator правильно отображает заданное количество постов"""
        posts_list = []
        for count in range(0, 13):
            posts = Post.objects.create(
                text=(f'test text {count}'),
                author=self.user,
                group=self.group,
            )
            posts_list.append(posts)
        response = self.guest_client.get(URL_FOR_GROUP_SECOND_PAGE)
        self.assertEqual(len(response.context['page']), 3)
