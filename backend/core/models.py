from django.conf import settings
from django.db import models


class DriveSource(models.Model):
    name = models.CharField(max_length=120)
    label = models.CharField(max_length=120, blank=True)
    color = models.CharField(max_length=20, default="#64748b")
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    drive_url = models.URLField(blank=True)
    drive_folder_id = models.CharField(max_length=128, blank=True)
    sync_status = models.CharField(max_length=20, default="pending")
    sync_error = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.label or self.name


class Folder(models.Model):
    source = models.ForeignKey(DriveSource, on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    external_id = models.CharField(max_length=255, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["source", "parent", "name"], name="fldr_src_par_nm_idx")]

    def __str__(self):
        return self.name


class File(models.Model):
    class Kind(models.TextChoices):
        PDF = "pdf", "PDF"
        IMAGE = "image", "Image"
        DOCUMENT = "document", "Document"
        SPREADSHEET = "spreadsheet", "Spreadsheet"
        VIDEO = "video", "Video"
        OTHER = "other", "Other"

    source = models.ForeignKey(DriveSource, on_delete=models.CASCADE, related_name="files")
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.SET_NULL, related_name="files")
    resource_category = models.ForeignKey("ResourceCategory", null=True, blank=True, on_delete=models.SET_NULL, related_name="files")
    name = models.CharField(max_length=255, db_index=True)
    mime_type = models.CharField(max_length=150, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.OTHER)
    size_bytes = models.BigIntegerField(default=0)
    external_id = models.CharField(max_length=255, blank=True, db_index=True)
    web_url = models.URLField(blank=True)
    uploaded_file = models.FileField(upload_to="uploads/%Y/%m/", blank=True, null=True)
    sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="uploaded_files")
    modified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["source", "folder", "kind"], name="file_src_fldr_kind_idx")]

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events")
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=80, blank=True)
    object_id = models.CharField(max_length=120, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} ({self.object_type}:{self.object_id})"


class StudyYear(models.Model):
    """First academic level (e.g. Licence 3 or Master 1)."""
    source = models.ForeignKey(DriveSource, on_delete=models.CASCADE, related_name="study_years")
    folder = models.OneToOneField(Folder, on_delete=models.CASCADE, related_name="study_year_entry")
    name = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "سنة دراسية"
        verbose_name_plural = "السنوات الدراسية"

    def __str__(self):
        return self.name


class Filiere(models.Model):
    study_year = models.ForeignKey(StudyYear, on_delete=models.CASCADE, related_name="filieres")
    folder = models.OneToOneField(Folder, on_delete=models.CASCADE, related_name="filiere_entry")
    name = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "شعبة"
        verbose_name_plural = "الشعب"

    def __str__(self):
        return self.name


class Speciality(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name="specialities")
    folder = models.OneToOneField(Folder, on_delete=models.CASCADE, related_name="speciality_entry")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=40, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "تخصص"
        verbose_name_plural = "التخصصات"

    def __str__(self):
        return self.name


class Subject(models.Model):
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, related_name="subjects")
    folder = models.OneToOneField(Folder, on_delete=models.CASCADE, related_name="subject_entry")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "مادة"
        verbose_name_plural = "المواد"

    def __str__(self):
        return self.name


class ResourceCategory(models.Model):
    class Code(models.TextChoices):
        COURSE = "course", "Cours"
        TD = "td", "TD"
        EXAM = "exam", "Examens"
        OTHER = "other", "Autres"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="resource_categories")
    folder = models.OneToOneField(Folder, on_delete=models.CASCADE, related_name="resource_category_entry", null=True, blank=True)
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, choices=Code.choices, default=Code.OTHER)
    sort_order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "صنف مورد"
        verbose_name_plural = "أصناف الموارد"
        constraints = [models.UniqueConstraint(fields=["subject", "code"], name="uniq_subject_resource_category")]

    def __str__(self):
        return f"{self.subject.name} / {self.name}"

