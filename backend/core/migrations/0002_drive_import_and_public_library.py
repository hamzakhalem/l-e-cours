from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="drivesource",
            name="is_public",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="drivesource",
            name="drive_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="drivesource",
            name="drive_folder_id",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="drivesource",
            name="sync_status",
            field=models.CharField(default="pending", max_length=20),
        ),
        migrations.AddField(
            model_name="drivesource",
            name="sync_error",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="drivesource",
            name="last_synced_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
