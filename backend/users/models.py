from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):

    email = models.EmailField(
        'email',
        max_length=254,
        blank=False,
        unique=True
    )   
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    avatar = models.ImageField('Аватар', upload_to='users/images/',
                               null=True, blank=True)


class Subscription(models.Model):
    user = models.ForeignKey(
        MyUser,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        MyUser,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follows',
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан на {self.following.username}'
