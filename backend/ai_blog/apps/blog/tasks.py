from celery import shared_task

from .models import GenerationJob
from .services.generation import BlogGenerationService


@shared_task(bind=True, name='blog.generate_post_job')
def generate_post_job(self, job_id: int):
    try:
        job = GenerationJob.objects.get(id=job_id)
    except GenerationJob.DoesNotExist:
        return

    job.status = GenerationJob.JobStatus.RUNNING
    job.progress = 10
    job.task_id = self.request.id or ''
    job.error_message = ''
    job.save(update_fields=['status', 'progress', 'task_id', 'error_message', 'updated_at'])

    try:
        service = BlogGenerationService()
        result = service.generate_post(
            topic=job.topic,
            persona_slug=job.persona_slug,
            additional_context=job.additional_context or {},
            speed=job.speed or 'fast',
        )

        job.progress = 100
        job.status = GenerationJob.JobStatus.COMPLETED
        blog_post_id = result.get('blog_post_id')
        if blog_post_id:
            job.blog_post_id = blog_post_id
        job.save(update_fields=['progress', 'status', 'blog_post', 'updated_at'])
    except Exception as exc:
        job.status = GenerationJob.JobStatus.FAILED
        job.progress = 100
        job.error_message = str(exc)
        job.save(update_fields=['status', 'progress', 'error_message', 'updated_at'])
        raise

