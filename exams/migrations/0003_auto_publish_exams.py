# Generated migration file - Auto publish existing exams

from django.db import migrations

def publish_exams(apps, schema_editor):
    """Publish all existing unpublished exams"""
    Exam = apps.get_model('exams', 'Exam')
    updated = Exam.objects.filter(is_published=False).update(is_published=True)
    print(f"Published {updated} exams")

def unpublish_exams(apps, schema_editor):
    """Reverse: unpublish exams (for rollback if needed)"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_exam_deletion_notified_exam_deletion_scheduled_at'),
    ]

    operations = [
        migrations.RunPython(publish_exams, unpublish_exams),
    ]
