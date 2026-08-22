from django.db import migrations


def set_default_standard_cycles(apps, schema_editor):
    LivestockCategory = apps.get_model('livestock', 'LivestockCategory')

    default_cycles = {
        '鸡': 45,
        '鸭': 50,
        '鹅': 80,
        '牛': 540,
        '羊': 180,
        '猪': 180,
    }

    for name, standard_cycle in default_cycles.items():
        LivestockCategory.objects.filter(name=name, standard_cycle__lte=0).update(standard_cycle=standard_cycle)


class Migration(migrations.Migration):

    dependencies = [
        ('livestock', '0026_remove_simmental_category'),
    ]

    operations = [
        migrations.RunPython(set_default_standard_cycles, migrations.RunPython.noop),
    ]

