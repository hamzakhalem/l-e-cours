from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import DriveSource, Folder, File, StudyYear, Filiere, Speciality, Subject, ResourceCategory

class Command(BaseCommand):
    help = "Create a five-level academic demo catalogue for local development."

    def handle(self, *args, **options):
        if DriveSource.objects.exists():
            self.stdout.write(self.style.WARNING("Demo data already exists; no changes made."))
            return
        source = DriveSource.objects.create(name="demo_university", label="جامعة تجريبية", color="#4285F4")
        year_folder = Folder.objects.create(source=source, name="Licence 3")
        year = StudyYear.objects.create(source=source, folder=year_folder, name=year_folder.name)
        filiere_folder = Folder.objects.create(source=source, parent=year_folder, name="Informatique")
        filiere = Filiere.objects.create(study_year=year, folder=filiere_folder, name=filiere_folder.name)
        speciality_folder = Folder.objects.create(source=source, parent=filiere_folder, name="Intelligence Artificielle")
        speciality = Speciality.objects.create(filiere=filiere, folder=speciality_folder, name=speciality_folder.name)
        subject_folder = Folder.objects.create(source=source, parent=speciality_folder, name="Machine Learning")
        subject = Subject.objects.create(speciality=speciality, folder=subject_folder, name=subject_folder.name)
        for index, (code, label) in enumerate([("course", "Cours"), ("td", "TD"), ("exam", "Examens"), ("other", "Autres")]):
            category_folder = Folder.objects.create(source=source, parent=subject_folder, name=label)
            category = ResourceCategory.objects.create(subject=subject, folder=category_folder, name=label, code=code, sort_order=index)
            if code == "course":
                File.objects.create(source=source, folder=category_folder, resource_category=category,
                                    name="Introduction.pdf", kind="pdf", mime_type="application/pdf", size_bytes=0)
        self.stdout.write(self.style.SUCCESS("Created a demo five-level academic hierarchy with four resource categories."))
