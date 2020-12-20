from django.test import TestCase

from posts.models import Post, Group, User

USERNAME = 'testuser'
GROUP_TITLE_FOR_POST = 'test title post'
GROUP_SLUG_FOR_POST = 'test_slug_post'
GROUP_DESCRIPTION_FOR_POST = 'test description post'
POST_TEXT = 'test text'
GROUP_TITLE_FOR_GROUP = 'test title group'
GROUP_SLUG_FOR_GROUP = 'test_slug_group'
GROUP_DESCRIPTION_FOR_GROUP = 'test description group'


class PostModelTest(TestCase):
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

    def test_verbose_name(self):
        """vervose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст сообщения',
            'author': 'Автор сообщения',
            'group': 'Название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Введите ваше сообщение',
            'group': 'Вы можете выбрать группу для этого поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def text_object_name_is_string_field(self):
        """Вызов объекта как str должен вывести заданную строку"""
        post = self.post
        if post.group:
            expected_object_name = (f'Текст поста: "{post.text[:15]}...", '
                                    f'автор: {post.author.username}, '
                                    f'группа: {post.group}')
        expected_object_name = (f'Текст поста: "{post.text[:15]}...", '
                                f'автор: {post.author.username}')
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE_FOR_GROUP,
            slug=GROUP_SLUG_FOR_GROUP,
            description=GROUP_DESCRIPTION_FOR_GROUP,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Заголовок группы',
            'slug': 'Идентификатор группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            'title': 'Введите название группы длиной не более 200 символов',
            'slug': ('Slug группы должен быть уникальным и не превышать 100 '
                     'символов'),
            'description': 'Введите описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )

    def text_object_name_is_title_field(self):
        """Вызов объекта как str должен вывести содержимое поля title"""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
