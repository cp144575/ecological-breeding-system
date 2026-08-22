from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0013_remove_feedinfo_brand'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='diseasereport',
            name='treatment_plan',
            field=models.TextField(blank=True, null=True, verbose_name='处理意见'),
        ),
        migrations.AddField(
            model_name='diseasereport',
            name='handled_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='处理时间'),
        ),
        migrations.AddField(
            model_name='diseasereport',
            name='handled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_disease_reports', to=settings.AUTH_USER_MODEL, verbose_name='处理人'),
        ),
    ]

