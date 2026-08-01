"""Dashboard data for the Unfold admin home screen."""

from django.urls import reverse

from .models import BlogPost, Office, Project, Service, SocialLink


def dashboard_callback(request, context):
    services = Service.objects.count()
    projects = Project.objects.count()
    blogs = BlogPost.objects.count()
    offices = Office.objects.count()
    social = SocialLink.objects.count()

    context.update(
        {
            "vg_stats": [
                {
                    "label": "Services",
                    "value": services,
                    "hint": "Shown on home + /services",
                    "icon": "design_services",
                    "href": reverse("admin:content_service_changelist"),
                    "tone": "blue",
                },
                {
                    "label": "Projects",
                    "value": projects,
                    "hint": "Spherical gallery items",
                    "icon": "work",
                    "href": reverse("admin:content_project_changelist"),
                    "tone": "indigo",
                },
                {
                    "label": "Blog posts",
                    "value": blogs,
                    "hint": "Notes & articles",
                    "icon": "article",
                    "href": reverse("admin:content_blogpost_changelist"),
                    "tone": "violet",
                },
                {
                    "label": "Footer",
                    "value": offices + social,
                    "hint": f"{offices} offices · {social} socials",
                    "icon": "location_on",
                    "href": reverse("admin:content_office_changelist"),
                    "tone": "sky",
                },
            ],
            "vg_quick_actions": [
                {
                    "title": "Add service",
                    "description": "New card for the homepage stack",
                    "icon": "add_circle",
                    "href": reverse("admin:content_service_add"),
                },
                {
                    "title": "Add project",
                    "description": "Upload images + set live link",
                    "icon": "add_photo_alternate",
                    "href": reverse("admin:content_project_add"),
                },
                {
                    "title": "Write blog post",
                    "description": "Publish a studio note",
                    "icon": "edit_note",
                    "href": reverse("admin:content_blogpost_add"),
                },
                {
                    "title": "View website",
                    "description": "Open the live Next.js site",
                    "icon": "open_in_new",
                    "href": "http://localhost:3000",
                    "external": True,
                },
            ],
            "vg_recent_projects": list(
                Project.objects.order_by("-date", "order")[:5].values(
                    "id", "title", "subtitle", "date", "slug"
                )
            ),
            "vg_recent_blogs": list(
                BlogPost.objects.order_by("-date")[:5].values(
                    "id", "title", "category", "date", "slug"
                )
            ),
        }
    )
    return context
