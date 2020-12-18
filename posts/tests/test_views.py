
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
        cls.user = User.objects.create(
            username=USERNAME,
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
        )
        cls.URL_FOR_POST_EDIT = reverse(
            'post_edit',
            args=(USERNAME, cls.post.id)
        )
        cls.URL_FOR_POST = reverse(
            'post',
            args=(USERNAME, cls.post.id)
        )

    def setUp(self):
        self.user_for_client = self.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            'index.html': URL_FOR_INDEX,
            'group.html': URL_FOR_GROUP,
            'new.html': URL_FOR_NEW_POST,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_shows_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_FOR_INDEX)
        post = response.context.get('page')
        self.assertIn(PostsPagesTests.post, post)

    def test_page_group_shows_correct_context(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_FOR_GROUP)
        group = response.context.get('page')
        self.assertIn(PostsPagesTests.post, group)

    def test_page_new_post_edit_shows_correct_context(self):
        """Шаблон new.html сформирован с правильным контекстом для
        редактируемого поста"""
        response = self.authorized_client.get(
            PostsPagesTests.URL_FOR_POST_EDIT
        )
        post_text = response.context.get('post').text
        post_group = response.context.get('post').group
        self.assertEqual(post_text, 'test text')
        self.assertEqual(post_group, PostsPagesTests.group)

    def test_page_profile_shows_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(URL_FOR_PROFILE)
        author = response.context.get('author')
        post = response.context.get('page')
        self.assertIn(PostsPagesTests.post, post)
        self.assertEqual(author, PostsPagesTests.user)

    def test_page_post_shows_correct_context(self):
        """Шаблон post.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostsPagesTests.URL_FOR_POST)
        author = response.context.get('author')
        post_text = response.context.get('view_post').text
        post_author = response.context.get('view_post').author
        post_group = response.context.get('view_post').group
        self.assertEqual(post_text, 'test text')
        self.assertEqual(post_author, PostsPagesTests.user)
        self.assertEqual(post_group, PostsPagesTests.group)
        self.assertEqual(author, PostsPagesTests.user)
