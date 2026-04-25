# orkestracija
# prvo dimenzije -> fact tablica

from transform.dimensions.zanr_dim           import transform_zanr_dim
from transform.dimensions.izvodjac_dim       import transform_izvodjac_dim
from transform.dimensions.album_dim          import transform_album_dim
from transform.dimensions.audio_catchy_dim   import transform_audio_catchy_dim
from transform.dimensions.audio_tehnical_dim import transform_audio_technical_dim
from transform.facts.popularnost_fact        import transform_popularnost_fact

def run_transformations(raw_data):
    csv_df = raw_data.get("csv_spotify")

    # 1. dim zanra
    zanr_dim = transform_zanr_dim(raw_data["zanr"], csv_df)
    print("1/5 dim_zanr zavrsena")

    # 2. dim izvođaca " scd t2 "
    izvodjac_dim = transform_izvodjac_dim(raw_data["izvodjac"], csv_df)
    print("2/5 dim_izvodjac zavrsena (SCD2)")

    # 3. dim albuma (s brojem pjesama iz tablice pjesma)
    album_dim = transform_album_dim(raw_data["album"], raw_data["pjesma"], csv_df)
    print("3/5 dim_album zavrsena")

    # 4. audio catchiness dimenzija
    audio_catchy_dim = transform_audio_catchy_dim(raw_data["pjesma"], csv_df)
    print("4a/5 dim_audio_catchy zavrsena")

    # 5. audio tehnicka dimenzija
    audio_technical_dim = transform_audio_technical_dim(raw_data["pjesma"], csv_df)
    print("4b/5 dim_audio_technical zavrsena")

    # 6. fact tablica 
    fact_popularnost = transform_popularnost_fact(
        raw_data,
        zanr_dim,
        izvodjac_dim,
        album_dim,
        audio_catchy_dim,
        audio_technical_dim
    )
    print("5/5 fact_popularnost zavrsena")

    return {
        "star_dim_zanr":             zanr_dim,
        "star_dim_izvodjac":         izvodjac_dim,
        "star_dim_album":            album_dim,
        "star_dim_audio_catchy":     audio_catchy_dim,
        "star_dim_audio_technical":  audio_technical_dim,
        "star_fact_popularnost":     fact_popularnost,
    }