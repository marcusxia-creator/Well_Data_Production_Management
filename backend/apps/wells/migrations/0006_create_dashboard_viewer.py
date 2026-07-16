from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations

VIEWER_GROUP_NAME = "Dashboard and Production Viewer"
VIEWER_USERNAME = "User1"
VIEWER_PASSWORD = "TTI2026Test"


def create_viewer(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Group = apps.get_model("auth", "Group")
    group, _ = Group.objects.get_or_create(name=VIEWER_GROUP_NAME)
    user, _ = User.objects.get_or_create(username=VIEWER_USERNAME, defaults={"is_active": True, "is_staff": False, "is_superuser": False})
    user.password = make_password(VIEWER_PASSWORD)
    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    user.save(update_fields=["password", "is_active", "is_staff", "is_superuser"])
    user.groups.add(group)


def remove_viewer(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    User.objects.filter(username=VIEWER_USERNAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("wells", "0005_move_header_attributes_to_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [migrations.RunPython(create_viewer, remove_viewer)]
