# Generated by Django 2.1.5 on 2019-01-21 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0009_auto_20190118_0011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadmovie',
            name='destination_location',
            field=models.CharField(max_length=7024),
        ),
    ]
