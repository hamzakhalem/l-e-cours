from django.core.management.base import BaseCommand
from core.models import DriveSource, Folder, File
from core.drive_importer import rebuild_academic_structure

class Command(BaseCommand):
    help = "Create safe sample data for local development."

    def handle(self, *args, **options):
        if DriveSource.objects.exists():
            self.stdout.write(self.style.WARNING("Demo data already exists; no changes made."))
            return
        sources = [
            DriveSource.objects.create(name="drive_one", label="Google Drive 1", color="#4285F4"),
            DriveSource.objects.create(name="drive_two", label="Google Drive 2", color="#0F9D58"),
            DriveSource.objects.create(name="drive_three", label="Google Drive 3", color="#F4B400"),
        ]
        samples = [
            ("Projects", [("Brief.pdf", "pdf", "application/pdf", 245000),
                          ("Roadmap.xlsx", "spreadsheet", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 82000)]),
            ("Resources", [("Guide.docx", "document", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 125000),
                           ("Diagram.png", "image", "image/png", 98000)]),
            ("Archive", [("Intro.mp4", "video", "video/mp4", 4200000),
                         ("Notes.txt", "other", "text/plain", 12000)]),
        ]
        for source, (folder_name, entries) in zip(sources, samples):
            folder = Folder.objects.create(source=source, name=folder_name)
            for name, kind, mime, size in entries:
                File.objects.create(source=source, folder=folder, name=name, kind=kind, mime_type=mime, size_bytes=size)
        rebuild_academic_structure_for_sources(sources)
        self.stdout.write(self.style.SUCCESS("Created 3 sources, 3 folders and 6 demo file records, with academic catalogue entries."))


def rebuild_academic_structure_for_sources(sources):
    # Demo root folders become filières. Real Drive imports populate deeper levels automatically.
    from core.models import Filiere
    for source in sources:
        for folder in Folder.objects.filter(source=source, parent__isnull=True):
            Filiere.objects.update_or_create(folder=folder, defaults={"source": source, "name": folder.name})
