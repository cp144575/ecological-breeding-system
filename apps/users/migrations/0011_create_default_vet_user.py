"""
文件功能：创建默认兽医分组与默认兽医账号（方案A：由管理员创建/指定兽医账号）。
"""

from django.db import migrations


def create_default_vet_user(apps, _schema_editor):
    """
    创建默认兽医分组与账号。

    参数：
        apps: Django 迁移 apps registry
        _schema_editor: schema editor

    返回值：
        None
    """
    group_model = apps.get_model('auth', 'Group')
    user_model = apps.get_model('users', 'User')

    vet_group, _created = group_model.objects.get_or_create(name='vet')

    from django.contrib.auth.hashers import make_password

    vet_user, created_user = user_model.objects.get_or_create(
        username='vet',
        defaults={
            'is_active': True,
            'is_staff': False,
            'password': make_password('123456'),
        },
    )

    if not created_user:
        if not vet_user.check_password('123456'):
            vet_user.password = make_password('123456')
            vet_user.save(update_fields=['password'])

    if not vet_user.groups.filter(name='vet').exists():
        vet_user.groups.add(vet_group)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_delete_vetprofile'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_default_vet_user, migrations.RunPython.noop),
    ]

