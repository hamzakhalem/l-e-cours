import hashlib
import mimetypes
from pathlib import Path

from django.conf import settings
from django.db.models import Count, Q, Sum
from django.http import Http404, HttpResponseRedirect
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .models import DriveSource, Folder, File, AuditLog, Filiere
from .serializers import DriveSourceSerializer, FolderSerializer, FileSerializer


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = DriveSourceSerializer
    queryset = DriveSource.objects.filter(is_active=True, is_public=True).annotate(
        folder_count=Count("folders", distinct=True), file_count=Count("files", distinct=True)
    )


class FolderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = FolderSerializer
    queryset = Folder.objects.filter(source__is_active=True, source__is_public=True).select_related("source").annotate(
        children_count=Count("children", distinct=True), files_count=Count("files", distinct=True)
    )
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        source = self.request.query_params.get("source")
        parent = self.request.query_params.get("parent")
        if source:
            qs = qs.filter(source_id=source)
        if parent is not None:
            qs = qs.filter(parent__isnull=True) if parent.lower() == "null" else qs.filter(parent_id=parent)
        return qs


class FileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == "upload":
            return [IsAuthenticated()]
        return [AllowAny()]
    serializer_class = FileSerializer
    queryset = File.objects.filter(source__is_active=True, source__is_public=True).select_related("source", "folder").all()
    search_fields = ["name", "mime_type"]
    ordering_fields = ["name", "size_bytes", "modified_at", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        source = self.request.query_params.get("source")
        folder = self.request.query_params.get("folder")
        kind = self.request.query_params.get("kind")
        if source:
            qs = qs.filter(source_id=source)
        if folder:
            qs = qs.filter(folder_id=folder)
        if kind:
            qs = qs.filter(kind=kind)
        return qs

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser], url_path="upload")
    def upload(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response({"detail": "أرفق ملفاً في الحقل file."}, status=status.HTTP_400_BAD_REQUEST)
        max_bytes = int(getattr(settings, "MAX_UPLOAD_SIZE", 50 * 1024 * 1024))
        if uploaded.size > max_bytes:
            return Response({"detail": f"حجم الملف يتجاوز الحد المسموح ({max_bytes // (1024 * 1024)} MB)."}, status=413)

        safe_name = Path(uploaded.name.replace("\\", "/")).name.strip()
        if not safe_name or safe_name in {".", ".."}:
            return Response({"detail": "اسم الملف غير صالح."}, status=400)
        ext = Path(safe_name).suffix.lower().lstrip(".")
        allowed = set(getattr(settings, "ALLOWED_UPLOAD_EXTENSIONS", []))
        if ext not in allowed:
            return Response({"detail": "نوع الملف غير مسموح به."}, status=415)

        try:
            source = DriveSource.objects.get(pk=request.data.get("source"), is_active=True)
        except (DriveSource.DoesNotExist, TypeError, ValueError):
            return Response({"detail": "مصدر التخزين غير صالح أو غير نشط."}, status=400)
        folder = None
        folder_id = request.data.get("folder")
        if folder_id:
            try:
                folder = Folder.objects.get(pk=folder_id, source=source)
            except (Folder.DoesNotExist, TypeError, ValueError):
                return Response({"detail": "المجلد غير صالح لهذا المصدر."}, status=400)

        kind_map = {
            "pdf": "pdf", "png": "image", "jpg": "image", "jpeg": "image", "gif": "image", "webp": "image",
            "doc": "document", "docx": "document", "odt": "document", "rtf": "document",
            "xls": "spreadsheet", "xlsx": "spreadsheet", "ods": "spreadsheet", "csv": "spreadsheet",
            "mp4": "video", "mov": "video", "webm": "video", "txt": "other", "md": "other",
        }
        digest = hashlib.sha256()
        for chunk in uploaded.chunks():
            digest.update(chunk)
        uploaded.seek(0)
        record = File.objects.create(
            source=source, folder=folder, name=safe_name,
            mime_type=uploaded.content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream",
            kind=kind_map.get(ext, "other"), size_bytes=uploaded.size, sha256=digest.hexdigest(),
            uploaded_file=uploaded, uploaded_by=request.user,
        )
        AuditLog.objects.create(user=request.user, action="file.upload", object_type="file",
                                object_id=str(record.pk), detail={"name": record.name, "size": record.size_bytes})
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="download", permission_classes=[AllowAny])
    def download(self, request, pk=None):
        record = self.get_object()
        if not record.uploaded_file:
            raise Http404("الملف غير متوفر في التخزين.")
        AuditLog.objects.create(user=request.user, action="file.download", object_type="file",
                                object_id=str(record.pk), detail={"name": record.name})
        return HttpResponseRedirect(record.uploaded_file.url)


@api_view(["GET"])
@permission_classes([AllowAny])
def dashboard(request):
    return Response({
        "sources": DriveSource.objects.filter(is_active=True, is_public=True).count(),
        "folders": Folder.objects.filter(source__is_active=True, source__is_public=True).count(),
        "files": File.objects.filter(source__is_active=True, source__is_public=True).count(),
        "total_size_bytes": File.objects.filter(source__is_active=True, source__is_public=True).aggregate(total=Sum("size_bytes"))["total"] or 0,
        "recent_files": FileSerializer(File.objects.filter(source__is_active=True, source__is_public=True).select_related("source", "folder").order_by("-created_at")[:8], many=True, context={"request": request}).data,
        "source_breakdown": DriveSourceSerializer(DriveSource.objects.filter(is_active=True, is_public=True).annotate(
            folder_count=Count("folders", distinct=True), file_count=Count("files", distinct=True)
        ), many=True).data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    q = request.query_params.get("q", "").strip()
    source = request.query_params.get("source")
    kind = request.query_params.get("kind")
    files = File.objects.filter(source__is_active=True, source__is_public=True).select_related("source", "folder").all()
    if q:
        files = files.filter(Q(name__icontains=q) | Q(mime_type__icontains=q))
    if source:
        files = files.filter(source_id=source)
    if kind:
        files = files.filter(kind=kind)
    return Response(FileSerializer(files.order_by("name")[:100], many=True, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def add_drive_source(request):
    from .drive_importer import extract_folder_id, sync_drive_source
    drive_url = (request.data.get("drive_url") or "").strip()
    label = (request.data.get("label") or "").strip()
    try:
        folder_id = extract_folder_id(drive_url)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    source = DriveSource.objects.create(
        name=label or f"Google Drive {folder_id[:8]}", label=label or "Google Drive",
        drive_url=drive_url, drive_folder_id=folder_id, is_public=True, sync_status="syncing"
    )
    try:
        counts = sync_drive_source(source)
    except Exception as exc:
        source.sync_status = "error"
        source.sync_error = str(exc)[:2000]
        source.save(update_fields=["sync_status", "sync_error"])
        return Response({"source": DriveSourceSerializer(source).data, "detail": str(exc)}, status=400)
    source.refresh_from_db()
    return Response({"source": DriveSourceSerializer(source).data, "imported": counts}, status=201)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def sync_drive(request, source_id):
    from .drive_importer import sync_drive_source
    try:
        source = DriveSource.objects.get(pk=source_id)
    except DriveSource.DoesNotExist:
        return Response({"detail": "المصدر غير موجود."}, status=404)
    try:
        counts = sync_drive_source(source)
    except Exception as exc:
        source.sync_status = "error"
        source.sync_error = str(exc)[:2000]
        source.save(update_fields=["sync_status", "sync_error"])
        return Response({"detail": str(exc)}, status=400)
    source.refresh_from_db()
    return Response({"source": DriveSourceSerializer(source).data, "imported": counts})


@api_view(["GET"])
@permission_classes([AllowAny])
def academic_structure(request):
    """Public nested catalogue generated from Drive folder hierarchy."""
    result = []
    filieres = Filiere.objects.filter(is_public=True, source__is_active=True, source__is_public=True).select_related("folder", "source").prefetch_related("levels__subjects__courses__folder")
    for filiere in filieres:
        levels_data = []
        for level in filiere.levels.filter(is_public=True).select_related("folder"):
            subjects_data = []
            for subject in level.subjects.filter(is_public=True).select_related("folder").prefetch_related("courses__folder"):
                courses_data = [{"id": c.id, "name": c.name, "folder_id": c.folder_id, "description": c.description}
                                for c in subject.courses.filter(is_public=True)]
                subjects_data.append({"id": subject.id, "name": subject.name, "code": subject.code, "folder_id": subject.folder_id, "courses": courses_data})
            levels_data.append({"id": level.id, "name": level.name, "folder_id": level.folder_id, "subjects": subjects_data})
        result.append({"id": filiere.id, "name": filiere.name, "source_id": filiere.source_id, "folder_id": filiere.folder_id, "levels": levels_data})
    return Response(result)
