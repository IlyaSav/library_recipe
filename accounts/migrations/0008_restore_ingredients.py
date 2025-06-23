from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_recipe_ingredients_ingredient'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Ingredient',
        ),
    ] 