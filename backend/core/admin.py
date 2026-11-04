from django.contrib import admin
from .models import DriveSource, Folder, File, AuditLog, StudyYear, Filiere, Speciality, Subject, ResourceCategory

@admin.register(DriveSource)
class DriveSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "label", "is_active", "is_public", "sync_status", "last_synced_at")
    search_fields = ("name", "label")

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "parent")
    list_filter = ("source",)
    search_fields = ("name",)

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "folder", "resource_category", "kind", "size_bytes", "modified_at")
    list_filter = ("source", "kind", "resource_category")
    search_fields = ("name", "mime_type")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "created_at")
    list_filter = ("action",)

@admin.register(StudyYear)
class StudyYearAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "is_public", "sort_order")
    list_editable = ("sort_order", "is_public")
    list_filter = ("source", "is_public")
    search_fields = ("name",)

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ("name", "study_year", "is_public", "sort_order")
    list_editable = ("sort_order", "is_public")
    list_filter = ("study_year", "is_public")
    search_fields = ("name",)

@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("name", "filiere", "code", "is_public", "sort_order")
    list_editable = ("sort_order", "is_public")
    list_filter = ("filiere", "is_public")
    search_fields = ("name",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "speciality", "code", "is_public", "sort_order")
    list_editable = ("sort_order", "is_public")
    list_filter = ("speciality__filiere__study_year", "is_public")
    search_fields = ("name", "code")

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "subject", "is_public", "sort_order")
    list_editable = ("sort_order", "is_public")
    list_filter = ("code", "is_public")
    search_fields = ("name", "subject__name")
