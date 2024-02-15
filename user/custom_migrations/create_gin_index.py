from django.core.management.base import BaseCommand
from user.models import User
from django.db import connection


class Command(BaseCommand):
    help = 'Create a GIN index on a specific field'

    def add_arguments(self, parser):
        parser.add_argument('field_name', type=str, help='Name of the field to index')

    def handle(self, *args, **kwargs):
        field_name = kwargs['field_name']

        # Check if the field exists in the model
        if not hasattr(User, field_name):
            self.stdout.write(self.style.ERROR(f"Field '{field_name}' does not exist in the model."))
            return

        # Check if the database is PostgreSQL
        if connection.vendor != 'postgresql':
            self.stdout.write(self.style.ERROR("This command is only supported on PostgreSQL databases."))
            return

        # Create the GIN index
        self.stdout.write(self.style.SUCCESS(f"Creating GIN index on field '{field_name}'..."))
        with connection.schema_editor() as schema_editor:
            schema_editor.execute(
                f'CREATE INDEX {field_name}_gin_idx ON {User._meta.db_table} USING GIN ({field_name})'
            )
        self.stdout.write(self.style.SUCCESS(f"GIN index on field '{field_name}' created successfully."))
