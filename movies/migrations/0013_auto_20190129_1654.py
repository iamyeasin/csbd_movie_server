# Generated by Django 2.1.5 on 2019-01-29 10:54

from django.db import migrations, models
import movies.models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0012_mainfeaturehead'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_image',
            field=models.FileField(blank=True, max_length=700, upload_to=movies.models.upload_location),
        ),
        migrations.AddField(
            model_name='category',
            name='frontpage_feature',
            field=models.BooleanField(default=False),
        ),
    ]