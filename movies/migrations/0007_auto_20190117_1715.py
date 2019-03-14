# Generated by Django 2.1.5 on 2019-01-17 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_auto_20190117_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadmovie',
            name='cast',
            field=models.CharField(max_length=650),
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='destination_location',
            field=models.FilePathField(max_length=600),
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='director',
            field=models.CharField(max_length=650),
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='genre',
            field=models.CharField(max_length=650),
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='movie_title',
            field=models.CharField(max_length=650),
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='plot',
            field=models.CharField(max_length=6600),
        ),
        migrations.AlterField(
            model_name='uploadmovie',
            name='writer',
            field=models.CharField(max_length=650),
        ),
    ]
