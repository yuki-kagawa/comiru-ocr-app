# Generated by Django 5.0.14 on 2025-04-14 06:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_child'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='child',
            name='birth_date',
        ),
        migrations.AddField(
            model_name='child',
            name='birthday',
            field=models.DateField(default=datetime.date(2010, 8, 24)),
            preserve_default=False,
        ),
    ]
