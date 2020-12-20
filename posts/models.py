from django.contrib.auth import get_user_model
from django.db import models

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
        help_text='Вы можете выбрать группу для этого поста',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        if self.group:
            return (f'Текст поста: "{self.text[:15]}...", '
                    f'автор: {self.author.username}, '
                    f'группа: {self.group}')
        return (f'Текст поста: "{self.text[:15]}...", '
                f'автор: {self.author.username}')
    # А можно оставить в таком виде? Красиво же=) Если нет, я исправлю.


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите ваш комментарий',
        max_length=200,
    )
    created = models.DateTimeField(
        'date_published',
        auto_now_add=True,
    )
