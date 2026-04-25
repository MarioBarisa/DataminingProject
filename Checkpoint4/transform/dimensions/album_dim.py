from pyspark.sql.functions import col, trim, count, udf, lit, when
from pyspark.sql.types import StringType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def _velicina_albuma(n):
    # prema broju pjesama se određuje o čemu je riječ
    if n is None or n <= 2:
        return "single"
    if n <= 6:
        return "EP"
    return "album"

velicina_udf = udf(_velicina_albuma, StringType())

def transform_album_dim(album_df, pjesma_df, csv_df=None):
    max_album_nk = (
        album_df
        .select(col("id").cast("int").alias("id"))
        .groupBy()
        .max("id")
        .collect()[0]["max(id)"]
    ) or 0

    count_df = (
        pjesma_df
        .groupBy(col("album_fk").alias("album_id_count"))
        .agg(count("*").alias("n_pjesama"))
    )

    df = (
        album_df
        .select(col("id").alias("album_nk"), trim(col("naziv")).alias("naziv"))
        .dropDuplicates(["naziv"])
        .join(count_df, col("album_nk") == col("album_id_count"), "left")
        .fillna({"n_pjesama": 0, "naziv": "Unknown Album"})
        .drop("album_id_count")
    )

    if csv_df is not None:
        csv_album = (
            csv_df
            .select(trim(col("album_name")).alias("naziv"))
            .distinct()
            .withColumn("album_nk", lit(None).cast("int"))
            .withColumn("n_pjesama", lit(0))
        )
        df = df.unionByName(csv_album).dropDuplicates(["naziv"])

    nk_window = Window.orderBy("naziv")
    df = (
        df
        .withColumn("_rn_nk", row_number().over(nk_window))
        .withColumn(
            "album_nk",
            when(col("album_nk").isNull(), lit(max_album_nk) + col("_rn_nk"))
            .otherwise(col("album_nk").cast("int"))
        )
        .drop("_rn_nk")
    )

    df = df.withColumn("velicina_albuma", velicina_udf(col("n_pjesama")))
    window = Window.orderBy("naziv")
    df = df.withColumn("album_tk", row_number().over(window))
    return df.select("album_tk", "album_nk", "naziv", "n_pjesama", "velicina_albuma")