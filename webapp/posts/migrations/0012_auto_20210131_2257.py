# Generated by Django 2.2 on 2021-01-31 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_post_original_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='original_name',
            new_name='image_name',
        ),
    ]
