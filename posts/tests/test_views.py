
from django.test import Client, TestCase
from django.urls import reverse
#from django.core.files.uploadedfile import SimpleUploadedFile
#import shutil
#import tempfile
#from django.conf import settings

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
        #settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(
            username=USERNAME,
        )
        #cls.small_gif = (
        #    b'\x47\x49\x46\x38\x39\x61\x02\x00'
        #    b'\x01\x00\x80\x00\x00\x00\x00\x00'
        #    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        #    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        #    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        #    b'\x0A\x00\x3B'
        #)
        #cls.uploaded = SimpleUploadedFile(
        #    name='small.gif',
        #    content=cls.small_gif,
        #    content_type='image/gif'
        #)
        cls.group = Group.objects.create(
            title=GROUP_TITLE_FOR_POST,
            slug=GROUP_SLUG_FOR_POST,
            description=GROUP_DESCRIPTION_FOR_POST,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        #    image=cls.uploaded,
        )
        cls.URL_FOR_POST_EDIT = reverse(
            'post_edit',
            args=(USERNAME, cls.post.id)
        )
        cls.URL_FOR_POST = reverse(
            'post',
            args=(USERNAME, cls.post.id)
        )

    #@classmethod
    #def tearDownClass(cls):
    #    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
    #    super().tearDownClass()

    def setUp(self):
        self.user_for_client = self.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)

    def test_pages_shows_correct_context(self):
        """Шаблон сформирован с правильным контекстом"""
        context_url_names = {
            URL_FOR_INDEX: 'page',
            URL_FOR_GROUP: 'page',
            URL_FOR_PROFILE: 'page',
        }
        for reverse_name, context in context_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                context = response.context[context]
                self.assertIn(self.post, context)

    def test_page_new_post_edit_shows_correct_context(self):
        """Шаблон new.html сформирован с правильным контекстом для
        страницы редактирования поста"""
        response = self.authorized_client.get(
            self.URL_FOR_POST_EDIT
        )
        post = response.context['post']
        self.assertEqual(post.text, 'test text')
        self.assertEqual(post.group, self.group)

    def test_page_profile_shows_correct_author(self):
        """Шаблон profile.html принимает правильный контекст из
        переменной author"""
        response = self.authorized_client.get(URL_FOR_PROFILE)
        author = response.context['author']
        self.assertEqual(author, self.user)

    def test_page_post_shows_correct_context(self):
        """Шаблон post.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(self.URL_FOR_POST)
        post = response.context['view_post']
        self.assertEqual(post.text, 'test text')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
    # Если перенести эту проверку в test_pages_shows_correct_context
    # Выдаёт ошибку, т.к. на страницу поста не передаётся список
    # объектов, и выдаёт ошибку, что аргументы типа Post не итерируются
    # по этой причине я оставил проверку автора в этом тесте,
    # и отдельно сделал проверку автора для страницы profile
