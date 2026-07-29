from django.test import SimpleTestCase

from .database import build_database_config


class DatabaseConfigTests(SimpleTestCase):
    def test_supabase_metadata_is_not_passed_to_psycopg(self):
        config = build_database_config(
            "postgresql://user:password@aws-0-us-east-1.pooler.supabase.com:"
            "6543/postgres?sslmode=require&supa=base-pooler.x"
        )

        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertNotIn("supa", config["OPTIONS"])
        self.assertIsNone(config["OPTIONS"]["prepare_threshold"])
        self.assertTrue(config["DISABLE_SERVER_SIDE_CURSORS"])

    def test_standard_postgres_options_are_preserved(self):
        config = build_database_config(
            "postgresql://user:password@database.example.com:"
            "5432/foodfanatic?sslmode=require"
        )

        self.assertEqual(config["OPTIONS"], {"sslmode": "require"})
        self.assertNotIn("DISABLE_SERVER_SIDE_CURSORS", config)
