# Pyha-dokumentaatio

## Yleisesti

Pyha on aineistopyynt�jen teko- , hallinnointi- ja seurantaj�rjestelm�.

Pyha:an on toteutettu nelj� k�ytt�j�ryhm��: yll�pit�j�t, viranomaiset, aineistojen omistajat ja maallikot.

Kirjautumalla j�rjestelm��n maallikot voivat luoda j�rjestelm��n uusia aineistopyynt�j�. He voivat my�s ladata hyv�ksyttyjen aineistopyynt�jen aineistoja, sek� seurata aineistopyynt�jens� k�sittely�. Viranomaisilta vaaditaan kirjautuminen, jonka j�lkeen he voivat k�yd� l�pi aineistopyynt�j�, hallita niiden tilaa, ja l�hett�� aineistonpyyt�jille kysymyksi�.

Tyypillinen workflow menee siten, ett� maallikko luo aineistopyynn�n valitsemillaan rajauksilla, k�ytt�tarkoituksella sek� yhteystiedoillaan j�rjestelm��n (hyv�ksyen tietosuojaehdot). Viranomaisille, sek� mahdollisesti aineiston haltijoille, l�hetet��n riitt�v�n lyhyin v�liajoin ilmoitus (s�hk�postitse) aineistopyynn�ist�, jotka vaativat heilt� toimenpiteit�. Mik�li kaikki aineistopyynt�� hallitsevat osapuolet (viranomaiset ja aineiston haltijat) ovat tehneet p��t�ksen (hyv�ksy/hylk��) koskien aineistopyynt��, l�hetet��n aineistopyynn�n tekij�lle t�st� ilmoitus (s�hk�postitse). Hyv�ksytyss� tapauksessa ilmoitus sis�lt�� linkin, jonka kautta maallikko voi (kirjautumisen j�lkeen) ladata aineistopyynt�� vastaavan aineiston itselleen.

J�rjestelm� tarjoaa vaihtoehtoisen toiminnon (ymp�rist�muuttuja), jolloin uudet pyynn�t voidaan k�sitell� pelk�st��n aineistonhoitajien toimesta. T�ll�in aineistonhoitajat vastaavat my�s aineistopyynt�jen omien aineistojen sensitiivisen sis�ll�n hallinnoinnista.

## J�rjestelm�n osat

### Pyynn�n valintan�kym� (/index)

Pyynn�n valintan�kym�ss� luetellaan kaikki maallikon tekem�t aineistopyynn�t, sek� kerrotaan niiden yleistiedot ja tila.
Aineistojen omistajille luetellaan kaikki aineistopyynn�t, jotka sis�lt�v�t aineistonomistajan aineistoja.

### Pyynn�n tilan�kym� (/requestview/id)

Pyynn�n tilan�kym�ss� n�ytet��n maallikolle kaikki pyynt��n, ja sen tilaan liittyv�t tiedot.
Aineistojen omistaja voi yll�mainitun lis�ksi tehd� p��t�ksen oman aineistonsa hyv�ksymisest� aineiston pyyt�j�lle.

### Pyynt�lomakkeen t�ytt�n�kym� (/requestform/id)

T�ytt�n�kym�ss� maallikko t�ytt�� aineistopyynn�n valitsemillaan rajauksilla, k�ytt�tarkoituksella sek� yhteystiedoillaan j�rjestelm��n (hyv�ksyen tietosuojaehdot).

### Uloskirjautuminen (/logout)

Tekee sen mit� alaotsikossa mainitaan.

### Rajapinta (/api/)

Tarjoaa rajapinnan toisille applikaatioille. ([Api-dokumentaatio](Api.md))

### Rajapinta ajax-kyselyille (/ajax/)

Tarjoaa rajapinnan ajax-kyselyille.

### Asetukset (/settings)

Tarjoaa administraattoreille asetuksia ohjelmiston automaattisen toiminnallisuuden muokkaamiseen.

## Arkkitehtuuri

### Tietokanta

Tietokannan tiedot l�ytyv�t t��lt�: [Tietokanta](Tietokanta.md)

### K��nn�kset

K��nt�misen tiedot l�ytyv�t t��lt�: [K��nt�minen](K��nt�minen.md)

### Tunnukset

Piilotettavat tunnisteet m��ritet��n ymp�rist�muuttujiin.
