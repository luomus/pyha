# Pyha-dokumentaatio

## Yleisesti

Pyha on aineistopyyntöjen teko- , hallinnointi- ja seurantajärjestelmä. Pyha:an on toteutettu kolme käyttäjäryhmää: viranomaiset, aineistojen omistajat ja maallikot. Kirjautumalla järjestelmään maallikot voivat luoda järjestelmään uusia aineistopyyntöjä. He voivat myös ladata hyväksyttyjen aineistopyyntöjen aineistoja, sekä seurata aineistopyyntöjensä käsittelyä. Viranomaisilta vaaditaan kirjautuminen, jonka jälkeen he voivat käydä läpi aineistopyyntöjä, hallita niiden tilaa, ja lähettää aineistonpyytäjille kysymyksiä.

Tyypillinen workflow menee siten, että maallikko luo aineistopyynnön valitsemillaan rajauksilla, käyttötarkoituksella sekä yhteystiedoillaan järjestelmään (hyväksyen tietosuojaehdot). Viranomaisille, sekä mahdollisesti aineiston haltijoille, lähetetään riittävän lyhyin väliajoin ilmoitus (sähköpostitse) aineistopyynnöistä, jotka vaativat heiltä toimenpiteitä. Mikäli kaikki aineistopyyntöä hallitsevat osapuolet (viranomaiset ja aineiston haltijat) ovat tehneet päätöksen (hyväksy/hylkää) koskien aineistopyyntöä, lähetetään aineistopyynnön tekijälle tästä ilmoitus (sähköpostitse). Hyväksytyssä tapauksessa ilmoitus sisältää linkin, jonka kautta maallikko voi (kirjautumisen jälkeen) ladata aineistopyyntöä vastaavan aineiston itselleen.

## Järjestelmän osat

### Pyynnön valinta näkymä (/index)

Pyynnön valintanäkymässä luetellaan kaikki maallikon tekemät aineistopyynnöt, sekä kerrotaan niiden yleistiedot ja tila.
Aineistojen omistajille luetellaan kaikki aineistopyynnöt, jotka sisältävät aineistonomistajan aineistoja.
Viranomaisille luetellaan kaikki aineistopyynnöt, jotka sisältävät sensitiivisiä havaintoja.

### Pyynnön tilanäkymä (/requestview/id)

Pyynnön tilanäkymässä näytetään maallikolle kaikki pyyntöön, ja sen tilaan liittyvät tiedot.
Aineistojen omistaja voi yllämainitun lisäksi tehdä päätöksen oman aineistonsa hyväksymisestä aineiston pyytäjälle.

### Pyyntölomakkeen täyttönäkymä (/requestform/id)

Täyttönäkymässä maallikko täyttää aineistopyynnön valitsemillaan rajauksilla, käyttötarkoituksella sekä yhteystiedoillaan järjestelmään (hyväksyen tietosuojaehdot).


## Arkkitehtuuri

### Tietokanta

Tietokannan tiedot löytyvät täältä: [Tietokanta](dokumentaatio/Tietokanta.md)

### Tunnukset

Piilotettavat tunnisteet määritetään ympäristömuuttujiin.

### LajiStore

Lue lisää LajiStoresta: [https://bitbucket.org/luomus/lajistore-api](https://bitbucket.org/luomus/lajistore-api)

### TipuApi

TipuApi-service hakee TipuApista tiedot lajeista Species-luokan ilmentyminä.

### LajiAuth

LajiAuthin toimintalogiikka on seuraava:

1. Kirjautumissivulla (login.html) on linkit kirjautumispalveluihin. Linkkien hrefissä kulkee järjestelmän tunnus ja relatiivinen polku, jonne ohjataan kirjautumisen jälkeen
2. Luomus määrittää järjestelmän tunnusta vastaavan uudelleenohjausosoitteen. Tunnuksia on kaksi: yksi stagingiin ja toinen localhostiin osoittava
3. Käyttäjä tulee takaisin järjestelmän login-sivulle POST pyynnöllä tokenin kanssa, joka luetaan backendissa parametrista "token"
4. Tokenin oikeellisuus lähetetään backendissä laji-authille validoitavaksi POST'n bodyssä
  - POST https://login.laji.fi/validation/
  - Content-Type: application/json
  - Body: &lt;token&gt;
5. Jos validointi onnistui, vastauksena saadaan käyttäjän tiedot -- Muussa tapauksessa käyttäjää ei tule päästää sisälle

Lue lisää LajiAuthista: [https://bitbucket.org/luomus/laji-auth](https://bitbucket.org/luomus/laji-auth)
