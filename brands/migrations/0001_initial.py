# Generated by Django 5.1.4 on 2024-12-07 07:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Required, unique, max 255 characters', max_length=255, unique=True, verbose_name='Brand Name')),
                ('slug', models.SlugField(help_text='Unique URL identifier for the brand.', max_length=255, unique=True, verbose_name='Brand Slug')),
                ('description', models.TextField(blank=True, help_text='Optional', null=True, verbose_name='Brand Description')),
                ('logo', models.ImageField(blank=True, help_text='Optional', null=True, upload_to='brand_logos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])], verbose_name='Brand Logo')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Format: Y-m-d H:M:S', verbose_name='Date Brand Created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Format: Y-m-d H:M:S', verbose_name='Date Brand Updated')),
            ],
            options={
                'verbose_name': 'Brand',
                'verbose_name_plural': 'Brands',
                'ordering': ['name'],
            },
        ),
    ]
