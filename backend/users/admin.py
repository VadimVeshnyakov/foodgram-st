from django.contrib import admin

from .models import MyUser, Subscription


@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    '''Возможность редактировать и удалять все данные о пользователях.
    Поиск по адресу электронной почты и имени пользователя.'''

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'avatar',
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    '''Настройки отображения данных о подписках.'''

    list_display = ('user', 'following')
