from django.db import migrations, models
import django.db.models.deletion


def seed_categories_and_assign_files(apps, schema_editor):
    Subject = apps.get_model('core', 'Subject')
    ResourceCategory = apps.get_model('core', 'ResourceCategory')
    File = apps.get_model('core', 'File')
    Folder = apps.get_model('core', 'Folder')
    aliases = {
        'course': ('course', 'cours', 'lecture', 'lectures', 'محاضرات', 'دروس', 'درس'),
        'td': ('td', 'tutorial', 'tutorials', 'travaux diriges', 'تمارين', 'اعمال موجهة'),
        'exam': ('exam', 'exams', 'examens', 'اختبار', 'اختبارات', 'امتحان', 'امتحانات'),
        'other': ('other', 'others', 'autres', 'أخرى', 'اخرى', 'متفرقات'),
    }
    labels = {'course': 'Cours', 'td': 'TD', 'exam': 'Examens', 'other': 'Autres'}
    for subject in Subject.objects.all().iterator():
        categories = {}
        child_folders = Folder.objects.filter(parent_id=subject.folder_id)
        for folder in child_folders:
            value = folder.name.strip().lower()
            code = next((key for key, words in aliases.items() if value in words), 'other')
            category, _ = ResourceCategory.objects.get_or_create(
                subject_id=subject.pk, code=code,
                defaults={'name': labels[code], 'folder_id': folder.pk, 'sort_order': list(labels).index(code)},
            )
            if not category.folder_id:
                category.folder_id = folder.pk
                category.save(update_fields=['folder'])
            categories[folder.pk] = category
        for code, label in labels.items():
            ResourceCategory.objects.get_or_create(
                subject_id=subject.pk, code=code,
                defaults={'name': label, 'sort_order': list(labels).index(code)},
            )
        for folder_id, category in categories.items():
            File.objects.filter(folder_id=folder_id, resource_category__isnull=True).update(resource_category_id=category.pk)
        other = ResourceCategory.objects.get(subject_id=subject.pk, code='other')
        File.objects.filter(folder_id=subject.folder_id, resource_category__isnull=True).update(resource_category_id=other.pk)


class Migration(migrations.Migration):
    dependencies = [('core', '0003_academic_catalogue')]

    operations = [
        migrations.RenameModel(old_name='Filiere', new_name='StudyYear'),
        migrations.RenameModel(old_name='StudyLevel', new_name='Filiere'),
        migrations.RenameModel(old_name='Subject', new_name='Speciality'),
        migrations.RenameModel(old_name='Course', new_name='Subject'),
        migrations.RenameField(model_name='filiere', old_name='filiere', new_name='study_year'),
        migrations.RenameField(model_name='speciality', old_name='level', new_name='filiere'),
        migrations.RenameField(model_name='subject', old_name='subject', new_name='speciality'),
        migrations.AlterField(model_name='studyyear', name='source', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_years', to='core.drivesource')),
        migrations.AlterField(model_name='filiere', name='study_year', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filieres', to='core.studyyear')),
        migrations.AlterField(model_name='speciality', name='filiere', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specialities', to='core.filiere')),
        migrations.AlterField(model_name='subject', name='speciality', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='core.speciality')),
        migrations.AlterField(model_name='studyyear', name='folder', field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='study_year_entry', to='core.folder')),
        migrations.AlterField(model_name='filiere', name='folder', field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='filiere_entry', to='core.folder')),
        migrations.AlterField(model_name='speciality', name='folder', field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='speciality_entry', to='core.folder')),
        migrations.AlterField(model_name='subject', name='folder', field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subject_entry', to='core.folder')),
        migrations.AlterField(model_name='subject', name='speciality', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='core.speciality')),
        migrations.AddField(model_name='subject', name='code', field=models.CharField(blank=True, max_length=40)),
        migrations.AlterModelOptions(name='studyyear', options={'ordering': ['sort_order', 'name'], 'verbose_name': 'سنة دراسية', 'verbose_name_plural': 'السنوات الدراسية'}),
        migrations.AlterModelOptions(name='filiere', options={'ordering': ['sort_order', 'name'], 'verbose_name': 'شعبة', 'verbose_name_plural': 'الشعب'}),
        migrations.AlterModelOptions(name='speciality', options={'ordering': ['sort_order', 'name'], 'verbose_name': 'تخصص', 'verbose_name_plural': 'التخصصات'}),
        migrations.AlterModelOptions(name='subject', options={'ordering': ['sort_order', 'name'], 'verbose_name': 'مادة', 'verbose_name_plural': 'المواد'}),
        migrations.CreateModel(name='ResourceCategory', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=120)),
            ('code', models.CharField(choices=[('course', 'Cours'), ('td', 'TD'), ('exam', 'Examens'), ('other', 'Autres')], default='other', max_length=20)),
            ('sort_order', models.PositiveIntegerField(default=0)),
            ('is_public', models.BooleanField(default=True)),
            ('folder', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resource_category_entry', to='core.folder')),
            ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_categories', to='core.subject')),
        ], options={'ordering': ['sort_order', 'name'], 'verbose_name': 'صنف مورد', 'verbose_name_plural': 'أصناف الموارد'}),
        migrations.AddField(model_name='file', name='resource_category', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='core.resourcecategory')),
        migrations.AddConstraint(model_name='resourcecategory', constraint=models.UniqueConstraint(fields=('subject', 'code'), name='uniq_subject_resource_category')),
        migrations.RunPython(seed_categories_and_assign_files, migrations.RunPython.noop),
    ]
