from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def _tempo_band(t):
    if t is None:
        return "unknown"
    if t < 90:
        return "slow"
    if t < 140:
        return "mid"
    return "fast"

tempo_udf = udf(_tempo_band, StringType())

def transform_audio_technical_dim(pjesma_df, csv_df=None):
    def _select_technical(df, id_col):
        return df.select(
            col(id_col).alias("track_id"),
            col("loudness").cast("double"),
            col("acousticness").cast("double"),
            col("instrumentalness").cast("double"),
            col("key").cast("int"),
            col("mode").cast("int"),
            col("tempo").cast("double"),
            col("time_signature").cast("int")
        )

    df = _select_technical(pjesma_df, "track_id")

    if csv_df is not None:
        csv_tech = _select_technical(csv_df, "track_id")
        df = df.unionByName(csv_tech)

    df = (
        df
        .dropDuplicates(["track_id"])
        .dropna(subset=["track_id"])
        .withColumn("tempo_band", tempo_udf(col("tempo")))
    )
    window = Window.orderBy("track_id")
    df = df.withColumn("technical_tk", row_number().over(window))
    return df.select(
        "technical_tk", "track_id", "loudness", "acousticness",
        "instrumentalness", "key", "mode", "tempo", "time_signature", "tempo_band"
    )