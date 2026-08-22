from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('traceability_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livestocktrace',
            name='query_count',
        ),
    ]
