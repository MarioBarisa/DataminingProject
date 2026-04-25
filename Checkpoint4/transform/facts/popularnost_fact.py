# izrada fact tablice star_fact_popularnost.
# Mjere: popularity, duration_ms. Degenerirana dim: explicit.
# povezivanje s dimenzijama putem surogat kljuceva (_tk).

from pyspark.sql.functions import col, trim, lower, split, lit
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def transform_popularnost_fact(raw_data, zanr_dim, izvodjac_dim, album_dim, audio_catchy_dim, audio_technical_dim):
    pjesma_df          = raw_data["pjesma"]
    izvodjac_pjesma_df = raw_data["izvodjac_pjesma"]
    csv_df             = raw_data.get("csv_spotify")

    # sql fact baza
    sql_fact_base = (
        pjesma_df
        .select(
            col("track_id"),
            col("popularity").cast("int"),
            col("duration_ms").cast("int"),
            col("explicit").cast("boolean"),
            col("genre_fk").cast("int").alias("genre_fk"),
            col("album_fk").cast("int").alias("album_fk")
        )
        .dropDuplicates(["track_id"])
        .dropna(subset=["track_id"])
    )

    izv_dedup = (
        izvodjac_pjesma_df
        .select(
            col("track_id").alias("ip_track_id"),
            col("artist_id").cast("int").alias("artist_id")
        )
        .dropDuplicates(["ip_track_id"])
    )

    sql_fact_base = (
        sql_fact_base
        .join(izv_dedup, sql_fact_base["track_id"] == izv_dedup["ip_track_id"], "left")
        .drop("ip_track_id")
        .withColumn("source_priority", lit(0))
    )

    zanr_lookup_nk = zanr_dim.select(
        col("zanr_nk").cast("int").alias("zanr_nk"),
        col("zanr_tk")
    )
    izv_lookup_nk = izvodjac_dim.filter(col("is_current") == True).select(
        col("izvodjac_nk").cast("int").alias("izvodjac_nk"),
        col("izvodjac_tk")
    )
    album_lookup_nk = album_dim.select(
        col("album_nk").cast("int").alias("album_nk"),
        col("album_tk")
    )

    sql_fact_tk = (
        sql_fact_base
        .join(zanr_lookup_nk,  sql_fact_base["genre_fk"] == zanr_lookup_nk["zanr_nk"], "left")
        .join(izv_lookup_nk,   sql_fact_base["artist_id"] == izv_lookup_nk["izvodjac_nk"], "left")
        .join(album_lookup_nk, sql_fact_base["album_fk"] == album_lookup_nk["album_nk"], "left")
        .select(
            col("track_id"),
            col("zanr_tk"),
            col("izvodjac_tk"),
            col("album_tk"),
            col("popularity"),
            col("duration_ms"),
            col("explicit"),
            col("source_priority")
        )
    )

    # csv lookup po nazivima za dodatnih 20%
    csv_fact_tk = None
    if csv_df is not None:
        zanr_lookup_name = zanr_dim.select(
            lower(trim(col("naziv"))).alias("genre_name_norm"),
            col("zanr_tk")
        )
        album_lookup_name = album_dim.select(
            lower(trim(col("naziv"))).alias("album_name_norm"),
            col("album_tk")
        )
        izv_lookup_name = izvodjac_dim.filter(col("is_current") == True).select(
            lower(trim(col("ime"))).alias("artist_name_norm"),
            col("izvodjac_tk")
        )

        csv_fact_base = (
            csv_df
            .select(
                col("track_id"),
                col("popularity").cast("int"),
                col("duration_ms").cast("int"),
                col("explicit").cast("boolean").alias("explicit"),
                lower(trim(col("track_genre"))).alias("genre_name_norm"),
                lower(trim(col("album_name"))).alias("album_name_norm"),
                lower(trim(split(col("artists"), ";").getItem(0))).alias("artist_name_norm")
            )
            .dropDuplicates(["track_id"])
            .dropna(subset=["track_id"])
            .withColumn("source_priority", lit(1))
        )

        csv_fact_tk = (
            csv_fact_base
            .join(zanr_lookup_name,  "genre_name_norm", "left")
            .join(album_lookup_name, "album_name_norm", "left")
            .join(izv_lookup_name,   "artist_name_norm", "left")
            .select(
                col("track_id"),
                col("zanr_tk"),
                col("izvodjac_tk"),
                col("album_tk"),
                col("popularity"),
                col("duration_ms"),
                col("explicit"),
                col("source_priority")
            )
        )

    if csv_fact_tk is not None:
        fact_base_tk = sql_fact_tk.unionByName(csv_fact_tk)
    else:
        fact_base_tk = sql_fact_tk

    # za iste track_id zadrzi sql redak 
    dedup_window = Window.partitionBy("track_id").orderBy("source_priority")
    fact_base_tk = (
        fact_base_tk
        .withColumn("_rn", row_number().over(dedup_window))
        .filter(col("_rn") == 1)
        .drop("_rn", "source_priority")
    )

    # track_id -> catchy_tk
    catchy_lookup = audio_catchy_dim.select("track_id", "catchy_tk")

    # track_id -> technical_tk
    technical_lookup = audio_technical_dim.select("track_id", "technical_tk")

    # spajanje redom
    fact_df = (
        fact_base_tk
        .join(catchy_lookup,  "track_id", "left")
        .join(technical_lookup, "track_id", "left")
        .select(
            col("track_id"),
            col("zanr_tk"),
            col("izvodjac_tk"),
            col("album_tk"),
            col("catchy_tk"),
            col("technical_tk"),
            col("popularity"),
            col("duration_ms"),
            col("explicit")
        )
    )

    # gen surogat kljuca fact_tk
    window = Window.orderBy("track_id")
    fact_df = fact_df.withColumn("fact_tk", row_number().over(window))

    return fact_df.select(
        "fact_tk", "track_id", "zanr_tk", "izvodjac_tk",
        "album_tk", "catchy_tk", "technical_tk",
        "popularity", "duration_ms", "explicit"
    )