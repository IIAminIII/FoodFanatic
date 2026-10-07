"""Database configuration helpers."""

import environ


def build_database_config(database_url):
    """Convert a provider URL into Django settings safe for psycopg."""
    config = environ.Env.db_url_config(database_url)
    options = config.setdefault("OPTIONS", {})

    # Vercel's Supabase integration appends routing metadata that is not a
    # PostgreSQL connection option and would otherwise be passed to psycopg.
    options.pop("supa", None)

    # Transaction poolers (Supabase on port 6543, Neon's "-pooler" hosts)
    # cannot retain session-scoped cursors or prepared statements between
    # transactions.
    is_transaction_pooler = str(config.get("PORT", "")) == "6543" or "-pooler." in str(
        config.get("HOST", "")
    )
    if is_transaction_pooler:
        options.setdefault("prepare_threshold", None)
        config["DISABLE_SERVER_SIDE_CURSORS"] = True

    if not options:
        config.pop("OPTIONS")

    return config


def resolve_database_url(runtime_environment, file_environment):
    """Prefer deployment-injected database URLs over local .env defaults."""
    return (
        runtime_environment.get("DATABASE_URL")
        or runtime_environment.get("POSTGRES_URL")
        or file_environment("DATABASE_URL", default="")
        or file_environment("POSTGRES_URL", default="")
    )
