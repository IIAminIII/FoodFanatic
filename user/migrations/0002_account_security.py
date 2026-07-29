import uuid

from django.db import migrations, models


def normalize_accounts(apps, schema_editor):
    AccountModel = apps.get_model("user", "AccountModel")
    AccountModel.objects.filter(is_activated__isnull=True).update(is_activated=False)


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            normalize_accounts,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="accountmodel",
            name="is_activated",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="accountmodel",
            name="email_token",
            field=models.UUIDField(
                blank=True,
                default=uuid.uuid4,
                editable=False,
                null=True,
                unique=True,
            ),
        ),
    ]
