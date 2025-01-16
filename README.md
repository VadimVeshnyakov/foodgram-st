«Фудграм» — сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск проекта

1. Клонируйте репозиторий

2. Создайте файл `.env` в директории `infra` на основе `.env.example`:

3. В директории `infra` Запустите проект:
```bash
docker-compose up 
```

4. Выполните миграции:
```bash
docker-compose exec backend python manage.py migrate
```

5. Если нужно, заполните базу тестовыми данными:
```bash
docker-compose exec backend python manage.py loaddata test_data.json
```

## Адреса

- Веб-интерфейс: [Localhost](http://localhost/)
- API документация: [Localhost docs](http://localhost/api/docs/)
- Админ-панель: [Localhost admin](http://localhost/admin/)
