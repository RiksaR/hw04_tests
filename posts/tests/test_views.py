from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
                username='testuser',
        )
        Group.objects.create(
                id=1,
                title='test title post',
                slug='test_slug_post',
                description='test description post',
        )
        Post.objects.create(
            id=1,
            text='test text',
            author=User.objects.get(username='testuser'),
            group=Group.objects.get(id=1),
        )
        cls.post = Post.objects.get(id=1)
        cls.group = Group.objects.get(id=1)
        cls.group2 = Group.objects.create(
            id=2,
            title='test title post 2',
            slug='test_slug_post_2',
            description='test description post 2',
        )
        cls.user = User.objects.get(username='testuser')

    def setUp(self):
        self.user_for_client = PostsPagesTests.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""

        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (reverse('group', args=('test_slug_post',))),
            'new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_shows_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('index'))
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        self.assertEqual(post_text, 'test text')
        self.assertEqual(post_author, User.objects.get(username='testuser'))
        self.assertEqual(post_group, PostsPagesTests.group)

    def test_page_group_shows_correct_context(self):
        """Шаблон group.html сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse(
            'group', args=('test_slug_post',))
        )
        group_text = response.context.get('page')[0]
        group_title = response.context.get('group').title
        group_slug = response.context.get('group').slug
        group_description = response.context.get('group').description
        self.assertEqual(group_text, PostsPagesTests.post)
        self.assertEqual(group_title, 'test title post')
        self.assertEqual(group_slug, 'test_slug_post')
        self.assertEqual(group_description, 'test description post')

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

    def test_new_post_display_correctly(self):
        """Новый пост создаётся корректно"""

        test_post = PostsPagesTests.post
        test_post.group = PostsPagesTests.group2
        test_post.save()
        response_group_with_post = self.authorized_client.get(reverse(
            'group', args=('test_slug_post_2',))
        )
        response_group_without_post = self.authorized_client.get(reverse(
            'group', args=('test_slug_post',))
        )
        response_index = self.authorized_client.get(reverse('index'))
        index_posts = response_index.context.get('page')
        group_with_post = response_group_with_post.context.get('page')
        group_without_post = response_group_without_post.context.get(
            'page'
        )
        self.assertNotIn(PostsPagesTests.post, group_without_post)
        self.assertIn(PostsPagesTests.post, group_with_post)
        self.assertIn(PostsPagesTests.post, index_posts)

    def test_page_new_post_edit_shows_correct_fields(self):
        """Шаблон new.html сформирован с правильным полями формы для
        редактируемого поста"""

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_client.get(reverse(
            'post_edit',
            args=('testuser', 1)
            )
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_new_post_edit_shows_correct_context(self):
        """Шаблон new.html сформирован с правильным контекстом для
        редактируемого поста"""

        response = self.authorized_client.get(reverse(
            'post_edit',
            args=('testuser', 1)
            )
        )
        post_text = response.context.get('post').text
        post_group = response.context.get('post').group
        self.assertEqual(post_text, 'test text')
        self.assertEqual(post_group, PostsPagesTests.group)

    def test_page_profile_shows_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом"""

        response = self.authorized_client.get(reverse(
            'profile',
            args=('testuser',),
            )
        )
        profile = response.context.get('profile')
        count = response.context.get('count')
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        self.assertEqual(post_text, 'test text')
        self.assertEqual(post_author, PostsPagesTests.user)
        self.assertEqual(post_group, PostsPagesTests.group)
        self.assertEqual(count, 1)
        self.assertEqual(profile, PostsPagesTests.user)

    def test_page_post_shows_correct_context(self):
        """Шаблон post.html сформирован с правильным контекстом"""

        response = self.authorized_client.get(reverse(
            'post',
            args=('testuser', 1),
            )
        )
        profile = response.context.get('profile')
        count = response.context.get('count')
        post_text = response.context.get('view_post').text
        post_author = response.context.get('view_post').author
        post_group = response.context.get('view_post').group
        self.assertEqual(post_text, 'test text')
        self.assertEqual(post_author, PostsPagesTests.user)
        self.assertEqual(post_group, PostsPagesTests.group)
        self.assertEqual(count, 1)
        self.assertEqual(profile, PostsPagesTests.user)
