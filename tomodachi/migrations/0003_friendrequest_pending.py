# Generated by Django 4.0.2 on 2022-02-15 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tomodachi', '0002_appuser_friends_post_friendrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='pending',
            field=models.BooleanField(default=True),
        ),
    ]
