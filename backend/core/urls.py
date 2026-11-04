from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .views import SourceViewSet, FolderViewSet, FileViewSet, StudyYearViewSet, FiliereViewSet, SpecialityViewSet, SubjectViewSet, ResourceCategoryViewSet, dashboard, search, add_drive_source, sync_drive, academic_structure

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "تم تسجيل الخروج."}, status=status.HTTP_200_OK)


class ThrottledTokenAuthView(ObtainAuthToken):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]


router = DefaultRouter()
router.register("sources", SourceViewSet, basename="source")
router.register("folders", FolderViewSet, basename="folder")
router.register("files", FileViewSet, basename="file")
router.register("admin/study-years", StudyYearViewSet, basename="admin-study-year")
router.register("admin/filieres", FiliereViewSet, basename="admin-filiere")
router.register("admin/specialities", SpecialityViewSet, basename="admin-speciality")
router.register("admin/subjects", SubjectViewSet, basename="admin-subject")
router.register("admin/resource-categories", ResourceCategoryViewSet, basename="admin-resource-category")

urlpatterns = [
    path("auth/token/", ThrottledTokenAuthView.as_view(), name="api-token-auth"),
    path("auth/logout/", LogoutView.as_view(), name="api-token-logout"),
    path("", include(router.urls)),
    path("dashboard/", dashboard),
    path("admin/drive-sources/", add_drive_source),
    path("admin/drive-sources/<int:source_id>/sync/", sync_drive),
    path("search/", search),
    path("academic/", academic_structure),
]
