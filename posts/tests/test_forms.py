from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post, User

USERNAME = 'testuser'
GROUP_SLUG = 'test_slug_post'
GROUP_TITLE = 'test title post'
GROUP_DESCRIPTION = 'test description post'
POST_TEXT = 'test text'

URL_FOR_NEW_POST = reverse('new_post')
URL_FOR_INDEX = reverse('index')
URL_FOR_GROUP = reverse('group', args=(GROUP_SLUG,))


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
                username=USERNAME,
        )
        cls.group = Group.objects.create(
                title=GROUP_TITLE,
                slug=GROUP_SLUG,
                description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.URL_FOR_POST_EDIT = reverse(
            'post_edit',
            args=(
                USERNAME,
                cls.post.id
            )
        )
        cls.URL_FOR_POST = reverse('post', args=(USERNAME, cls.post.id))

    def setUp(self):
        self.user_for_client = self.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        TEST_GROUP_TITLE = 'test title post 2'
        TEST_GROUP_SLUG = 'test_slug_post_2'
        TEST_GROUP_DESCRIPTION = 'test description post 2'
        TEXT_FOR_CREATE = 'test text for create'
        posts_count = Post.objects.count()
        group_for_create = Group.objects.create(
                title=TEST_GROUP_TITLE,
                slug=TEST_GROUP_SLUG,
                description=TEST_GROUP_DESCRIPTION,
        )
        form_data = {
            'text': TEXT_FOR_CREATE,
            'group': group_for_create.id,
        }
        response = self.authorized_client.post(
            URL_FOR_NEW_POST,
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(text=TEXT_FOR_CREATE, group=group_for_create)
        response_get = self.authorized_client.get(
            reverse('post', args=(USERNAME, post.id))
        )
        response_get_group = self.authorized_client.get(URL_FOR_GROUP)
        post_in_group = response_get_group.context.get('page')
        text = response_get.context.get('view_post').text
        group = response_get.context.get('view_post').group
        author = response_get.context.get('view_post').author
        self.assertRedirects(response, URL_FOR_INDEX)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(text, TEXT_FOR_CREATE)
        self.assertEqual(group, group_for_create)
        self.assertEqual(author, PostCreateFormTests.user)
        self.assertNotIn(post, post_in_group)

    def test_change_post(self):
        """После редактирования поста изменяется соответствующая запись
        в базе данных"""
        EDIT_GROUP_TITLE = 'test title post 2'
        EDIT_GROUP_SLUG = 'test_slug_post_2'
        EDIT_GROUP_DESCRIPTION = 'test description post 2'
        TEXT_FOR_POST_EDIT = 'edit text'
        group_for_edit = Group.objects.create(
                title=EDIT_GROUP_TITLE,
                slug=EDIT_GROUP_SLUG,
                description=EDIT_GROUP_DESCRIPTION,
        )
        form_data = {
            'text': TEXT_FOR_POST_EDIT,
            'group': group_for_edit.id,
        }
        response = self.authorized_client.post(
            PostCreateFormTests.URL_FOR_POST_EDIT,
            data=form_data,
            follow=True,
        )
        response_get = self.authorized_client.get(
            PostCreateFormTests.URL_FOR_POST
        )
        text = response_get.context.get('view_post').text
        group = response_get.context.get('view_post').group
        self.assertRedirects(response, PostCreateFormTests.URL_FOR_POST)
        self.assertEqual(text, TEXT_FOR_POST_EDIT)
        self.assertEqual(group, group_for_edit)

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
            PostCreateFormTests.URL_FOR_POST_EDIT
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
