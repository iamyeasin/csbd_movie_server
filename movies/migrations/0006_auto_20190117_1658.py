# Generated by Django 2.1.5 on 2019-01-17 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_students'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Students',
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='destination_location',
            field=models.FilePathField(max_length=200),
        ),
    ]
