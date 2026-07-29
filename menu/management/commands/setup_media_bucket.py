from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from Food_Fanatic.storage import SupabaseStorage


def bucket_id(bucket):
    if isinstance(bucket, dict):
        return bucket.get("id")
    return getattr(bucket, "id", None)


class Command(BaseCommand):
    help = "Create the public Supabase bucket used for restaurant menu media."

    def handle(self, *args, **options):
        if not getattr(settings, "SUPABASE_STORAGE_ENABLED", False):
            self.stdout.write("Supabase media storage is not configured; skipped.")
            return

        storage = SupabaseStorage(
            url=settings.SUPABASE_URL,
            key=settings.SUPABASE_SERVICE_ROLE_KEY,
            bucket_name=settings.SUPABASE_STORAGE_BUCKET,
        )
        bucket_names = {
            bucket_id(bucket)
            for bucket in storage.client.storage.list_buckets()
        }
        if storage.bucket_name in bucket_names:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Supabase media bucket '{storage.bucket_name}' is ready."
                )
            )
            return

        try:
            storage.client.storage.create_bucket(
                storage.bucket_name,
                options={
                    "public": True,
                    "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
                },
            )
        except Exception as error:
            # A parallel deploy may create the same bucket between list and create.
            refreshed_names = {
                bucket_id(bucket)
                for bucket in storage.client.storage.list_buckets()
            }
            if storage.bucket_name not in refreshed_names:
                raise CommandError(
                    f"Could not create Supabase media bucket: {error}"
                ) from error

        self.stdout.write(
            self.style.SUCCESS(
                f"Supabase media bucket '{storage.bucket_name}' is ready."
            )
        )
