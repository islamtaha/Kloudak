# Generated by Django 2.0.5 on 2018-06-18 20:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ControllerAPI', '0004_vmtask_oldconf'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vmtask',
            name='oldConf',
        ),
    ]