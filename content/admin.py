from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from unfold.decorators import display

from .models import (
    BlogPost,
    FooterSettings,
    Office,
    Project,
    ProjectImage,
    Service,
    SocialLink,
)

admin.site.site_header = "Vanguard Admin"
admin.site.site_title = "Vanguard Admin"
admin.site.index_title = "Content"

# Re-register auth models so they pick up the Unfold styling.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class ContentAdmin(ModelAdmin, ImportExportModelAdmin):
    """Unfold styling + Import/Export buttons on the changelist."""

    import_form_class = ImportForm
    export_form_class = ExportForm
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True
    list_fullwidth = True


@admin.register(Service)
class ServiceAdmin(ContentAdmin):
    list_display = ("order", "title", "tags", "placement")
    list_display_links = ("title",)
    list_editable = ("order",)
    search_fields = ("title", "description", "tags")
    list_filter = ("order",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            "Basics",
            {
                "classes": ["tab"],
                "fields": ("order", "title", "slug", "tags"),
            },
        ),
        (
            "Copy",
            {
                "classes": ["tab"],
                "fields": ("description", "summary"),
            },
        ),
        (
            "Service page",
            {
                "classes": ["tab"],
                "fields": (
                    "what_we_define_heading",
                    "what_we_define",
                    "how_we_work",
                    "leave_with",
                ),
            },
        ),
    )

    @display(
        description="Shown on",
        label={"Homepage": "success", "Services page": "info"},
    )
    def placement(self, obj: Service) -> str:
        first_four = list(
            Service.objects.order_by("order", "id").values_list("id", flat=True)[:4]
        )
        return "Homepage" if obj.id in first_four else "Services page"


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("preview", "image", "order")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj: ProjectImage):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px" />',
                obj.image.url,
            )
        return "—"


@admin.register(Project)
class ProjectAdmin(ContentAdmin):
    list_display = ("order", "title", "subtitle", "date", "image_count", "link_status")
    list_display_links = ("title", "subtitle")
    list_editable = ("order",)
    date_hierarchy = "date"
    search_fields = ("title", "subtitle", "description")
    list_filter = ("date", "services")
    filter_horizontal = ("services",)
    prepopulated_fields = {"slug": ("title", "subtitle")}
    inlines = [ProjectImageInline]
    fieldsets = (
        (
            "Basics",
            {
                "classes": ["tab"],
                "fields": ("order", "title", "subtitle", "slug", "date"),
            },
        ),
        (
            "Story",
            {
                "classes": ["tab"],
                "fields": ("description", "overview", "services", "external_url"),
            },
        ),
    )

    @display(description="Images")
    def image_count(self, obj: Project) -> str:
        return str(obj.images.count())

    @display(
        description="Live site",
        label={"Linked": "success", "No link": "warning"},
    )
    def link_status(self, obj: Project) -> str:
        return "Linked" if obj.external_url else "No link"


@admin.register(BlogPost)
class BlogPostAdmin(ContentAdmin):
    list_display = ("title", "category_label", "status", "date", "read_time")
    date_hierarchy = "date"
    search_fields = ("title", "subtitle", "description", "category")
    list_filter = ("status", "category", "date")
    list_editable = ("status",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            "Basics",
            {
                "classes": ["tab"],
                "fields": ("title", "slug", "date", "category", "status", "read_time"),
            },
        ),
        (
            "Article",
            {
                "classes": ["tab"],
                "fields": ("subtitle", "description"),
            },
        ),
        (
            "Cover",
            {
                "classes": ["tab"],
                "fields": ("image", "image_url"),
            },
        ),
    )

    @display(description="Category", label="info")
    def category_label(self, obj: BlogPost) -> str:
        return obj.category or "—"


@admin.register(Office)
class OfficeAdmin(ContentAdmin):
    list_display = ("order", "city", "address", "phone")
    list_display_links = ("city",)
    list_editable = ("order",)


@admin.register(SocialLink)
class SocialLinkAdmin(ContentAdmin):
    list_display = ("order", "label", "url")
    list_display_links = ("label",)
    list_editable = ("order",)


@admin.register(FooterSettings)
class FooterSettingsAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
