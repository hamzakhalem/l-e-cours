from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("core", "0002_drive_import_and_public_library")]

    operations = [
        migrations.CreateModel(
            name="Filiere",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_public", models.BooleanField(default=True)),
                ("folder", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="filiere_entry", to="core.folder")),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="filieres", to="core.drivesource")),
            ],
            options={"verbose_name": "شعبة", "verbose_name_plural": "الشعب", "ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="StudyLevel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_public", models.BooleanField(default=True)),
                ("filiere", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="levels", to="core.filiere")),
                ("folder", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="level_entry", to="core.folder")),
            ],
            options={"verbose_name": "مستوى", "verbose_name_plural": "المستويات", "ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(blank=True, max_length=40)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_public", models.BooleanField(default=True)),
                ("folder", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="subject_entry", to="core.folder")),
                ("level", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subjects", to="core.studylevel")),
            ],
            options={"verbose_name": "مادة", "verbose_name_plural": "المواد", "ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_public", models.BooleanField(default=True)),
                ("folder", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="course_entry", to="core.folder")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="courses", to="core.subject")),
            ],
            options={"verbose_name": "درس", "verbose_name_plural": "الدروس", "ordering": ["sort_order", "name"]},
        ),
    ]
