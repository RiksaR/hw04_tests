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
URL_FOR_NEW_POST_REDIRECT = (reverse('login') + '?next=' + reverse('new_post'))


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
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
        cls.URL_FOR_OTHER_USER_REDIRECT = (
            reverse('login') +
            '?next=' +
            reverse(
                'post_edit',
                args=(USERNAME3, cls.post1.id),
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_client = self.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_client)

    def test_urls_exists_at_desired_location(self):
        """Страница по заданному адресу возвращает ожидаемый status_code"""
        expected_status_code = [
            [URL_FOR_INDEX, 200, self.guest_client],
            [URL_FOR_GROUP, 200, self.guest_client],
            [URL_FOR_NEW_POST, 302, self.guest_client],
            [URL_FOR_PROFILE, 200, self.guest_client],
            [self.URL_FOR_POST, 200, self.guest_client],
            [self.URL_FOR_POST_EDIT, 302, self.guest_client],
            [URL_FOR_STATUS_404, 404, self.guest_client],
            [URL_FOR_INDEX, 200, self.authorized_client],
            [URL_FOR_GROUP, 200, self.authorized_client],
            [URL_FOR_NEW_POST, 200, self.authorized_client],
            [URL_FOR_PROFILE, 200, self.authorized_client],
            [self.URL_FOR_POST, 200, self.authorized_client],
            [self.URL_FOR_POST_EDIT, 200, self.authorized_client],
            [URL_FOR_STATUS_404, 404, self.authorized_client],
        ]
        for url, status_code, client in expected_status_code:
            with self.subTest():
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            URL_FOR_INDEX: 'index.html',
            URL_FOR_GROUP: 'group.html',
            URL_FOR_NEW_POST: 'new.html',
            self.URL_FOR_POST_EDIT: 'new.html',
            self.URL_FOR_POST: 'post.html',
            URL_FOR_PROFILE: 'profile.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Redirect корректно срабатывает для авторизованного
        и неавторизованного пользователя"""
        expected_redirect = [
            [
                URL_FOR_NEW_POST,
                URL_FOR_NEW_POST_REDIRECT,
                self.guest_client
            ],
            [
                self.URL_FOR_OTHER_USER,
                self.URL_FOR_OTHER_USER_REDIRECT,
                self.guest_client,
            ],
            [
                self.URL_FOR_POST_EDIT_REDIRECT,
                self.URL_FOR_POST_REDIRECT,
                self.authorized_client,
            ],
        ]
        for url, redirect, client in expected_redirect:
            with self.subTest():
                response = client.get(url, follow=True)
                self.assertRedirects(
                    response, redirect)
