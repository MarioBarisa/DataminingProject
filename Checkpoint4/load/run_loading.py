from pyspark.sql import DataFrame
import pymysql

JDBC_URL = "jdbc:mysql://127.0.0.1:3306/studio_data?useSSL=false"
CONNECTION_PROPERTIES = {
    "user": "root",
    "password": "12345678",
    "driver": "com.mysql.cj.jdbc.Driver"
}

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DB = "studio_data"
MYSQL_USER = "root"
MYSQL_PASSWORD = "12345678"


def reset_star_schema():
    tables = [
        "star_fact_popularnost",
        "star_dim_zanr",
        "star_dim_izvodjac",
        "star_dim_album",
        "star_dim_audio_catchy",
        "star_dim_audio_technical",
    ]

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
    )

    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS=0;")
            for t in tables:
                cur.execute(f"TRUNCATE TABLE {t};")
            cur.execute("SET FOREIGN_KEY_CHECKS=1;")
        print("Reset star sheme zavrsen (TRUNCATE).")
    finally:
        conn.close()


def write_spark_df_to_mysql(spark_df: DataFrame, table_name: str, mode: str = "append"):
    print(f"Pisanje u tablicu '{table_name}' (mod: {mode})...")
    try:
        spark_df.write.jdbc(
            url=JDBC_URL,
            table=table_name,
            mode=mode,
            properties=CONNECTION_PROPERTIES
        )
        print(f"Uspjesno zapisano: '{table_name}'")
    except Exception as e:
        print(f"Greska pri pisanju u '{table_name}': {e}")
        raise