from datetime import datetime
from app.database import create_db_connection


def seed_initial_data():
    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM products")
    product_count = cursor.fetchone()["count"]

    if product_count == 0:
        cursor.executemany(
            """
            INSERT INTO products (product_id, name, price, stock)
            VALUES (%s, %s, %s, %s)
            """,
            [
                ("prod_101", "Wireless Headphones", 199.99, 50),
                ("prod_102", "Mechanical Keyboard", 149.50, 5),
                ("prod_103", "Gaming Mouse", 89.00, 0),
            ],
        )

    cursor.execute("SELECT COUNT(*) AS count FROM deployment_config")
    config_count = cursor.fetchone()["count"]

    if config_count == 0:
        cursor.executemany(
            """
            INSERT INTO deployment_config (key, value)
            VALUES (%s, %s)
            """,
            [
                ("environment", "production"),
                ("payment_mode", "live"),
                ("api_version", "1.0.0"),
                ("client_id", "client-A"),
                ("discount_enabled", "true"),
            ],
        )

    cursor.execute("SELECT COUNT(*) AS count FROM migrations WHERE version = %s", ("1",))
    migration_count = cursor.fetchone()["count"]

    if migration_count == 0:
        cursor.execute(
            """
            INSERT INTO migrations (version, applied_at)
            VALUES (%s, %s)
            """,
            ("1", datetime.now().isoformat()),
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Initial data seeded")