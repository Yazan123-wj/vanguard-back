from django.db import models
from django.utils.text import slugify


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


def _split_commas(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


class Service(models.Model):
    """A service — feeds the homepage stack, /services grid, and detail page."""

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    order = models.PositiveIntegerField(
        default=0, help_text="Display order. The first 4 show on the homepage."
    )
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField("Service name", max_length=120)
    description = models.TextField(
        help_text="Short card text shown on the stack card and services grid."
    )
    summary = models.TextField(
        blank=True,
        help_text="Longer intro on the service page. Falls back to the description if empty.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED,
        db_index=True,
    )
    what_we_define_heading = models.CharField(
        "First section heading",
        max_length=80,
        default="What we define",
        help_text="e.g. What we define / What we design / What we build.",
    )
    what_we_define = models.TextField(
        "What we define", blank=True, help_text="First section on the service page."
    )
    how_we_work = models.TextField(
        "How we work", blank=True, help_text="Second section on the service page."
    )
    leave_with = models.TextField(
        "What you leave with",
        blank=True,
        help_text="Outcomes list — one item per line.",
    )
    tags = models.CharField(
        max_length=250,
        blank=True,
        help_text="Comma-separated chips, e.g. Research, Positioning, Naming",
    )
    # Round-trip structured blocks for the Next.js admin editor.
    blocks = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def tag_list(self) -> list[str]:
        return _split_commas(self.tags)

    @property
    def leave_with_list(self) -> list[str]:
        return _split_lines(self.leave_with)


class Project(models.Model):
    """A project in the spherical gallery + its detail overlay."""

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    order = models.PositiveIntegerField(default=0, help_text="Display order in the gallery.")
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=120, help_text="Client / big name, e.g. NETFLIX")
    subtitle = models.CharField(
        max_length=200, help_text="Project name, e.g. STRANGER THINGS EXPERIENCE"
    )
    description = models.TextField(
        blank=True,
        help_text="Right column in the project detail overlay (supporting copy).",
    )
    overview = models.TextField(
        blank=True,
        help_text="Left column in the project detail overlay (larger lead copy).",
    )
    date = models.DateField(help_text="Project date — the year shows in the gallery.")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED,
        db_index=True,
    )
    featured = models.BooleanField(default=False)
    cover_url = models.URLField(
        blank=True,
        help_text="External cover image URL (used when no uploaded images).",
    )
    external_url = models.URLField(
        "Visit full site link",
        blank=True,
        help_text="External URL for the “Visit live site” button. Leave empty to hide it.",
    )
    services = models.ManyToManyField(
        Service,
        blank=True,
        related_name="projects",
        help_text="Tags — pick from your services.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-date", "id"]

    def __str__(self) -> str:
        return f"{self.title} — {self.subtitle}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.subtitle}")[:50]
        super().save(*args, **kwargs)

    @property
    def year(self) -> str:
        return str(self.date.year)


class ProjectImage(models.Model):
    """Uploaded image for a project. The first image is the gallery card."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="projects/")
    order = models.PositiveIntegerField(
        default=0, help_text="0 = cover (gallery card + first detail image)."
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.project} — image {self.order}"


class BlogPost(models.Model):
    """A studio note — home Notes section, /blogs grid, article page."""

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200)
    subtitle = models.TextField(
        help_text="Short summary shown on cards and as the article lead."
    )
    description = models.TextField(
        help_text="Article body. Separate paragraphs with a blank line."
    )
    date = models.DateField()
    category = models.CharField(
        max_length=80, blank=True, default="Studio",
        help_text="Label above the card, e.g. Brand Strategy.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED,
        db_index=True,
        help_text="Only published posts appear on the public website.",
    )
    image = models.ImageField(
        upload_to="blogs/", blank=True, help_text="Cover image (upload)."
    )
    image_url = models.URLField(
        blank=True,
        help_text="Or an external cover image URL (used when no upload).",
    )
    read_time = models.CharField(max_length=40, blank=True, default="5 min read")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Most recently published/updated first (drives /blogs hero featured).
        ordering = ["-updated_at", "-date", "-id"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)

    @property
    def body_paragraphs(self) -> list[str]:
        paragraphs = [
            p.strip().replace("\n", " ")
            for p in (self.description or "").split("\n\n")
        ]
        return [p for p in paragraphs if p]


class Office(models.Model):
    """Footer office entry."""

    order = models.PositiveIntegerField(default=0)
    city = models.CharField(max_length=80)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Footer office"

    def __str__(self) -> str:
        return self.city


class SocialLink(models.Model):
    """Footer social link."""

    order = models.PositiveIntegerField(default=0)
    label = models.CharField(max_length=80)
    url = models.URLField()
    enabled = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Footer social link"

    def __str__(self) -> str:
        return self.label


class MediaAsset(models.Model):
    """Uploaded / linked media for the admin library."""

    name = models.CharField(max_length=200)
    file = models.ImageField(upload_to="media-library/", blank=True)
    url = models.URLField(blank=True, help_text="External URL when not uploading a file.")
    alt = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "id"]

    def __str__(self) -> str:
        return self.name

    @property
    def resolved_url(self) -> str:
        if self.file:
            return self.file.url
        return self.url or ""


class FooterSettings(models.Model):
    """Singleton for the remaining footer bits."""

    contact_email = models.EmailField(default="hello@vanguard.studio")

    class Meta:
        verbose_name = "Footer settings"
        verbose_name_plural = "Footer settings"

    def __str__(self) -> str:
        return "Footer settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "FooterSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
