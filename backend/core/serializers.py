from rest_framework import serializers
from .models import DriveSource, Folder, File

class DriveSourceSerializer(serializers.ModelSerializer):
    folder_count = serializers.IntegerField(read_only=True)
    file_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = DriveSource
        fields = ["id", "name", "label", "color", "is_active", "is_public", "drive_url", "sync_status", "sync_error", "last_synced_at", "folder_count", "file_count"]

class FolderSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.label", read_only=True)
    children_count = serializers.IntegerField(read_only=True)
    files_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Folder
        fields = ["id", "source", "source_name", "name", "parent", "external_id", "children_count", "files_count"]

class FileSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.label", read_only=True)
    folder_name = serializers.CharField(source="folder.name", read_only=True, allow_null=True)
    size_display = serializers.SerializerMethodField()
    has_upload = serializers.SerializerMethodField()
    class Meta:
        model = File
        fields = ["id", "source", "source_name", "folder", "folder_name", "name", "mime_type",
                  "kind", "size_bytes", "size_display", "external_id", "web_url", "modified_at", "created_at", "sha256", "has_upload"]
        read_only_fields = fields
    def get_size_display(self, obj):
        size = float(obj.size_bytes or 0)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024 or unit == "TB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
    def get_has_upload(self, obj):
        return bool(obj.uploaded_file)
