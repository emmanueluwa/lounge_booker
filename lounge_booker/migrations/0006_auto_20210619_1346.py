# Generated by Django 3.0.8 on 2021-06-19 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lounge_booker', '0005_auto_20210619_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='lounge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setting', to='lounge_booker.Lounge'),
        ),
    ]