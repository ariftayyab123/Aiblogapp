"""
Management command to load initial personas into the database.
Run: python manage.py loadpersonas
"""
from django.core.management.base import BaseCommand
from ai_blog.apps.blog.models import Persona


class Command(BaseCommand):
    help = 'Load default personas into the database'

    PERSONAS = [
        {
            'name': 'Technical Writer',
            'slug': 'technical',
            'persona_type': 'technical',
            'description': 'Precise, jargon-appropriate, citation-heavy writing',
            'system_prompt': '',
            'temperature': 0.7,
            'max_tokens': 4000,
            'display_order': 1,
        },
        {
            'name': 'Storyteller',
            'slug': 'narrative',
            'persona_type': 'narrative',
            'description': 'Narrative-driven, emotional hooks, memorable content',
            'system_prompt': '',
            'temperature': 0.8,
            'max_tokens': 4000,
            'display_order': 2,
        },
        {
            'name': 'Industry Analyst',
            'slug': 'analyst',
            'persona_type': 'analyst',
            'description': 'Data-focused, trend-aware, forward-looking insights',
            'system_prompt': '',
            'temperature': 0.6,
            'max_tokens': 4000,
            'display_order': 3,
        },
        {
            'name': 'Educator',
            'slug': 'educator',
            'persona_type': 'educator',
            'description': 'Explanatory, structured, beginner-friendly approach',
            'system_prompt': '',
            'temperature': 0.7,
            'max_tokens': 4000,
            'display_order': 4,
        },
    ]

    def handle(self, *args, **options):
        """Execute the command"""
        created_count = 0
        updated_count = 0

        for persona_data in self.PERSONAS:
            slug = persona_data['slug']
            persona, created = Persona.objects.get_or_create(
                slug=slug,
                defaults=persona_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created persona: {persona.name}')
                )
            else:
                # Update existing persona
                for key, value in persona_data.items():
                    setattr(persona, key, value)
                persona.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated persona: {persona.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nComplete: {created_count} created, {updated_count} updated'
            )
        )
