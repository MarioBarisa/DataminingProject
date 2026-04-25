import os
import subprocess
from pyspark.sql import SparkSession

os.environ.pop("SPARK_HOME", None)


def _ensure_java_home():
    java_home = os.environ.get("JAVA_HOME")
    if java_home and os.path.exists(java_home):
        return java_home

    java_home = subprocess.check_output(
        ["/usr/libexec/java_home", "-v", "17"]
    ).decode().strip()

    os.environ["JAVA_HOME"] = java_home
    os.environ["PATH"] = java_home + "/bin:" + os.environ.get("PATH", "")
    return java_home


def get_spark_session(app_name="ETL_Studio"):
    _ensure_java_home()

    return (
        SparkSession.builder
        .master("local[*]")
        .appName(app_name)
        .config("spark.jars.packages", "com.mysql:mysql-connector-j:9.2.0")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )