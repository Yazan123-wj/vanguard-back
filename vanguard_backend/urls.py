from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from content import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Public
    path("api/services/", views.services_list),
    path("api/projects/", views.projects_list),
    path("api/blogs/", views.blogs_list),
    path("api/footer/", views.footer_detail),
    # Admin CMS
    path("api/admin/dashboard/", views.admin_dashboard),
    path("api/admin/blogs/", views.admin_blogs),
    path("api/admin/blogs/<slug:slug>/", views.admin_blog_detail),
    path("api/admin/services/", views.admin_services),
    path("api/admin/services/<slug:slug>/", views.admin_service_detail),
    path("api/admin/projects/", views.admin_projects),
    path("api/admin/projects/<slug:slug>/", views.admin_project_detail),
    path("api/admin/projects/<slug:slug>/images/", views.admin_project_images),
    path(
        "api/admin/projects/<slug:slug>/images/<int:pk>/",
        views.admin_project_image_detail,
    ),
    path("api/admin/footer/", views.admin_footer),
    path("api/admin/media/", views.admin_media),
    path("api/admin/media/<int:pk>/", views.admin_media_detail),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
