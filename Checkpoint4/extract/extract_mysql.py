from spar_session import get_spark_session;

JDBC_URL = "jdbc:mysql://127.0.0.1:3306/studio_data?useSSL=false"
CONNECTION_PROPERTIES = {
    "user": "root",
    "password": "12345678",
    "driver": "com.mysql.cj.jdbc.Driver"
}

def extract_table(table_name):
    spark = get_spark_session("ETL_Studio")
    df = spark.read.jdbc(
        url=JDBC_URL,
        table=table_name,
        properties=CONNECTION_PROPERTIES
    )
    return df

def extract_all_tables():
    return {
        "zanr":            extract_table("zanr"),
        "izvodjac":        extract_table("izvodjac"),
        "album":           extract_table("album"),
        "pjesma":          extract_table("pjesma"),
        "izvodjac_pjesma": extract_table("izvodjac_pjesma"),
    }