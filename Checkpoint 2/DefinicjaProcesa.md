## Opis poslovnog konteksta

Studio d.o.o. je glazbeni studio koji profesionalno producira i snima glazbu za vlastite klijente. Studio surađuje s više od 50 izvođača godišnje, raspoređenih u različite glazbene žanrove. Svaki izvođač snima pjesme koje se objavljuju na streaming platformama, pri čemu je cilj studija maksimizirati popularnost objavljenih pjesama kroz analizu audio trendova.

Kako bi donošenje produkcijskih odluka bilo temeljeno na podacima, Studio d.o.o. analizira skup podataka od 114.000 pjesama s platforme Spotify, raspoređenih u 125 glazbenih žanrova. Svaka pjesma sadrži žanr,izvođača, album, 18+?, izmjerene audio značajke (danceability, energy, valence, tempo i dr.) i numeričku metriku popularnosti (0–100) uz ostale. Podaci su prikupljeni putem Spotify Web API-ja i dostupni u CSV formatu.

## Poslovni cilj

Studio želi odgovoriti na sljedeća pitanja:

- Koje audio karakteristike (tempo, energy, danceability, valence…) koreliraju s visokom popularnošću pjesme?
- Koji žanrovi trenutno ostvaruju najveću prosječnu popularnost na platformi te uz koje audio           karakteristike?
- Kako se popularnost razlikuje između eksplicitnih i neeksplicitnih pjesama?
- Koje kombinacije audio značajki Studio treba targetirati pri produkciji novih pjesama kako bi one bile što kompetitivnije?
- Što slušatelji/publika očekuju od određenog žanra.
- Koji je idealan omjer različitih audio karatkteristika za različite vrste pjesama / žanrova.


## Tablica kardinalnosti veza:

| Entitet A | Veza       | Entitet B | Tip | Obrazloženje                                                                                                                        |
| --------- | ---------- | --------- | --- | ----------------------------------------------------------------------------------------------------------------------------------- |
| ZANR      | Pripada    | PJESMA    | 1:M | Jedan žanr obuhvaća više pjesama; svaka pjesma pripada točno jednom žanru                                                           |
| ALBUM     | Sadrži     | PJESMA    | 1:M | Jedan album sadrži više pjesama; svaka pjesma pripada točno jednom albumu                                                           |
| IZVODJAC  | Izvodi     | PJESMA    | M:M | Jedan izvođač izvodi više pjesama; jedna pjesma može imati više izvođača — razrješava se asocijativnom tablicom IZVODJAC_PJESMA     |
| IZVODJAC  | Objavljuje | ALBUM     | M:M | Jedan izvođač može objaviti više albuma; jedan album može imati više izvođača — razrješava se asocijativnom tablicom IZVODJAC_ALBUM |