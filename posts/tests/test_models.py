from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
                username='testuser',
        )
        group = Group.objects.create(
                id=2,
                title='test title post',
                slug='test_slug_post',
                description='test description post',
        )
        Post.objects.create(
            id=1,
            text='test text',
            author=user,
            group=group,
        )
        cls.post = Post.objects.get(id=1)

    def test_verbose_name(self):
        """vervose_name в полях совпадает с ожидаемым."""

        post = PostModelTest.post
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

        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите ваше сообщение',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def text_object_name_is_string_field(self):
        """Вызов объекта как str должен вывести заданную строку"""

        post = PostModelTest.post
        if post.group is not None:
            expected_object_name = (f'Текст поста: "{post.text[:15]}...", '
                                    f'автор: {post.author.username}, '
                                    f'группа: {post.group}\n')
        expected_object_name = (f'Текст поста: "{post.text[:15]}...", '
                                f'автор: {post.author.username}\n')
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            id=1,
            title='test title group',
            slug='test_slug_group',
            description='test description group',
        )
        Group.objects.create(
                id=3,
                title='Ж'*100,
                description='test description slug',
        )
        cls.group = Group.objects.get(slug='test_slug_group')
        cls.group_for_slug = Group.objects.get(id=3)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""

        group = GroupModelTest.group
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

        group = GroupModelTest.group
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

        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_text_convert_to_slug(self):
        """save преобразует в slug содержимое поля title."""

        group_for_slug = GroupModelTest.group_for_slug
        expected_slug_name = group_for_slug.slug
        self.assertEqual(expected_slug_name, 'zh'*50)

    def test_text_slug_max_length_not_exceed(self):
        """Длинный slug обрезается и не больше slug max_length."""

        group_for_slug = GroupModelTest.group_for_slug
        max_length_slug = group_for_slug._meta.get_field('slug').max_length
        length_slug = (len(group_for_slug.slug))
        self.assertEqual(max_length_slug, length_slug)
