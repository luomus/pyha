# Pyha-dokumentaatio

## Yleisesti

Pyha on aineistopyyntöjen teko- , hallinnointi- ja seurantajärjestelmä. Pyha:an on toteutettu kolme käyttäjäryhmää: viranomaiset, aineistojen omistajat ja maallikot. Kirjautumalla järjestelmään maallikot voivat luoda järjestelmään uusia aineistopyyntöjä. He voivat myös ladata hyväksyttyjen aineistopyyntöjen aineistoja, sekä seurata aineistopyyntöjensä käsittelyä. Viranomaisilta vaaditaan kirjautuminen, jonka jälkeen he voivat käydä läpi aineistopyyntöjä, hallita niiden tilaa, ja lähettää aineistonpyytäjille kysymyksiä.

Tyypillinen workflow menee siten, että maallikko luo aineistopyynnön valitsemillaan rajauksilla, käyttötarkoituksella sekä yhteystiedoillaan järjestelmään (hyväksyen tietosuojaehdot). Viranomaisille, sekä mahdollisesti aineiston haltijoille, lähetetään riittävän lyhyin väliajoin ilmoitus (sähköpostitse) aineistopyynnöistä, jotka vaativat heiltä toimenpiteitä. Mikäli kaikki aineistopyyntöä hallitsevat osapuolet (viranomaiset ja aineiston haltijat) ovat tehneet päätöksen (hyväksy/hylkää) koskien aineistopyyntöä, lähetetään aineistopyynnön tekijälle tästä ilmoitus (sähköpostitse). Hyväksytyssä tapauksessa ilmoitus sisältää linkin, jonka kautta maallikko voi (kirjautumisen jälkeen) ladata aineistopyyntöä vastaavan aineiston itselleen.

Järjestelmä tarjoaa vaihtoehtoisen toiminnon (ympäristömuuttuja), jolloin uudet pyynnöt voidaan käsitellä pelkästään aineistonhoitajien toimesta. Tällöin aineistonhoitajat vastaavat myös aineistopyyntöjen omien aineistojen sensitiivisen sisällön hallinnoinnista.

## Järjestelmän osat

### Pyynnön valintanäkymä (/index)

Pyynnön valintanäkymässä luetellaan kaikki maallikon tekemät aineistopyynnöt, sekä kerrotaan niiden yleistiedot ja tila.
Aineistojen omistajille luetellaan kaikki aineistopyynnöt, jotka sisältävät aineistonomistajan aineistoja.
Viranomaisille luetellaan kaikki aineistopyynnöt, jotka sisältävät sensitiivisiä havaintoja.

### Pyynnön tilanäkymä (/requestview/id)

Pyynnön tilanäkymässä näytetään maallikolle kaikki pyyntöön, ja sen tilaan liittyvät tiedot.
Aineistojen omistaja voi yllämainitun lisäksi tehdä päätöksen oman aineistonsa hyväksymisestä aineiston pyytäjälle.

### Pyyntölomakkeen täyttönäkymä (/requestform/id)

Täyttönäkymässä maallikko täyttää aineistopyynnön valitsemillaan rajauksilla, käyttötarkoituksella sekä yhteystiedoillaan järjestelmään (hyväksyen tietosuojaehdot).

### Uloskirjautuminen (/logout)

Tekee sen mitä alaotsikossa mainitaan.

### Rajapinta (/api/)

Tarjoaa rajapinnan toisille aplikaatioille.

### Rajapinta ajax-kyselyille (/ajax/)

Tarjoaa rajapinnan ajax-kyselyille.



## Arkkitehtuuri

### Tietokanta

Tietokannan tiedot löytyvät täältä: [Tietokanta](Tietokanta.md)

### Tunnukset

Piilotettavat tunnisteet määritetään ympäristömuuttujiin.
