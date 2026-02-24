from django.conf import settings
from django.db import migrations, models


def backfill_owner(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    BlogPost = apps.get_model('blog', 'BlogPost')
    GenerationJob = apps.get_model('blog', 'GenerationJob')

    fallback_email = 'legacy-owner@example.local'
    fallback_user, created = User.objects.get_or_create(
        username=fallback_email,
        defaults={
            'email': fallback_email,
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
        }
    )
    if created:
        fallback_user.password = '!'
        fallback_user.save(update_fields=['password'])

    BlogPost.objects.filter(owner__isnull=True).update(owner=fallback_user)
    GenerationJob.objects.filter(owner__isnull=True).update(owner=fallback_user)


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_generationjob_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='owned_blog_posts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='generationjob',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='owned_generation_jobs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_owner, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='blogpost',
            name='owner',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='owned_blog_posts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='generationjob',
            name='owner',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='owned_generation_jobs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
