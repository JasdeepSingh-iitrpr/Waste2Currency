# Generated by Django 3.0.3 on 2020-03-27 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waste2currency', '0002_auto_20200312_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waste',
            name='wtype',
            field=models.CharField(default='', max_length=200),
        ),
    ]
