# Initial schema for L-E-COURS.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='DriveSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('label', models.CharField(blank=True, max_length=120)),
                ('color', models.CharField(default='#64748b', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.folder')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='core.drivesource')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('mime_type', models.CharField(blank=True, max_length=150)),
                ('kind', models.CharField(choices=[('pdf', 'PDF'), ('image', 'Image'), ('document', 'Document'), ('spreadsheet', 'Spreadsheet'), ('video', 'Video'), ('other', 'Other')], default='other', max_length=20)),
                ('size_bytes', models.BigIntegerField(default=0)),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=255)),
                ('web_url', models.URLField(blank=True)),
                ('uploaded_file', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/')),
                ('sha256', models.CharField(blank=True, db_index=True, max_length=64)),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='core.folder')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='core.drivesource')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_files', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=80)),
                ('object_type', models.CharField(blank=True, max_length=80)),
                ('object_id', models.CharField(blank=True, max_length=120)),
                ('detail', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(model_name='folder', index=models.Index(fields=['source', 'parent', 'name'], name='fldr_src_par_nm_idx')),
        migrations.AddIndex(model_name='file', index=models.Index(fields=['source', 'folder', 'kind'], name='file_src_fldr_kind_idx')),
    ]
