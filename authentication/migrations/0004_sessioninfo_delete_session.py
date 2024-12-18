# Generated by Django 5.1.4 on 2024-12-10 11:34

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_session'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device', models.CharField(blank=True, max_length=100, null=True)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('last_activity', models.DateTimeField(default=django.utils.timezone.now)),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='info', to='sessions.session')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_infos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Session',
        ),
    ]
