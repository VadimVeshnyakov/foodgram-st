«Фудграм» — сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск проекта

1. Клонируйте репозиторий
```bash
git clone git@github.com:VadimVeshnyakov/foodgram-st.git
```

2. Перейдите в директорию `infra`
```bash
cd foodgram-st/infra
```
```bash
touch .env
```

3. Создайте файл `.env` в директории `infra` на основе `.env.example`:

4. В директории `infra` Запустите проект:
```bash
docker-compose up 
```

5. Выполните миграции:
```bash
docker-compose exec backend python manage.py migrate
```

6. Если нужно, заполните базу ингредиентами и тестовыми данными:
```bash
docker-compose exec backend python manage.py load_ingredients
```

## Адреса

- Веб-интерфейс: [Localhost](http://localhost/)
- API документация: [Localhost docs](http://localhost/api/docs/)
- Админ-панель: [Localhost admin](http://localhost/admin/)
