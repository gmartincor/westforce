from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS django_cache_table (
                cache_key VARCHAR(255) NOT NULL PRIMARY KEY,
                value TEXT NOT NULL,
                expires TIMESTAMP WITH TIME ZONE NOT NULL
            );
            CREATE INDEX IF NOT EXISTS django_cache_table_expires 
            ON django_cache_table (expires);
            """,
            reverse_sql="DROP TABLE IF EXISTS django_cache_table;",
        ),
    ]
