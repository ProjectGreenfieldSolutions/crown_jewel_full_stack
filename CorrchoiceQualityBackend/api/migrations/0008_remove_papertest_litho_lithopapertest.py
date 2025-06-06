# Generated by Django 4.2.13 on 2025-02-12 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_lithopaper_litho_lithopaper_litho_pt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='papertest',
            name='litho',
        ),
        migrations.CreateModel(
            name='LithoPaperTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('test_value', models.FloatField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.account')),
                ('litho_paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.lithopaper')),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.plant')),
                ('test_position', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.papertestposition')),
                ('test_reason', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.papertestreason')),
                ('test_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='api.papertesttype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
