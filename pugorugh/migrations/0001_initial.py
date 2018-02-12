# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-02-12 06:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image_filename', models.CharField(max_length=100)),
                ('breed', models.CharField(blank=True, max_length=100)),
                ('age', models.IntegerField()),
                ('gender', models.CharField(max_length=1)),
                ('size', models.CharField(max_length=2)),
                ('sterilized', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserDog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=1)),
                ('dog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pugorugh.Dog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.CharField(default='b,y,a,s', max_length=20)),
                ('gender', models.CharField(default='m,f', max_length=20)),
                ('size', models.CharField(default='s,m,l,xl', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userdog',
            unique_together=set([('user', 'dog')]),
        ),
    ]