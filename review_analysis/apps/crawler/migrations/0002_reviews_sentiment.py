# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-14 05:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviews',
            name='sentiment',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
