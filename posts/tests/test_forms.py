from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
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
            author=user,
            group=Group.objects.get(id=1),
        )
        cls.user = User.objects.get(username='testuser')
        cls.post = Post.objects.get(id=1)

    def setUp(self):
        self.user_for_client = PostCreateFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()
        group_for_test = Group.objects.create(
                id=2,
                title='test title post 2',
                slug='test_slug_post2',
                description='test description post 2',
        )
        form_data = {
            'text': 'test text for create',
            'group': group_for_test.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_change_post(self):
        """После редактирования поста изменяется соответствующая запись
        в базе данных"""

        post_for_edit = PostCreateFormTests.post
        group_for_edit = Group.objects.create(
                id=2,
                title='test title post 2',
                slug='test_slug_post2',
                description='test description post 2',
        )
        post_for_edit.text = 'edit text'
        post_for_edit.group = group_for_edit
        post_for_edit.save
        form_data = {
            'text': 'edit text',
            'group': group_for_edit.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=('testuser', 1)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('post', args=('testuser', 1)))
        self.assertEqual(post_for_edit.text, 'edit text')
        self.assertEqual(post_for_edit.group, group_for_edit)
