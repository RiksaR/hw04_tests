from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'testuser'
USERNAME2 = 'testuser2'
USERNAME3 = 'otheruser'
GROUP_TITLE_FOR_POST = 'test title post'
GROUP_SLUG_FOR_POST = 'test_slug_post'
GROUP_SLUG_FOR_STATUS_404 = 'test_slug_pos'
GROUP_DESCRIPTION_FOR_POST = 'test description post'
POST_TEXT = 'test text'

URL_FOR_INDEX = reverse('index')
URL_FOR_GROUP = reverse('group', args=(GROUP_SLUG_FOR_POST,))
URL_FOR_STATUS_404 = reverse('group', args=(GROUP_SLUG_FOR_STATUS_404,))
URL_FOR_NEW_POST = reverse('new_post')
URL_FOR_PROFILE = reverse('profile', args=(USERNAME,))


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user =  User.objects.create(
            username=USERNAME,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE_FOR_POST,
            slug=GROUP_SLUG_FOR_POST,
            description=GROUP_DESCRIPTION_FOR_POST,
        )
        cls.post1 = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.post2 = Post.objects.create(
            text=POST_TEXT,
            author=User.objects.create(username=USERNAME2),
            group=cls.group,
        )
        cls.URL_FOR_POST_EDIT = reverse(
            'post_edit',
            args=(USERNAME, cls.post1.id)
        )
        cls.URL_FOR_POST = reverse(
            'post',
            args=(USERNAME, cls.post1.id)
        )
        cls.URL_FOR_OTHER_USER = reverse(
            'post_edit',
            args=(USERNAME3, cls.post1.id)
        )
        cls.URL_FOR_POST_REDIRECT = reverse('post', args=(
            USERNAME2,
            cls.post2.id
            )
        )
        cls.URL_FOR_POST_EDIT_REDIRECT = reverse(
            'post_edit', args=(
                USERNAME2,
                cls.post2.id
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_client = self.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_client)

    def test_guest_urls_exists_at_desired_location(self):
        """Страница по заданному адресу доступна неавторизованному
        пользователю."""
        guest_url_names = {
            URL_FOR_INDEX: 200,
            URL_FOR_GROUP: 200,
            StaticURLTests.URL_FOR_POST_EDIT: 302,
            URL_FOR_STATUS_404: 404,
        }
        for url, status_code in guest_url_names.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_authorized_urls_exists_at_desired_location(self):
        """Страница по заданному адресу доступна авторизованному
        пользователю."""
        authorized_url_names = {
            URL_FOR_NEW_POST: 200,
            URL_FOR_PROFILE: 200,
            StaticURLTests.URL_FOR_POST: 200,
            StaticURLTests.URL_FOR_POST_EDIT: 200,
        }
        for url, status_code in authorized_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': URL_FOR_INDEX,
            'group.html': URL_FOR_GROUP,
            'new.html': URL_FOR_NEW_POST,
            'new.html': StaticURLTests.URL_FOR_POST_EDIT,
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страница по заданному адресу перенаправит анонимного
        пользователя на страницу логина."""
        redirect_url_names = {
            URL_FOR_NEW_POST: '/auth/login/?next=/new/',
            StaticURLTests.URL_FOR_OTHER_USER:
            '/auth/login/?next=/otheruser/1/edit/',
        }
        for url, redirect in redirect_url_names.items():
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, redirect)

    def test_for_post_edit_by_other_user(self):
        """Пользователь будет перенаправлен на страницу поста"""
        redirect_url_names = {
            StaticURLTests.URL_FOR_POST_EDIT_REDIRECT:
            StaticURLTests.URL_FOR_POST_REDIRECT,
        }
        for url, redirect in redirect_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url, follow=True)
                self.assertRedirects(
                    response, redirect)
