# Generated by Django 2.0 on 2018-09-11 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_shop_shopitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopitem',
            name='shop',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.Shop'),
        ),
    ]
