# Generated by Django 2.2.7 on 2019-12-08 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardapp', '0002_auto_20191208_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approved',
            name='answer',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboardapp.Answer'),
        ),
        migrations.AlterField(
            model_name='approved',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboardapp.Question'),
        ),
    ]
