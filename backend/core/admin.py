from django.contrib import admin
from .models import DriveSource, Folder, File, AuditLog, Filiere, StudyLevel, Subject, Course

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
    list_display = ("name", "source", "folder", "kind", "size_bytes", "modified_at")
    list_filter = ("source", "kind")
    search_fields = ("name", "mime_type")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "created_at")
    list_filter = ("action",)


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "is_public", "sort_order")
    list_filter = ("source", "is_public")
    search_fields = ("name",)

@admin.register(StudyLevel)
class StudyLevelAdmin(admin.ModelAdmin):
    list_display = ("name", "filiere", "is_public", "sort_order")
    list_filter = ("filiere", "is_public")
    search_fields = ("name", "filiere__name")

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "code", "is_public", "sort_order")
    list_filter = ("level__filiere", "is_public")
    search_fields = ("name", "code")

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "is_public", "sort_order")
    list_filter = ("subject__level__filiere", "is_public")
    search_fields = ("name", "description")
