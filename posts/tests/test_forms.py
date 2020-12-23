import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'testuser'
GROUP_SLUG = 'test_slug_post'
GROUP_TITLE = 'test title post'
GROUP_DESCRIPTION = 'test description post'
POST_TEXT = 'test text'

URL_FOR_LOGIN = reverse('login')
URL_FOR_NEW_POST = reverse('new_post')
URL_FOR_INDEX = reverse('index')
URL_FOR_GROUP = reverse('group', args=(GROUP_SLUG,))
URL_FOR_NEW_POST_REDIRECT = (URL_FOR_LOGIN + '?next=' + URL_FOR_NEW_POST)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(
            username=USERNAME,
        )
        self.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        self.post = Post.objects.create(
            text=POST_TEXT,
            author=self.user,
            group=self.group,
        )
        self.URL_FOR_POST_EDIT = reverse(
            'post_edit',
            args=(
                USERNAME,
                self.post.id
            )
        )
        self.URL_FOR_GUEST_POST_EDIT = (
            URL_FOR_LOGIN +
            '?next=' +
            self.URL_FOR_POST_EDIT)
        self.URL_FOR_POST = reverse('post', args=(USERNAME, self.post.id))
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post с корректными данными"""
        post = Post.objects.first()
        post.delete()
        post.save()
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        group_for_create = Group.objects.create(
            title='test title post 2',
            slug='test_slug_post_2',
            description='test description post 2',
        )
        form_data = {
            'text': 'test text for create',
            'group': group_for_create.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            URL_FOR_NEW_POST,
            data=form_data,
            follow=True,
        )
        created_post = response.context['page'][0]
        self.assertRedirects(response, URL_FOR_INDEX)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group, group_for_create)
        self.assertEqual(created_post.author, self.user)
        self.assertIsNotNone(created_post.image)

    def test_post_created_in_expected_group(self):
        """Пост не попадает на чужую групп-ленту"""
        SLUG_FOR_TEST_GROUP = 'slug'
        URL_FOR_TEST_GROUP = reverse('group', args=(SLUG_FOR_TEST_GROUP,))
        Group.objects.create(
            title='title',
            slug=SLUG_FOR_TEST_GROUP,
            description='description',
        )
        response_for_test_group = self.authorized_client.get(
            URL_FOR_TEST_GROUP
        )
        context_for_test_group = response_for_test_group.context['page']
        self.assertNotIn(self.post, context_for_test_group)

    def test_create_post_by_anonymous(self):
        """Анонимный пользователь не сможет создать пост"""
        posts_count_before_try = Post.objects.count()
        group_for_anonymous = Group.objects.create(
            title='anonymous',
            slug='test_slug_anonymous',
            description='anonymous',
        )
        form_data = {
            'text': 'test text for anonymous',
            'group': group_for_anonymous.id,
        }
        response = self.guest_client.post(
            URL_FOR_NEW_POST,
            data=form_data,
            follow=True,
        )
        posts_count_after_try = Post.objects.count()
        self.assertRedirects(response, URL_FOR_NEW_POST_REDIRECT)
        self.assertEqual(posts_count_before_try, posts_count_after_try)

    def test_edit_post_by_anonymous(self):
        """Анонимный пользователь не сможет отредактировать пост"""
        response = self.guest_client.post(self.URL_FOR_POST_EDIT)
        self.assertRedirects(response, self.URL_FOR_GUEST_POST_EDIT)

    def test_change_post(self):
        """После редактирования поста изменяется соответствующая запись
        в базе данных"""
        group_for_edit = Group.objects.create(
            title='test title post 2',
            slug='test_slug_post_2',
            description='test description post 2',
        )
        form_data = {
            'text': 'edit text',
            'group': group_for_edit.id,
        }
        response = self.authorized_client.post(
            self.URL_FOR_POST_EDIT,
            data=form_data,
            follow=True,
        )
        post = response.context['post']
        self.assertRedirects(response, self.URL_FOR_POST)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, group_for_edit)

    def test_page_new_post_shows_correct_fields(self):
        """Шаблон new.html сформирован с правильными типами полей формы"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_new_post_edit_shows_correct_fields(self):
        """Шаблон new.html сформирован с правильным полями формы для
        редактируемого поста"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(
            self.URL_FOR_POST_EDIT
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
