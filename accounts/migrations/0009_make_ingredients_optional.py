from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_restore_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.TextField(blank=True),
        ),
    ] 