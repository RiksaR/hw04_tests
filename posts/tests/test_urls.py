from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_for_post = User.objects.create(
                username='testuser',
        )
        Group.objects.create(
                id=2,
                title='test title post',
                slug='test_slug_post',
                description='test description post',
        )
        Post.objects.create(
            id=1,
            text='test text',
            author=user_for_post,
            group=Group.objects.get(id=2),
        )
        Post.objects.create(
            id=2,
            text='test text',
            author=User.objects.create(
                username='testuser2',
            ),
            group=Group.objects.get(id=2),
        )
        cls.group = Group.objects.get(id=2)
        cls.user_for_post = user_for_post

    def setUp(self):
        self.guest_client = Client()
        self.user_client = StaticURLTests.user_for_post
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_client)

    def test_guest_urls_exists_at_desired_location(self):
        """Страница по заданному адресу доступна неавторизованному
        пользователю."""

        guest_url_names = {
            '/': 200,
            '/group/test_slug_post/': 200,
            '/testuser/1/edit/': 302,
        }
        for url, status_code in guest_url_names.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_authorized_urls_exists_at_desired_location(self):
        """Страница по заданному адресу доступна авторизованному
        пользователю."""

        authorized_url_names = {
            '/new/': 200,
            '/testuser/': 200,
            '/testuser/1/': 200,
            '/testuser/1/edit/': 200,
        }
        for url, status_code in authorized_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test_slug_post/',
            'new.html': '/new/',
            'new.html': '/testuser/1/edit/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страница по заданному адресу перенаправит анонимного
        пользователя на страницу логина."""

        redirect_url_names = {
            '/new/': '/auth/login/?next=/new/',
            '/otheruser/1/edit/': '/auth/login/?next=/otheruser/1/edit/',
        }
        for url, redirect in redirect_url_names.items():
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, redirect)

    def test_for_post_edit_by_other_user(self):
        """Пользователь будет перенаправлен на страницу поста"""

        redirect_url_names = {
            '/testuser2/2/edit/': reverse('post', args=('testuser2', 2)),
        }
        for url, redirect in redirect_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url, follow=True)
                self.assertRedirects(
                    response, redirect)
