# Generated by Django 2.2 on 2021-01-31 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20210131_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='original_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]