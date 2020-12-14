from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок группы',
        help_text='Введите название группы длиной не более 200 символов',
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='Идентификатор группы',
        help_text=('Slug группы должен быть уникальным и не превышать 100 '
                   'символов'),
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы',
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Введите ваше сообщение',
    )
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор сообщения',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Выберите группу',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        if self.group is not None:
            return (f'Текст поста: "{self.text[:15]}...", '
                    f'автор: {self.author.username}, '
                    f'группа: {self.group}\n')
        return (f'Текст поста: "{self.text[:15]}...", '
                f'автор: {self.author.username}\n')
