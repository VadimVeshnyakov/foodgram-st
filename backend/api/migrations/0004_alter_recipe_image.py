# Generated by Django 3.2.16 on 2025-01-14 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_recipeingredient_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Добавьте изображение рецепта', upload_to='recipes/', verbose_name='Фото'),
        ),
    ]
