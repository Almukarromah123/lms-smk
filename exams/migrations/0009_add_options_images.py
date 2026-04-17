# Generated migration for adding options_images field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0003_auto_publish_exams'),
    ]

    operations = [
        migrations.AddField(
            model_name='examquestion',
            name='options_images',
            field=models.JSONField(blank=True, null=True, default=dict),
        ),
    ]

