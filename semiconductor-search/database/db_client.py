"""
PostgreSQL database client using psycopg2.
Replaces Oracle client with Replit's built-in PostgreSQL + pgvector extension.
"""

import psycopg2
import psycopg2.extras
from config.settings import DATABASE_URL


def get_connection():
    """Return a new database connection."""
    return psycopg2.connect(DATABASE_URL)


def initialize_schema():
    """
    Create the products table if it does not already exist.
    Uses pgvector's VECTOR type for storing embedding vectors.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Enable pgvector extension (idempotent)
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id              SERIAL PRIMARY KEY,
                    product_name    VARCHAR(255) NOT NULL UNIQUE,
                    category        VARCHAR(100),

                    -- Microcontroller fields
                    architecture    VARCHAR(100),
                    flash_kb        FLOAT,
                    ram_kb          FLOAT,
                    gpio_pins       INTEGER,
                    voltage_min     FLOAT,
                    voltage_max     FLOAT,
                    interfaces      TEXT,

                    -- Sensor fields
                    sensor_type     VARCHAR(100),
                    measurement_range VARCHAR(200),
                    accuracy        VARCHAR(100),

                    -- Power IC fields
                    topology        VARCHAR(100),
                    output_voltage  VARCHAR(100),
                    output_current_a FLOAT,
                    switching_frequency_khz FLOAT,
                    efficiency      VARCHAR(50),

                    -- Memory fields
                    memory_type     VARCHAR(100),
                    capacity_mb     FLOAT,
                    speed           VARCHAR(100),

                    -- Shared / generic fields
                    max_speed_mhz   FLOAT,
                    package_type    VARCHAR(100),
                    temp_range      VARCHAR(100),
                    interface       VARCHAR(200),
                    output_type     VARCHAR(100),

                    -- Natural language feature text used for embedding
                    features_text   TEXT,

                    -- Embedding vector (1536 dims for text-embedding-3-small)
                    embedding_vector VECTOR(1536),

                    created_at      TIMESTAMP DEFAULT NOW(),
                    updated_at      TIMESTAMP DEFAULT NOW()
                );
            """)

            # Index for fast vector similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS products_embedding_idx
                ON products
                USING ivfflat (embedding_vector vector_cosine_ops)
                WITH (lists = 10);
            """)

        conn.commit()
        print("Schema initialized successfully.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def upsert_product(product: dict) -> int:
    """
    Insert a new product or update an existing one by product_name.
    Returns the product id.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO products (
                    product_name, category, architecture, flash_kb, ram_kb,
                    gpio_pins, voltage_min, voltage_max, interfaces,
                    sensor_type, measurement_range, accuracy,
                    topology, output_voltage, output_current_a,
                    switching_frequency_khz, efficiency,
                    memory_type, capacity_mb, speed,
                    max_speed_mhz, package_type, temp_range,
                    interface, output_type, features_text
                ) VALUES (
                    %(product_name)s, %(category)s, %(architecture)s,
                    %(flash_kb)s, %(ram_kb)s, %(gpio_pins)s,
                    %(voltage_min)s, %(voltage_max)s, %(interfaces)s,
                    %(sensor_type)s, %(measurement_range)s, %(accuracy)s,
                    %(topology)s, %(output_voltage)s, %(output_current_a)s,
                    %(switching_frequency_khz)s, %(efficiency)s,
                    %(memory_type)s, %(capacity_mb)s, %(speed)s,
                    %(max_speed_mhz)s, %(package_type)s, %(temp_range)s,
                    %(interface)s, %(output_type)s, %(features_text)s
                )
                ON CONFLICT (product_name) DO UPDATE SET
                    category = EXCLUDED.category,
                    architecture = EXCLUDED.architecture,
                    flash_kb = EXCLUDED.flash_kb,
                    ram_kb = EXCLUDED.ram_kb,
                    gpio_pins = EXCLUDED.gpio_pins,
                    voltage_min = EXCLUDED.voltage_min,
                    voltage_max = EXCLUDED.voltage_max,
                    interfaces = EXCLUDED.interfaces,
                    sensor_type = EXCLUDED.sensor_type,
                    measurement_range = EXCLUDED.measurement_range,
                    accuracy = EXCLUDED.accuracy,
                    topology = EXCLUDED.topology,
                    output_voltage = EXCLUDED.output_voltage,
                    output_current_a = EXCLUDED.output_current_a,
                    switching_frequency_khz = EXCLUDED.switching_frequency_khz,
                    efficiency = EXCLUDED.efficiency,
                    memory_type = EXCLUDED.memory_type,
                    capacity_mb = EXCLUDED.capacity_mb,
                    speed = EXCLUDED.speed,
                    max_speed_mhz = EXCLUDED.max_speed_mhz,
                    package_type = EXCLUDED.package_type,
                    temp_range = EXCLUDED.temp_range,
                    interface = EXCLUDED.interface,
                    output_type = EXCLUDED.output_type,
                    features_text = EXCLUDED.features_text,
                    updated_at = NOW()
                RETURNING id;
            """, {**_default_product_fields(), **product})
            product_id = cur.fetchone()[0]
        conn.commit()
        return product_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_product_embedding(product_name: str, embedding: list):
    """Store the embedding vector for a product."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE products SET embedding_vector = %s WHERE product_name = %s;",
                (embedding, product_name)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_product_by_name(product_name: str) -> dict | None:
    """Fetch a single product row by exact product name."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM products WHERE product_name = %s;",
                (product_name,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_products_without_embeddings() -> list[dict]:
    """Return all products that do not yet have an embedding vector."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT product_name, features_text FROM products WHERE embedding_vector IS NULL;"
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_all_products() -> list[dict]:
    """Return all products (without the embedding vector blob)."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, product_name, category, architecture, flash_kb, ram_kb,
                       gpio_pins, voltage_min, voltage_max, interfaces,
                       sensor_type, measurement_range, accuracy,
                       topology, output_voltage, output_current_a,
                       switching_frequency_khz, efficiency,
                       memory_type, capacity_mb, speed,
                       max_speed_mhz, package_type, temp_range,
                       interface, output_type, features_text, created_at, updated_at
                FROM products
                ORDER BY id;
            """)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def _default_product_fields() -> dict:
    """Return a dict of all product columns set to None for safe merging."""
    return {
        "product_name": None, "category": None, "architecture": None,
        "flash_kb": None, "ram_kb": None, "gpio_pins": None,
        "voltage_min": None, "voltage_max": None, "interfaces": None,
        "sensor_type": None, "measurement_range": None, "accuracy": None,
        "topology": None, "output_voltage": None, "output_current_a": None,
        "switching_frequency_khz": None, "efficiency": None,
        "memory_type": None, "capacity_mb": None, "speed": None,
        "max_speed_mhz": None, "package_type": None, "temp_range": None,
        "interface": None, "output_type": None, "features_text": None,
    }
