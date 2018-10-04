# Pyha-dokumentaatio

## Yleisesti

Pyha on aineistopyynt�jen teko- , hallinnointi- ja seurantaj�rjestelm�. Pyha:an on toteutettu kolme k�ytt�j�ryhm��: viranomaiset, aineistojen omistajat ja maallikot. Kirjautumalla j�rjestelm��n maallikot voivat luoda j�rjestelm��n uusia aineistopyynt�j�. He voivat my�s ladata hyv�ksyttyjen aineistopyynt�jen aineistoja, sek� seurata aineistopyynt�jens� k�sittely�. Viranomaisilta vaaditaan kirjautuminen, jonka j�lkeen he voivat k�yd� l�pi aineistopyynt�j�, hallita niiden tilaa, ja l�hett�� aineistonpyyt�jille kysymyksi�.

Tyypillinen workflow menee siten, ett� maallikko luo aineistopyynn�n valitsemillaan rajauksilla, k�ytt�tarkoituksella sek� yhteystiedoillaan j�rjestelm��n (hyv�ksyen tietosuojaehdot). Viranomaisille, sek� mahdollisesti aineiston haltijoille, l�hetet��n riitt�v�n lyhyin v�liajoin ilmoitus (s�hk�postitse) aineistopyynn�ist�, jotka vaativat heilt� toimenpiteit�. Mik�li kaikki aineistopyynt�� hallitsevat osapuolet (viranomaiset ja aineiston haltijat) ovat tehneet p��t�ksen (hyv�ksy/hylk��) koskien aineistopyynt��, l�hetet��n aineistopyynn�n tekij�lle t�st� ilmoitus (s�hk�postitse). Hyv�ksytyss� tapauksessa ilmoitus sis�lt�� linkin, jonka kautta maallikko voi (kirjautumisen j�lkeen) ladata aineistopyynt�� vastaavan aineiston itselleen.

## J�rjestelm�n osat

### Pyynn�n valinta n�kym� (/index)

Pyynn�n valintan�kym�ss� luetellaan kaikki maallikon tekem�t aineistopyynn�t, sek� kerrotaan niiden yleistiedot ja tila.
Aineistojen omistajille luetellaan kaikki aineistopyynn�t, jotka sis�lt�v�t aineistonomistajan aineistoja.
Viranomaisille luetellaan kaikki aineistopyynn�t, jotka sis�lt�v�t sensitiivisi� havaintoja.

### Pyynn�n tilan�kym� (/requestview/id)

Pyynn�n tilan�kym�ss� n�ytet��n maallikolle kaikki pyynt��n, ja sen tilaan liittyv�t tiedot.
Aineistojen omistaja voi yll�mainitun lis�ksi tehd� p��t�ksen oman aineistonsa hyv�ksymisest� aineiston pyyt�j�lle.

### Pyynt�lomakkeen t�ytt�n�kym� (/requestform/id)

T�ytt�n�kym�ss� maallikko t�ytt�� aineistopyynn�n valitsemillaan rajauksilla, k�ytt�tarkoituksella sek� yhteystiedoillaan j�rjestelm��n (hyv�ksyen tietosuojaehdot).


## Arkkitehtuuri

### Tietokanta

Tietokannan tiedot l�ytyv�t t��lt�: [Tietokanta](dokumentaatio/Tietokanta.md)

### Tunnukset

Piilotettavat tunnisteet m��ritet��n ymp�rist�muuttujiin.

### LajiStore

Lue lis�� LajiStoresta: [https://bitbucket.org/luomus/lajistore-api](https://bitbucket.org/luomus/lajistore-api)

### TipuApi

TipuApi-service hakee TipuApista tiedot lajeista Species-luokan ilmentymin�.

### LajiAuth

LajiAuthin toimintalogiikka on seuraava:

1. Kirjautumissivulla (login.html) on linkit kirjautumispalveluihin. Linkkien hrefiss� kulkee j�rjestelm�n tunnus ja relatiivinen polku, jonne ohjataan kirjautumisen j�lkeen
2. Luomus m��ritt�� j�rjestelm�n tunnusta vastaavan uudelleenohjausosoitteen. Tunnuksia on kaksi: yksi stagingiin ja toinen localhostiin osoittava
3. K�ytt�j� tulee takaisin j�rjestelm�n login-sivulle POST pyynn�ll� tokenin kanssa, joka luetaan backendissa parametrista "token"
4. Tokenin oikeellisuus l�hetet��n backendiss� laji-authille validoitavaksi POST'n bodyss�
  - POST https://login.laji.fi/validation/
  - Content-Type: application/json
  - Body: &lt;token&gt;
5. Jos validointi onnistui, vastauksena saadaan k�ytt�j�n tiedot -- Muussa tapauksessa k�ytt�j�� ei tule p��st�� sis�lle

Lue lis�� LajiAuthista: [https://bitbucket.org/luomus/laji-auth](https://bitbucket.org/luomus/laji-auth)
