from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(
        unique=True,
        max_length=200,
        verbose_name='Email',
        help_text='Введите ваш email'
    )
    username = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя'
    )
    first_name = models.CharField(
        max_length=200,
        verbose_name='Имя',
        help_text='Введите ваше имя'
    )
    last_name = models.CharField(
        max_length=200,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию'
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на пользователя',
        help_text='Вы можете подписаться на данного автора'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
