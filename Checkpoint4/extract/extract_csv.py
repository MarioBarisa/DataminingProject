from spar_session import get_spark_session

def extract_from_csv(file_path):
    spark = get_spark_session("ETL_Studio")
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("multiLine", True)
        .option("escape", '"')
        .csv(file_path)
    )
    return df