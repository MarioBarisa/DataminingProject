from pyspark.sql.functions import col, trim, lit, current_date, explode, split, when
from pyspark.sql.types import BooleanType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def transform_izvodjac_dim(izvodjac_df, csv_df=None):
    max_izvodjac_nk = (
        izvodjac_df
        .select(col("id").cast("int").alias("id"))
        .groupBy()
        .max("id")
        .collect()[0]["max(id)"]
    ) or 0

    df = (
        izvodjac_df
        .select(col("id").alias("izvodjac_nk"), trim(col("ime")).alias("ime"))
        .dropDuplicates(["ime"])
        .fillna({"ime": "Unknown Artist"})
    )

    if csv_df is not None:
        csv_izv = (
            csv_df
            .select(explode(split(col("artists"), ";")).alias("ime"))
            .select(trim(col("ime")).alias("ime"))
            .distinct()
            .withColumn("izvodjac_nk", lit(None).cast("int"))
        )
        df = df.unionByName(csv_izv).dropDuplicates(["ime"])

    nk_window = Window.orderBy("ime")
    df = (
        df
        .withColumn("_rn_nk", row_number().over(nk_window))
        .withColumn(
            "izvodjac_nk",
            when(col("izvodjac_nk").isNull(), lit(max_izvodjac_nk) + col("_rn_nk"))
            .otherwise(col("izvodjac_nk").cast("int"))
        )
        .drop("_rn_nk")
    )

    df = (
        df
        .withColumn("valid_from", current_date())
        .withColumn("valid_to", lit("9999-12-31").cast("date"))
        .withColumn("is_current", lit(True).cast(BooleanType()))
    )
    window = Window.orderBy("ime")
    df = df.withColumn("izvodjac_tk", row_number().over(window))
    return df.select("izvodjac_tk", "izvodjac_nk", "ime", "valid_from", "valid_to", "is_current")