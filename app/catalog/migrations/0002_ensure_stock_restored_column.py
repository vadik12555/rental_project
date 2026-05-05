from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE catalog_order
                    ADD COLUMN IF NOT EXISTS stock_restored boolean NOT NULL DEFAULT false;
                    """,
                    reverse_sql="""
                    ALTER TABLE catalog_order
                    DROP COLUMN IF EXISTS stock_restored;
                    """,
                )
            ],
            state_operations=[],
        )
    ]

