# Generated by Django 5.2 on 2025-04-24 12:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-priority', '-created_at'], 'verbose_name': 'Task', 'verbose_name_plural': 'Tasks'},
        ),
        migrations.AlterField(
            model_name='task',
            name='assignee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Assignee'),
        ),
        migrations.AlterField(
            model_name='task',
            name='collaborators',
            field=models.ManyToManyField(blank=True, related_name='collaborating_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Collaborators'),
        ),
        migrations.AlterField(
            model_name='task',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='task',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateField(blank=True, null=True, verbose_name='Deadline'),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Urgent')], default=2, verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('TODO', 'To-Do'), ('INPROGRESS', 'In-Progress'), ('REVIEW', 'Code Review'), ('DONE', 'Done')], default='TODO', max_length=10, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='task',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.CreateModel(
            name='TaskHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('change_description', models.CharField(max_length=255, verbose_name='Change Description')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='tasks.task', verbose_name='Task')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User Performing Change')),
            ],
            options={
                'verbose_name': 'Task History Entry',
                'verbose_name_plural': 'Task History Entries',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
