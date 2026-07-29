# Production database and catalog

Production data belongs in a persistent database, not in the Git repository.
FoodFanatic supports PostgreSQL through the `DATABASE_URL` environment variable.

## First deployment

1. Provision a managed PostgreSQL database with automated backups.
2. Set the production environment variables:

   ```text
   DEBUG=False
   SECRET_KEY=<long-random-secret>
   ALLOWED_HOSTS=restaurant.example.com
   CSRF_TRUSTED_ORIGINS=https://restaurant.example.com
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
   MEDIA_ROOT=/path/to/persistent/media
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   ```

3. Install dependencies and build static assets:

   ```shell
   python -m pip install -r requirements.txt
   python manage.py collectstatic --noinput
   ```

4. Create/update the schema:

   ```shell
   python manage.py migrate
   ```

5. Import the non-sensitive starter catalog:

   ```shell
   python manage.py seed_menu
   ```

   The command is idempotent: rerunning it creates only missing records. Use
   `--update-existing` only when the packaged catalog should overwrite matching
   descriptions, prices, categories, availability, and discount configuration.
   Starter images are copied into the configured media storage.

6. Create the first operator account:

   ```shell
   python manage.py createsuperuser
   ```

## Later deployments

Run `python manage.py migrate` during every deployment. Migrations modify the
schema while the managed PostgreSQL service retains customers, orders, reviews,
and restaurant configuration.

Do not run `flush`, delete the database, or run `seed_menu --update-existing`
automatically during deployments.

## Media persistence

The database stores image paths, while the image files live in media storage.
`MEDIA_ROOT` must point to a persistent disk or a storage service mounted by the
deployment platform. An ephemeral application filesystem will lose uploaded
images when the service restarts.

## Backups and local development

- Enable daily PostgreSQL backups and test restores periodically.
- Keep `.env`, SQLite databases, production dumps, and media uploads out of Git.
- Local development continues to use the git-ignored `db.sqlite3`.
- To restore the packaged starter catalog locally, run `python manage.py seed_menu`.
