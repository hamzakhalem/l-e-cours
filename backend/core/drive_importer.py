import hashlib
import io
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone as django_timezone

from .models import DriveSource, Folder, File, Filiere, StudyLevel, Subject, Course

FOLDER_MIME = "application/vnd.google-apps.folder"
GOOGLE_NATIVE_PREFIX = "application/vnd.google-apps."


def extract_folder_id(value: str) -> str:
    value = (value or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", value):
        return value
    match = re.search(r"/folders/([A-Za-z0-9_-]+)", value)
    if match:
        return match.group(1)
    query = parse_qs(urlparse(value).query)
    if query.get("id"):
        return query["id"][0]
    raise ValueError("رابط Google Drive غير صالح. استعمل رابط مجلد يحتوي على /folders/.")


def sync_drive_source(source: DriveSource) -> dict:
    api_key = getattr(settings, "GOOGLE_DRIVE_API_KEY", "")
    if not api_key:
        raise RuntimeError("لازم تضيف GOOGLE_DRIVE_API_KEY في backend/.env لتفعيل استيراد Google Drive.")
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
    except ImportError as exc:
        raise RuntimeError("حزمة google-api-python-client غير مثبتة. نفّذ pip install -r requirements.txt.") from exc

    service = build("drive", "v3", developerKey=api_key, cache_discovery=False)
    root_id = source.drive_folder_id or extract_folder_id(source.drive_url)
    max_bytes = int(getattr(settings, "GOOGLE_DRIVE_IMPORT_MAX_FILE_SIZE", 50 * 1024 * 1024))
    max_total_bytes = int(getattr(settings, "GOOGLE_DRIVE_IMPORT_MAX_TOTAL_SIZE", 500 * 1024 * 1024))
    counters = {"folders": 0, "files": 0, "downloaded_files": 0, "skipped_large": 0,
                "skipped_total_limit": 0, "bytes_downloaded": 0, "google_native_files": 0, "download_errors": 0}

    def list_children(parent_id):
        page_token = None
        while True:
            response = service.files().list(
                q=f"'{parent_id}' in parents and trashed = false",
                pageSize=1000, pageToken=page_token,
                orderBy="folder,name",
                fields="nextPageToken,files(id,name,mimeType,size,modifiedTime,webViewLink,webContentLink)",
                supportsAllDrives=True, includeItemsFromAllDrives=True
            ).execute()
            yield from response.get("files", [])
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    def fetch_binary(file_id, expected_size):
        remaining_total = max_total_bytes - counters["bytes_downloaded"]
        if expected_size and expected_size > max_bytes:
            counters["skipped_large"] += 1
            return None
        if remaining_total <= 0 or (expected_size and expected_size > remaining_total):
            counters["skipped_total_limit"] += 1
            return None
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, service.files().get_media(fileId=file_id), chunksize=1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
            if buffer.tell() > max_bytes:
                counters["skipped_large"] += 1
                return None
            if buffer.tell() > remaining_total:
                counters["skipped_total_limit"] += 1
                return None
        return buffer.getvalue()

    def walk(parent_drive_id, parent_local=None):
        for item in list_children(parent_drive_id):
            if item.get("mimeType") == FOLDER_MIME:
                folder, _ = Folder.objects.update_or_create(
                    source=source, external_id=item["id"],
                    defaults={"name": item.get("name", "مجلد بدون اسم"), "parent": parent_local}
                )
                counters["folders"] += 1
                walk(item["id"], folder)
                continue

            name = item.get("name", "ملف بدون اسم")
            mime = item.get("mimeType", "application/octet-stream")
            ext = Path(name).suffix.lower().lstrip(".")
            if mime == "application/pdf" or ext == "pdf": kind = "pdf"
            elif mime.startswith("image/"): kind = "image"
            elif mime.startswith("video/"): kind = "video"
            elif "spreadsheet" in mime or ext in {"xls", "xlsx", "csv", "ods"}: kind = "spreadsheet"
            elif "document" in mime or ext in {"doc", "docx", "odt", "rtf"}: kind = "document"
            else: kind = "other"
            modified_at = datetime.fromisoformat(item["modifiedTime"].replace("Z", "+00:00")) if item.get("modifiedTime") else None
            record, _ = File.objects.get_or_create(
                source=source, external_id=item["id"],
                defaults={"folder": parent_local, "name": name, "mime_type": mime, "kind": kind}
            )
            unchanged = bool(record.uploaded_file and record.modified_at and modified_at and record.modified_at == modified_at)
            record.folder = parent_local
            record.name = name
            record.mime_type = mime
            record.kind = kind
            record.web_url = item.get("webViewLink", "") or f"https://drive.google.com/file/d/{item['id']}/view"
            record.modified_at = modified_at
            record.size_bytes = int(item.get("size", 0) or record.size_bytes or 0)

            if mime.startswith(GOOGLE_NATIVE_PREFIX):
                counters["google_native_files"] += 1
            elif not unchanged:
                try:
                    data = fetch_binary(item["id"], int(item.get("size", 0) or 0))
                    if data is not None:
                        if record.uploaded_file:
                            record.uploaded_file.delete(save=False)
                        record.uploaded_file.save(name, ContentFile(data), save=False)
                        record.size_bytes = len(data)
                        record.sha256 = hashlib.sha256(data).hexdigest()
                        counters["downloaded_files"] += 1
                        counters["bytes_downloaded"] += len(data)
                except Exception:
                    counters["download_errors"] += 1
            record.save()
            counters["files"] += 1

    with transaction.atomic():
        # The linked Drive folder is a container; its immediate child folders become filières.
        walk(root_id, None)
        rebuild_academic_structure(source)
        source.drive_folder_id = root_id
        source.sync_status = "success"
        source.sync_error = ""
        source.last_synced_at = django_timezone.now()
        source.save(update_fields=["drive_folder_id", "sync_status", "sync_error", "last_synced_at"])
    return counters


def rebuild_academic_structure(source: DriveSource) -> None:
    """Map Drive folder depth to Filiere → Level → Subject → Course."""
    folders = list(Folder.objects.filter(source=source).select_related("parent").order_by("id"))
    by_id = {folder.id: folder for folder in folders}
    filieres, levels, subjects = {}, {}, {}
    for folder in folders:
        parent = by_id.get(folder.parent_id) if folder.parent_id else None
        grandparent = by_id.get(parent.parent_id) if parent and parent.parent_id else None
        greatgrandparent = by_id.get(grandparent.parent_id) if grandparent and grandparent.parent_id else None
        if parent is None:
            entry, _ = Filiere.objects.update_or_create(folder=folder, defaults={"source": source, "name": folder.name})
            filieres[folder.id] = entry
        elif parent.id in filieres:
            entry, _ = StudyLevel.objects.update_or_create(folder=folder, defaults={"filiere": filieres[parent.id], "name": folder.name})
            levels[folder.id] = entry
        elif parent.id in levels:
            entry, _ = Subject.objects.update_or_create(folder=folder, defaults={"level": levels[parent.id], "name": folder.name})
            subjects[folder.id] = entry
        elif parent.id in subjects:
            Course.objects.update_or_create(folder=folder, defaults={"subject": subjects[parent.id], "name": folder.name})
