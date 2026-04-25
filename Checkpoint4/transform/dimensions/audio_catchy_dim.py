from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def _energy_segment(e):
    if e is None: return "unknown"
    if e < 0.33: return "low"
    if e < 0.66: return "mid"
    return "high"

def _valence_segment(v):
    if v is None: return "unknown"
    if v < 0.33: return "negative"
    if v < 0.66: return "neutral"
    return "positive"

_catchy_map = {
    ("high", "positive"): "Energetican/Pozitivan",
    ("high", "neutral"):  "Energetican/Neutralan",
    ("high", "negative"): "Energetican",
    ("mid",  "positive"): "Umjeren/Pozitivan",
    ("mid",  "neutral"):  "Umjeren/Neutralan",
    ("mid",  "negative"): "Umjeren",
    ("low",  "positive"): "Miran/Pozitivan",
    ("low",  "neutral"):  "Miran/Neutralan",
    ("low",  "negative"): "Miran",
}

def _catchy_karakter(es, vs):
    return _catchy_map.get((es, vs), "Nepoznato")

energy_udf  = udf(_energy_segment, StringType())
valence_udf = udf(_valence_segment, StringType())
catchy_udf  = udf(_catchy_karakter, StringType())

def transform_audio_catchy_dim(pjesma_df, csv_df=None):
    def _select_catchy(df):
        return df.select(
            col("track_id"),
            col("danceability").cast("double"),
            col("valence").cast("double"),
            col("energy").cast("double"),
            col("liveness").cast("double"),
            col("speechiness").cast("double")
        )

    df = _select_catchy(pjesma_df)

    if csv_df is not None:
        df = df.unionByName(_select_catchy(csv_df))

    df = (
        df
        .dropDuplicates(["track_id"])
        .dropna(subset=["track_id"])
        .withColumn("energy_segment",  energy_udf(col("energy")))
        .withColumn("valence_segment", valence_udf(col("valence")))
        .withColumn("catchy_karakter", catchy_udf(col("energy_segment"), col("valence_segment")))
    )

    window = Window.orderBy("track_id")
    df = df.withColumn("catchy_tk", row_number().over(window))

    return df.select(
        "catchy_tk", "track_id", "danceability", "valence",
        "energy", "liveness", "speechiness",
        "energy_segment", "valence_segment", "catchy_karakter"
    )