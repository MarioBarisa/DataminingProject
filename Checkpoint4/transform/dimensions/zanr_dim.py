from pyspark.sql.functions import col, trim, udf, lit, when
from pyspark.sql.types import StringType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def _zanr_grupa(naziv):
    if naziv is None:
        return "Other"
    n = naziv.lower()
    if any(x in n for x in ["acoustic", "folk", "singer", "indie", "alt-country", "country"]):
        return "Chill/Acoustic"
    if any(x in n for x in ["pop", "power-pop", "synth-pop", "cantopop", "mandopop", "k-pop", "j-pop"]):
        return "Pop"
    if any(x in n for x in ["hip-hop", "rap", "trap", "r-n-b", "soul", "funk"]):
        return "Urban/R&B"
    if any(x in n for x in ["rock", "metal", "punk", "grunge", "garage", "hard-rock", "psych"]):
        return "Rock/Metal"
    if any(x in n for x in ["dance", "edm", "electro", "house", "techno", "trance", "dubstep", "drum"]):
        return "Electronic/Dance"
    if any(x in n for x in ["jazz", "blues", "classical", "piano", "opera", "show-tunes"]):
        return "Classic/Jazz"
    if any(x in n for x in ["latin", "salsa", "samba", "mpb", "pagode", "sertanejo", "axe", "forro"]):
        return "Latino/World"
    return "Other"

zanr_grupa_udf = udf(_zanr_grupa, StringType())

def transform_zanr_dim(zanr_df, csv_df=None):
    max_zanr_nk = (
        zanr_df
        .select(col("id").cast("int").alias("id"))
        .groupBy()
        .max("id")
        .collect()[0]["max(id)"]
    ) or 0

    df = (
        zanr_df
        .select(col("id").alias("zanr_nk"), trim(col("naziv")).alias("naziv"))
        .dropDuplicates(["naziv"])
        .fillna({"naziv": "Unknown"})
    )

    if csv_df is not None:
        # extract zanrova iz CSV koji mozda nisu u trenutnom DIM
        csv_zanr = (
            csv_df
            .select(trim(col("track_genre")).alias("naziv"))
            .distinct()
            .withColumn("zanr_nk", lit(None).cast("int"))
        )
        df = df.unionByName(csv_zanr).dropDuplicates(["naziv"])

    nk_window = Window.orderBy("naziv")
    df = (
        df
        .withColumn("_rn_nk", row_number().over(nk_window))
        .withColumn(
            "zanr_nk",
            when(col("zanr_nk").isNull(), lit(max_zanr_nk) + col("_rn_nk"))
            .otherwise(col("zanr_nk").cast("int"))
        )
        .drop("_rn_nk")
    )

    df = df.withColumn("zanr_grupa", zanr_grupa_udf(col("naziv")))
    window = Window.orderBy("naziv")
    df = df.withColumn("zanr_tk", row_number().over(window))
    return df.select("zanr_tk", "zanr_nk", "naziv", "zanr_grupa")