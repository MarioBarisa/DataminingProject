-- broj redova
SELECT 'star_dim_zanr'            AS tablica, COUNT(*) AS n FROM star_dim_zanr
UNION ALL
SELECT 'star_dim_izvodjac',                   COUNT(*) FROM star_dim_izvodjac
UNION ALL
SELECT 'star_dim_album',                      COUNT(*) FROM star_dim_album
UNION ALL
SELECT 'star_dim_audio_catchy',               COUNT(*) FROM star_dim_audio_catchy
UNION ALL
SELECT 'star_dim_audio_technical',            COUNT(*) FROM star_dim_audio_technical
UNION ALL
SELECT 'star_fact_popularnost',               COUNT(*) FROM star_fact_popularnost;

-- ne smije biti nullova
SELECT
    SUM(CASE WHEN zanr_tk      IS NULL THEN 1 ELSE 0 END) AS null_zanr,
    SUM(CASE WHEN izvodjac_tk  IS NULL THEN 1 ELSE 0 END) AS null_izvodjac,
    SUM(CASE WHEN album_tk     IS NULL THEN 1 ELSE 0 END) AS null_album,
    SUM(CASE WHEN catchy_tk    IS NULL THEN 1 ELSE 0 END) AS null_catchy,
    SUM(CASE WHEN technical_tk IS NULL THEN 1 ELSE 0 END) AS null_technical
FROM star_fact_popularnost;

-- provjera join-a
SELECT
    z.naziv AS zanr,
    z.zanr_grupa,
    ROUND(AVG(f.popularity), 2) AS avg_popularity,
    COUNT(*)                    AS n_pjesama
FROM star_fact_popularnost f
JOIN star_dim_zanr z ON f.zanr_tk = z.zanr_tk
GROUP BY z.zanr_tk
ORDER BY avg_popularity DESC
LIMIT 10;

-- izvpđači sa više od 1 ver
SELECT
    izvodjac_nk,
    COUNT(*) AS n_verzija,
    GROUP_CONCAT(ime ORDER BY valid_from SEPARATOR ' -> ') AS history
FROM star_dim_izvodjac
GROUP BY izvodjac_nk
HAVING n_verzija > 1
LIMIT 10;

-- velicina albuma
SELECT
    a.velicina_albuma,
    COUNT(*) AS n_fact_redaka,
    ROUND(AVG(f.popularity), 2) AS avg_popularity
FROM star_fact_popularnost f
JOIN star_dim_album a ON f.album_tk = a.album_tk
GROUP BY a.velicina_albuma
ORDER BY avg_popularity DESC;