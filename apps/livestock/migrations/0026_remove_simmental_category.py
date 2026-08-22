from django.db import migrations


def remove_simmental_category(apps, schema_editor):
    livestock_category = apps.get_model('livestock', 'LivestockCategory')
    livestock_batch = apps.get_model('livestock', 'LivestockBatch')

    simmental_categories = livestock_category.objects.filter(name__contains='西门塔尔')
    if not simmental_categories.exists():
        return

    cow_category = livestock_category.objects.filter(name='牛').order_by('id').first()
    if cow_category is None:
        cow_category = livestock_category.objects.create(
            name='牛',
            standard_cycle=0,
            description=None,
        )

    cow_code = (getattr(cow_category, 'category_code', None) or '').strip().upper()
    if not cow_code:
        if not livestock_category.objects.filter(category_code='D').exclude(id=cow_category.id).exists():
            cow_category.category_code = 'D'
            cow_category.save(update_fields=['category_code'])

    simmental_ids = list(simmental_categories.values_list('id', flat=True))
    livestock_batch.objects.filter(category_id__in=simmental_ids).update(category_id=cow_category.id)
    livestock_category.objects.filter(id__in=simmental_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('livestock', '0025_remove_livestockbatch_name'),
    ]

    operations = [
        migrations.RunPython(remove_simmental_category, migrations.RunPython.noop),
    ]

