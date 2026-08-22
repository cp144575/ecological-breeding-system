from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('livestock', '0027_set_default_standard_cycle_for_six_categories'),
    ]

    operations = [
        migrations.RenameField(
            model_name='livestockbatch',
            old_name='birth_date',
            new_name='entry_date',
        ),
        migrations.AlterField(
            model_name='livestockbatch',
            name='entry_date',
            field=models.DateField(blank=True, null=True, verbose_name='入栏日期'),
        ),
    ]

