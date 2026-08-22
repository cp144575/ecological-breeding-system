from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0014_diseasereport_treatment_plan_and_handler'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='diseasereport',
            name='assigned_vet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_disease_reports', to=settings.AUTH_USER_MODEL, verbose_name='指派兽医'),
        ),
    ]

