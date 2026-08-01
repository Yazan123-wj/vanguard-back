from rest_framework import serializers

from .models import (
    BlogPost,
    MediaAsset,
    Office,
    Project,
    ProjectImage,
    Service,
    SocialLink,
)


class ServiceSerializer(serializers.ModelSerializer):
    """Shape matches the frontend StackCardData type."""

    id = serializers.SerializerMethodField()
    body = serializers.CharField(source="description")
    tags = serializers.ListField(source="tag_list", child=serializers.CharField())
    outcomes = serializers.ListField(
        source="leave_with_list", child=serializers.CharField()
    )
    sections = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id", "slug", "title", "body", "tags", "summary", "sections", "outcomes"]

    def get_id(self, obj: Service) -> str:
        # Display number derived from position (01, 02, …).
        ids = list(
            Service.objects.order_by("order", "id").values_list("id", flat=True)
        )
        return f"{ids.index(obj.id) + 1:02d}"

    def get_summary(self, obj: Service) -> str:
        return obj.summary or obj.description

    def get_sections(self, obj: Service) -> list[dict]:
        sections = []
        if obj.what_we_define:
            sections.append(
                {
                    "heading": obj.what_we_define_heading or "What we define",
                    "copy": obj.what_we_define,
                }
            )
        if obj.how_we_work:
            sections.append({"heading": "How we work", "copy": obj.how_we_work})
        return sections


class ProjectSerializer(serializers.ModelSerializer):
    """Shape matches the gallery's GalleryProject type."""

    id = serializers.CharField(source="slug")
    tags = serializers.SerializerMethodField()
    year = serializers.CharField(read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    externalUrl = serializers.CharField(source="external_url")

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "subtitle",
            "description",
            "overview",
            "tags",
            "date",
            "year",
            "image",
            "images",
            "externalUrl",
        ]

    def get_tags(self, obj: Project) -> list[str]:
        return [service.title.upper() for service in obj.services.all()]

    def _absolute(self, url: str) -> str:
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_image(self, obj: Project) -> str:
        first = obj.images.first()
        if first:
            return self._absolute(first.image.url)
        return obj.cover_url or ""

    def get_images(self, obj: Project) -> list[str]:
        uploaded = [self._absolute(img.image.url) for img in obj.images.all()]
        if uploaded:
            return uploaded
        return [obj.cover_url] if obj.cover_url else []


class BlogPostSerializer(serializers.ModelSerializer):
    """Shape matches the frontend NoteCardData type (public site)."""

    summary = serializers.CharField(source="subtitle")
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    readTime = serializers.CharField(source="read_time")
    body = serializers.ListField(
        source="body_paragraphs", child=serializers.CharField()
    )

    class Meta:
        model = BlogPost
        fields = [
            "slug",
            "category",
            "date",
            "title",
            "summary",
            "image",
            "readTime",
            "body",
        ]

    def get_date(self, obj: BlogPost) -> str:
        return obj.date.strftime("%B %d, %Y")

    def get_image(self, obj: BlogPost) -> str:
        if obj.image:
            request = self.context.get("request")
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return obj.image_url or ""


class AdminBlogSerializer(serializers.ModelSerializer):
    """Writable shape for the Next.js admin panel."""

    id = serializers.CharField(source="slug", read_only=True)
    body = serializers.CharField(source="description", allow_blank=True)
    image = serializers.SerializerMethodField()
    readTime = serializers.CharField(
        source="read_time", required=False, allow_blank=True
    )
    updatedAt = serializers.SerializerMethodField()
    date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "body",
            "date",
            "category",
            "status",
            "image",
            "readTime",
            "updatedAt",
        ]
        read_only_fields = ["id", "slug", "image", "updatedAt"]
        extra_kwargs = {
            "subtitle": {"required": False, "allow_blank": True},
        }

    def get_image(self, obj: BlogPost) -> str:
        if obj.image:
            request = self.context.get("request")
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return obj.image_url or ""

    def get_updatedAt(self, obj: BlogPost) -> str:
        return obj.updated_at.date().isoformat()

    def create(self, validated_data):
        if not validated_data.get("read_time"):
            validated_data["read_time"] = "5 min read"
        return super().create(validated_data)


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ["city", "address", "phone"]


class SocialLinkSerializer(serializers.ModelSerializer):
    href = serializers.URLField(source="url")

    class Meta:
        model = SocialLink
        fields = ["label", "href"]


def _items_to_text(items: list) -> str:
    chunks = []
    for item in items or []:
        title = (item or {}).get("title", "").strip()
        description = (item or {}).get("description", "").strip()
        if title and description:
            chunks.append(f"{title}\n{description}")
        elif title or description:
            chunks.append(title or description)
    return "\n\n".join(chunks)


class AdminServiceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)
    name = serializers.CharField(source="title")
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    defineItems = serializers.JSONField(required=False, write_only=True)
    workSteps = serializers.JSONField(required=False, write_only=True)
    leaveWith = serializers.JSONField(required=False, write_only=True)
    projectCount = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "summary",
            "tags",
            "status",
            "order",
            "defineItems",
            "workSteps",
            "leaveWith",
            "projectCount",
            "updatedAt",
        ]
        read_only_fields = ["id", "slug", "projectCount", "updatedAt"]

    def to_representation(self, instance):
        blocks = instance.blocks or {}
        return {
            "id": instance.slug,
            "slug": instance.slug,
            "name": instance.title,
            "description": instance.description,
            "summary": instance.summary,
            "tags": instance.tag_list,
            "status": instance.status,
            "order": instance.order,
            "defineItems": blocks.get("defineItems") or [],
            "workSteps": blocks.get("workSteps") or [],
            "leaveWith": blocks.get("leaveWith")
            or [{"title": line, "description": ""} for line in instance.leave_with_list],
            "projectCount": instance.projects.count(),
            "updatedAt": instance.updated_at.date().isoformat(),
        }

    def get_projectCount(self, obj: Service) -> int:
        return obj.projects.count()

    def get_updatedAt(self, obj: Service) -> str:
        return obj.updated_at.date().isoformat()

    def _sync_content(self, validated_data):
        define = validated_data.pop("defineItems", serializers.empty)
        work = validated_data.pop("workSteps", serializers.empty)
        leave = validated_data.pop("leaveWith", serializers.empty)
        tags = validated_data.pop("tags", serializers.empty)

        if tags is not serializers.empty:
            validated_data["tags"] = ", ".join(tags or [])

        instance = getattr(self, "instance", None)
        blocks = dict(instance.blocks) if instance and instance.blocks else {}

        if define is not serializers.empty:
            blocks["defineItems"] = define or []
            validated_data["what_we_define"] = _items_to_text(define or [])
        if work is not serializers.empty:
            blocks["workSteps"] = work or []
            validated_data["how_we_work"] = _items_to_text(work or [])
        if leave is not serializers.empty:
            blocks["leaveWith"] = leave or []
            validated_data["leave_with"] = "\n".join(
                (
                    (item.get("title") or item.get("description") or "").strip()
                    for item in (leave or [])
                    if (item.get("title") or item.get("description"))
                )
            )
        if define is not serializers.empty or work is not serializers.empty or leave is not serializers.empty:
            validated_data["blocks"] = blocks
        return validated_data

    def create(self, validated_data):
        validated_data = self._sync_content(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._sync_content(validated_data)
        return super().update(instance, validated_data)


class AdminProjectImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    isCover = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ["id", "url", "order", "isCover"]

    def get_url(self, obj: ProjectImage) -> str:
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

    def get_isCover(self, obj: ProjectImage) -> bool:
        first = obj.project.images.first()
        return bool(first and first.id == obj.id)


class AdminProjectSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)
    externalUrl = serializers.URLField(
        source="external_url", required=False, allow_blank=True
    )
    cover = serializers.SerializerMethodField()
    serviceNames = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
    )
    services = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()
    date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    class Meta:
        model = Project
        fields = [
            "id",
            "slug",
            "title",
            "subtitle",
            "description",
            "overview",
            "date",
            "status",
            "featured",
            "order",
            "externalUrl",
            "cover",
            "services",
            "serviceNames",
            "images",
            "updatedAt",
        ]
        read_only_fields = ["id", "slug", "cover", "services", "images", "updatedAt"]
        extra_kwargs = {
            "description": {"required": False, "allow_blank": True},
            "overview": {"required": False, "allow_blank": True},
            "subtitle": {"required": False, "allow_blank": True},
        }

    def get_cover(self, obj: Project) -> str:
        first = obj.images.first()
        if first:
            request = self.context.get("request")
            url = first.image.url
            return request.build_absolute_uri(url) if request else url
        return obj.cover_url or ""

    def get_images(self, obj: Project) -> list[dict]:
        return AdminProjectImageSerializer(
            obj.images.all(), many=True, context=self.context
        ).data

    def get_services(self, obj: Project) -> list[str]:
        return list(obj.services.values_list("title", flat=True))

    def get_updatedAt(self, obj: Project) -> str:
        return obj.updated_at.date().isoformat()

    def create(self, validated_data):
        service_names = validated_data.pop("serviceNames", [])
        if "services" in self.initial_data and isinstance(
            self.initial_data.get("services"), list
        ):
            service_names = self.initial_data.get("services") or service_names
        # Never persist cover_url from admin — uploads only.
        validated_data.pop("cover_url", None)
        project = Project.objects.create(**validated_data)
        self._set_services(project, service_names)
        return project

    def update(self, instance, validated_data):
        service_names = validated_data.pop("serviceNames", serializers.empty)
        if "services" in self.initial_data and isinstance(
            self.initial_data.get("services"), list
        ):
            service_names = self.initial_data.get("services")
        validated_data.pop("cover_url", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if service_names is not serializers.empty:
            self._set_services(instance, service_names)
        return instance

    def _set_services(self, project: Project, names: list):
        services = []
        for name in names or []:
            service = Service.objects.filter(title__iexact=name).first()
            if service:
                services.append(service)
        project.services.set(services)


class AdminOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ["id", "order", "city", "address", "phone", "enabled"]


class AdminSocialSerializer(serializers.ModelSerializer):
    openInNewTab = serializers.BooleanField(source="open_in_new_tab", required=False)

    class Meta:
        model = SocialLink
        fields = ["id", "order", "label", "url", "enabled", "openInNewTab"]


class AdminMediaSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    uploadedAt = serializers.SerializerMethodField()
    usedBy = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            "id",
            "name",
            "url",
            "alt",
            "size",
            "type",
            "uploadedAt",
            "usedBy",
        ]
        read_only_fields = ["id", "size", "type", "uploadedAt", "usedBy"]

    def get_url(self, obj: MediaAsset) -> str:
        url = obj.resolved_url
        if not url:
            return ""
        if url.startswith("http"):
            return url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_size(self, obj: MediaAsset) -> str:
        if obj.file and getattr(obj.file, "size", None):
            kb = max(1, round(obj.file.size / 1024))
            return f"{kb} KB"
        return "—"

    def get_type(self, obj: MediaAsset) -> str:
        if obj.file and obj.file.name:
            ext = obj.file.name.rsplit(".", 1)[-1].lower()
            return f"image/{ext}"
        return "image/url"

    def get_uploadedAt(self, obj: MediaAsset) -> str:
        return obj.created_at.date().isoformat()

    def get_usedBy(self, obj: MediaAsset) -> list[str]:
        url = self.get_url(obj)
        used = []
        if url:
            for project in Project.objects.all():
                if project.cover_url == url or project.cover_url == obj.url:
                    used.append(project.title)
            for blog in BlogPost.objects.all():
                if blog.image_url == url or blog.image_url == obj.url:
                    used.append(blog.title)
        return used
