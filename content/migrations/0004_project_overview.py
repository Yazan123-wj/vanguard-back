from django.db import migrations, models


def split_legacy_description(apps, schema_editor):
    """Move second+ paragraphs into overview when overview is empty."""
    Project = apps.get_model("content", "Project")
    for project in Project.objects.all():
        if project.overview or not project.description:
            continue
        parts = [p.strip() for p in project.description.split("\n\n") if p.strip()]
        if len(parts) < 2:
            continue
        project.description = parts[0]
        project.overview = "\n\n".join(parts[1:])
        project.save(update_fields=["description", "overview"])


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0003_connect_admin_cms"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="overview",
            field=models.TextField(
                blank=True,
                help_text="Right column in the project detail overlay (smaller overview copy).",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Left column in the project detail overlay (larger lead copy).",
            ),
        ),
        migrations.RunPython(split_legacy_description, migrations.RunPython.noop),
    ]
