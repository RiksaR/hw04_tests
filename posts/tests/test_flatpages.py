from django.contrib.flatpages.models import FlatPage
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.sites.models import Site

ABOUT_AUTHOR = reverse('about_author')
ABOUT_SPEC = reverse('about_spec')


class StaticPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site_name = Site(
            id=1,
            domain='127.0.0.1:8000',
            name='127.0.0.1:8000')
        cls.site_name.save()
        cls.about_author = FlatPage.objects.create(
            url=ABOUT_AUTHOR,
            title='test title for flatpage "about-author"',
            content='test content about author'
        )
        cls.about_spec = FlatPage.objects.create(
            url=ABOUT_SPEC,
            title='test title for flatpage "about-spec"',
            content='test content about spec'
        )
        cls.about_author.sites.add(cls.site_name)
        cls.about_spec.sites.add(cls.site_name)

    def setUp(self):
        self.guest_client = Client()

    def test_flatpage_about_author(self):
        """Страница по заданному URL доступна неавторизованному
        пользователю
        """
        flatpages_url_names = {
            ABOUT_AUTHOR: 200,
            ABOUT_SPEC: 200,
        }
        for url, status_code in flatpages_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)
