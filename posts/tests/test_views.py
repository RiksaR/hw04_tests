
import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'testuser'
GROUP_TITLE_FOR_POST = 'test title post'
GROUP_SLUG_FOR_POST = 'test_slug_post'
GROUP_DESCRIPTION_FOR_POST = 'test description post'
POST_TEXT = 'test text'

URL_FOR_INDEX = reverse('index')
URL_FOR_GROUP = reverse('group', args=(GROUP_SLUG_FOR_POST,))
URL_FOR_NEW_POST = reverse('new_post')
URL_FOR_PROFILE = reverse('profile', args=(USERNAME,))


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(
            username=USERNAME,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE_FOR_POST,
            slug=GROUP_SLUG_FOR_POST,
            description=GROUP_DESCRIPTION_FOR_POST,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.URL_FOR_POST_EDIT = reverse(
            'post_edit',
            args=(USERNAME, cls.post.id)
        )
        cls.URL_FOR_POST = reverse(
            'post',
            args=(USERNAME, cls.post.id)
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user_for_client = self.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_pages_shows_correct_context(self):
        """Страница сформирована с корректным контекстом"""
        context_url_names = [
            URL_FOR_INDEX,
            URL_FOR_GROUP,
            URL_FOR_PROFILE,
            self.URL_FOR_POST,
        ]
        for url in context_url_names:
            with self.subTest():
                response = self.authorized_client.get(url)
                if 'page' in response.context:
                    post = response.context['page'][0]
                    self.assertTrue(1==len(response.context['page']))
                else:
                    post = response.context['post']
                self.assertTrue(self.post==post)

    def test_pages_shows_correct_author(self):
        """Контекстная переменная author содержит корректные данные"""
        context_url_names = [
            URL_FOR_PROFILE,
            self.URL_FOR_POST,
        ]
        for url in context_url_names:
            with self.subTest():
                response = self.authorized_client.get(url)
                author = response.context['author']
                self.assertTrue(self.user==author)

    def test_index_cache(self):
        """Кэширование страницы выполняется корректно"""
        page_before = self.authorized_client.get(URL_FOR_INDEX)
        content_before = page_before.content
        Post.objects.create(
            text='cache',
            author=self.user,
            group=self.group,
        )
        cache_page = self.authorized_client.get(URL_FOR_INDEX)
        cache_content = cache_page.content
        cache.clear()
        page_after = self.authorized_client.get(URL_FOR_INDEX)
        content_after = page_after.content
        self.assertTrue(content_before==cache_content)
        self.assertFalse(content_before==content_after)
