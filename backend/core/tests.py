from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import DriveSource, File


class ApiSecurityTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="Strong-pass-2026")
        self.token = Token.objects.create(user=self.user)
        self.source = DriveSource.objects.create(name="drive_test", label="Test Drive")

    def test_api_requires_authentication(self):
        response = self.client.get("/api/sources/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_sources(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get("/api/sources/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(MAX_UPLOAD_SIZE=1024, ALLOWED_UPLOAD_EXTENSIONS=["pdf"])
    def test_upload_rejects_oversized_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        uploaded = SimpleUploadedFile("large.pdf", b"x" * 2048, content_type="application/pdf")
        response = self.client.post("/api/files/upload/", {"source": self.source.pk, "file": uploaded}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertEqual(File.objects.count(), 0)

    @override_settings(MAX_UPLOAD_SIZE=1024, ALLOWED_UPLOAD_EXTENSIONS=["pdf"])
    def test_upload_rejects_disallowed_extension(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        uploaded = SimpleUploadedFile("script.exe", b"MZ", content_type="application/octet-stream")
        response = self.client.post("/api/files/upload/", {"source": self.source.pk, "file": uploaded}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(File.objects.count(), 0)


class PublicLibraryTests(APITestCase):
    def setUp(self):
        self.source = DriveSource.objects.create(name="public_drive", label="Public Drive", is_public=True)
        self.private_source = DriveSource.objects.create(name="private_drive", label="Private Drive", is_public=False)

    def test_public_visitors_can_list_public_sources(self):
        response = self.client.get("/api/sources/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data["results"]], [self.source.id])

    def test_public_visitors_cannot_see_private_source_files(self):
        from .models import Folder
        public_folder = Folder.objects.create(source=self.source, name="Public section")
        private_folder = Folder.objects.create(source=self.private_source, name="Private section")
        response = self.client.get("/api/folders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data["results"]], [public_folder.id])

    def test_drive_import_requires_admin(self):
        response = self.client.post("/api/admin/drive-sources/", {"drive_url": "https://drive.google.com/drive/folders/abcdefghijk"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AcademicCatalogueTests(APITestCase):
    def test_drive_folder_tree_is_mapped_to_academic_catalogue(self):
        from .models import Folder, Filiere, StudyLevel, Subject, Course
        from .drive_importer import rebuild_academic_structure
        source = DriveSource.objects.create(name="faculty", label="Faculty", is_public=True)
        root = Folder.objects.create(source=source, name="Informatique")
        level = Folder.objects.create(source=source, name="L1", parent=root)
        subject = Folder.objects.create(source=source, name="Algorithmique", parent=level)
        course = Folder.objects.create(source=source, name="Cours 01", parent=subject)
        rebuild_academic_structure(source)
        self.assertEqual(Filiere.objects.get(folder=root).name, "Informatique")
        self.assertEqual(StudyLevel.objects.get(folder=level).name, "L1")
        self.assertEqual(Subject.objects.get(folder=subject).name, "Algorithmique")
        self.assertEqual(Course.objects.get(folder=course).name, "Cours 01")

    def test_public_academic_endpoint_returns_nested_sections(self):
        from .models import Folder
        from .drive_importer import rebuild_academic_structure
        source = DriveSource.objects.create(name="faculty", label="Faculty", is_public=True)
        root = Folder.objects.create(source=source, name="Informatique")
        Folder.objects.create(source=source, name="L1", parent=root)
        rebuild_academic_structure(source)
        response = self.client.get("/api/academic/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Informatique")
        self.assertEqual(response.data[0]["levels"][0]["name"], "L1")
