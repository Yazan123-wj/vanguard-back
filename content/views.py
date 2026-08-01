from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import (
    BlogPost,
    FooterSettings,
    MediaAsset,
    Office,
    Project,
    ProjectImage,
    Service,
    SocialLink,
)
from .serializers import (
    AdminBlogSerializer,
    AdminMediaSerializer,
    AdminOfficeSerializer,
    AdminProjectImageSerializer,
    AdminProjectSerializer,
    AdminServiceSerializer,
    AdminSocialSerializer,
    BlogPostSerializer,
    OfficeSerializer,
    ProjectSerializer,
    ServiceSerializer,
    SocialLinkSerializer,
)


def _admin_authorized(request) -> bool:
    expected = getattr(settings, "ADMIN_API_TOKEN", "vanguard-admin-dev")
    return request.headers.get("X-Admin-Token") == expected


def _deny():
    return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def services_list(request):
    queryset = Service.objects.filter(status=Service.STATUS_PUBLISHED)
    return Response(
        ServiceSerializer(queryset, many=True, context={"request": request}).data
    )


@api_view(["GET"])
def projects_list(request):
    queryset = Project.objects.filter(
        status=Project.STATUS_PUBLISHED
    ).prefetch_related("images", "services")
    return Response(
        ProjectSerializer(queryset, many=True, context={"request": request}).data
    )


@api_view(["GET"])
def blogs_list(request):
    # Hero featured = first item = most recently published/updated post.
    queryset = BlogPost.objects.filter(
        status=BlogPost.STATUS_PUBLISHED
    ).order_by("-updated_at", "-date", "-id")
    return Response(
        BlogPostSerializer(queryset, many=True, context={"request": request}).data
    )


@api_view(["GET"])
def footer_detail(request):
    settings_obj = FooterSettings.load()
    return Response(
        {
            "offices": OfficeSerializer(
                Office.objects.filter(enabled=True), many=True
            ).data,
            "social": SocialLinkSerializer(
                SocialLink.objects.filter(enabled=True), many=True
            ).data,
            "contactEmail": settings_obj.contact_email,
        }
    )


# ── Admin: blogs ────────────────────────────────────────────────────────────


def _save_blog_cover(blog: BlogPost, request) -> None:
    upload = request.FILES.get("image") or request.FILES.get("cover")
    if upload:
        blog.image = upload
        blog.image_url = ""
        blog.save(update_fields=["image", "image_url"])


@api_view(["GET", "POST"])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def admin_blogs(request):
    if not _admin_authorized(request):
        return _deny()
    if request.method == "GET":
        return Response(
            AdminBlogSerializer(
                BlogPost.objects.all(), many=True, context={"request": request}
            ).data
        )
    serializer = AdminBlogSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    blog = serializer.save()
    _save_blog_cover(blog, request)
    return Response(
        AdminBlogSerializer(blog, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PATCH", "PUT", "DELETE"])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def admin_blog_detail(request, slug: str):
    if not _admin_authorized(request):
        return _deny()
    blog = get_object_or_404(BlogPost, slug=slug)
    if request.method == "GET":
        return Response(
            AdminBlogSerializer(blog, context={"request": request}).data
        )
    if request.method == "DELETE":
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = AdminBlogSerializer(
        blog, data=request.data, partial=True, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    blog = serializer.save()
    _save_blog_cover(blog, request)
    return Response(AdminBlogSerializer(blog, context={"request": request}).data)


# ── Admin: services ─────────────────────────────────────────────────────────


@api_view(["GET", "POST"])
def admin_services(request):
    if not _admin_authorized(request):
        return _deny()
    if request.method == "GET":
        return Response(
            AdminServiceSerializer(Service.objects.all(), many=True).data
        )
    serializer = AdminServiceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "PUT", "DELETE"])
def admin_service_detail(request, slug: str):
    if not _admin_authorized(request):
        return _deny()
    service = get_object_or_404(Service, slug=slug)
    if request.method == "GET":
        return Response(AdminServiceSerializer(service).data)
    if request.method == "DELETE":
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = AdminServiceSerializer(service, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ── Admin: projects ─────────────────────────────────────────────────────────


@api_view(["GET", "POST"])
def admin_projects(request):
    if not _admin_authorized(request):
        return _deny()
    if request.method == "GET":
        qs = Project.objects.prefetch_related("images", "services")
        return Response(
            AdminProjectSerializer(
                qs, many=True, context={"request": request}
            ).data
        )
    serializer = AdminProjectSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "PUT", "DELETE"])
def admin_project_detail(request, slug: str):
    if not _admin_authorized(request):
        return _deny()
    project = get_object_or_404(
        Project.objects.prefetch_related("images", "services"), slug=slug
    )
    if request.method == "GET":
        return Response(
            AdminProjectSerializer(project, context={"request": request}).data
        )
    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = AdminProjectSerializer(
        project, data=request.data, partial=True, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def admin_project_images(request, slug: str):
    """Upload one or more images to a project. First image becomes cover if none exist."""
    if not _admin_authorized(request):
        return _deny()
    project = get_object_or_404(Project, slug=slug)
    files = request.FILES.getlist("images") or request.FILES.getlist("image")
    if not files:
        return Response(
            {"detail": "No image files provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    start_order = project.images.count()
    created = []
    for index, upload in enumerate(files):
        image = ProjectImage.objects.create(
            project=project,
            image=upload,
            order=start_order + index,
        )
        created.append(image)

    # Clear legacy external cover once uploads exist.
    if project.cover_url:
        project.cover_url = ""
        project.save(update_fields=["cover_url"])

    return Response(
        AdminProjectImageSerializer(
            created, many=True, context={"request": request}
        ).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["PATCH", "DELETE"])
def admin_project_image_detail(request, slug: str, pk: int):
    if not _admin_authorized(request):
        return _deny()
    project = get_object_or_404(Project, slug=slug)
    image = get_object_or_404(ProjectImage, project=project, pk=pk)

    if request.method == "DELETE":
        was_first = project.images.first() and project.images.first().id == image.id
        image.delete()
        # Re-pack orders so cover stays at 0.
        for index, row in enumerate(project.images.all()):
            if row.order != index:
                row.order = index
                row.save(update_fields=["order"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH — set as cover and/or update order
    if request.data.get("makeCover") in (True, "true", "1", 1):
        others = list(project.images.exclude(pk=image.pk).order_by("order", "id"))
        image.order = 0
        image.save(update_fields=["order"])
        for index, row in enumerate(others, start=1):
            row.order = index
            row.save(update_fields=["order"])
    elif "order" in request.data:
        try:
            image.order = int(request.data["order"])
            image.save(update_fields=["order"])
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    image.refresh_from_db()
    return Response(
        AdminProjectImageSerializer(image, context={"request": request}).data
    )


# ── Admin: footer ───────────────────────────────────────────────────────────


@api_view(["GET", "PUT", "PATCH"])
def admin_footer(request):
    if not _admin_authorized(request):
        return _deny()

    settings_obj = FooterSettings.load()

    if request.method == "GET":
        return Response(
            {
                "contactEmail": settings_obj.contact_email,
                "offices": AdminOfficeSerializer(Office.objects.all(), many=True).data,
                "social": AdminSocialSerializer(
                    SocialLink.objects.all(), many=True
                ).data,
            }
        )

    data = request.data
    if "contactEmail" in data:
        settings_obj.contact_email = data["contactEmail"]
        settings_obj.save()

    if "offices" in data and isinstance(data["offices"], list):
        keep_ids = []
        for index, row in enumerate(data["offices"]):
            office_id = row.get("id")
            defaults = {
                "order": row.get("order", index),
                "city": row.get("city", ""),
                "address": row.get("address", ""),
                "phone": row.get("phone", ""),
                "enabled": row.get("enabled", True),
            }
            if office_id:
                Office.objects.filter(id=office_id).update(**defaults)
                keep_ids.append(office_id)
            else:
                created = Office.objects.create(**defaults)
                keep_ids.append(created.id)
        Office.objects.exclude(id__in=keep_ids).delete()

    if "social" in data and isinstance(data["social"], list):
        keep_ids = []
        for index, row in enumerate(data["social"]):
            link_id = row.get("id")
            defaults = {
                "order": row.get("order", index),
                "label": row.get("label", ""),
                "url": row.get("url", ""),
                "enabled": row.get("enabled", True),
                "open_in_new_tab": row.get("openInNewTab", True),
            }
            if link_id:
                SocialLink.objects.filter(id=link_id).update(**defaults)
                keep_ids.append(link_id)
            else:
                created = SocialLink.objects.create(**defaults)
                keep_ids.append(created.id)
        SocialLink.objects.exclude(id__in=keep_ids).delete()

    return Response(
        {
            "contactEmail": settings_obj.contact_email,
            "offices": AdminOfficeSerializer(Office.objects.all(), many=True).data,
            "social": AdminSocialSerializer(SocialLink.objects.all(), many=True).data,
        }
    )


# ── Admin: media ────────────────────────────────────────────────────────────


@api_view(["GET", "POST"])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def admin_media(request):
    if not _admin_authorized(request):
        return _deny()

    if request.method == "GET":
        return Response(
            AdminMediaSerializer(
                MediaAsset.objects.all(),
                many=True,
                context={"request": request},
            ).data
        )

    name = request.data.get("name") or "Untitled"
    alt = request.data.get("alt") or ""
    url = request.data.get("url") or ""
    upload = request.FILES.get("file")

    asset = MediaAsset.objects.create(
        name=name,
        alt=alt,
        url=url if not upload else "",
        file=upload if upload else None,
    )
    return Response(
        AdminMediaSerializer(asset, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PATCH", "DELETE"])
def admin_media_detail(request, pk: int):
    if not _admin_authorized(request):
        return _deny()
    asset = get_object_or_404(MediaAsset, pk=pk)

    if request.method == "GET":
        return Response(
            AdminMediaSerializer(asset, context={"request": request}).data
        )

    if request.method == "DELETE":
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if "name" in request.data:
        asset.name = request.data["name"]
    if "alt" in request.data:
        asset.alt = request.data["alt"]
    if "url" in request.data:
        asset.url = request.data["url"]
    asset.save()
    return Response(AdminMediaSerializer(asset, context={"request": request}).data)


@api_view(["GET"])
def admin_dashboard(request):
    if not _admin_authorized(request):
        return _deny()
    return Response(
        {
            "projects": Project.objects.count(),
            "services": Service.objects.count(),
            "blogs": BlogPost.objects.count(),
            "media": MediaAsset.objects.count(),
            "published": (
                Project.objects.filter(status="published").count()
                + Service.objects.filter(status="published").count()
                + BlogPost.objects.filter(status="published").count()
            ),
            "drafts": (
                Project.objects.filter(status="draft").count()
                + Service.objects.filter(status="draft").count()
                + BlogPost.objects.filter(status="draft").count()
            ),
            "recentProjects": AdminProjectSerializer(
                Project.objects.prefetch_related("images", "services").order_by(
                    "-updated_at"
                )[:5],
                many=True,
                context={"request": request},
            ).data,
            "draftItems": [
                *[
                    {
                        "id": p.slug,
                        "title": p.title,
                        "kind": "Project",
                        "href": f"/admin/projects/{p.slug}/edit",
                        "meta": p.updated_at.date().isoformat(),
                    }
                    for p in Project.objects.filter(status="draft").order_by(
                        "-updated_at"
                    )[:5]
                ],
                *[
                    {
                        "id": b.slug,
                        "title": b.title,
                        "kind": "Blog",
                        "href": f"/admin/blogs/{b.slug}/edit",
                        "meta": b.updated_at.date().isoformat(),
                    }
                    for b in BlogPost.objects.filter(status="draft").order_by(
                        "-updated_at"
                    )[:5]
                ],
                *[
                    {
                        "id": s.slug,
                        "title": s.title,
                        "kind": "Service",
                        "href": f"/admin/services/{s.slug}/edit",
                        "meta": s.updated_at.date().isoformat(),
                    }
                    for s in Service.objects.filter(status="draft").order_by(
                        "-updated_at"
                    )[:5]
                ],
            ],
        }
    )
