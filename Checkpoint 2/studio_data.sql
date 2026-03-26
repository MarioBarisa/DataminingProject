DROP DATABASE studio_data;
CREATE DATABASE IF NOT EXISTS studio_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE studio_data;

SELECT * FROM  zanr;
SELECT * FROM pjesma;


SELECT 
    p.naziv AS pjesma,
    i.ime AS izvodjac,
    z.naziv AS zanr,
    p.popularity
FROM
    pjesma p
        JOIN
    zanr z ON p.genre_fk = z.id
        JOIN
    izvodjac_pjesma ip ON p.track_id = ip.track_id
        JOIN
    izvodjac i ON ip.artist_id = i.id
ORDER BY p.popularity DESC
LIMIT 5