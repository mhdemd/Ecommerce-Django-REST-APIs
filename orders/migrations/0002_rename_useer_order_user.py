# Generated by Django 5.1.4 on 2024-12-29 18:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='useer',
            new_name='user',
        ),
    ]