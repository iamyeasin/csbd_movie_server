# Generated by Django 2.1.5 on 2019-01-17 07:45

from django.db import migrations, models
import movies.models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_auto_20190116_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=20)),
                ('age', models.PositiveIntegerField()),
                ('profile_pic', models.ImageField(upload_to=movies.models.upload_location)),
            ],
        ),
    ]
