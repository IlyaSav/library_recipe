# Generated by Django 5.0.2 on 2025-06-23 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='moderation_status',
            field=models.CharField(choices=[('pending', 'На модерации'), ('approved', 'Одобрен'), ('rejected', 'Отклонён')], default='pending', max_length=10),
        ),
    ]
