# Generated by Django 5.1.7 on 2025-03-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_posts',
            field=models.ManyToManyField(blank=True, related_name='saved_by', to='app.blogpost'),
        ),
    ]
