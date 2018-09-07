## 1 - Kehitysympäristön pystyttäminen

Nämä ohjeet on kirjoitettu Ubuntulle, ja etänä käytettävälle Oracle tietokantapalvelimelle.

Asenna *Oracle Instant Client* ja *Instant Client SDK* seuraavasti. Lataa ne [täältä](http://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html). Pura arkistot (ne purkautuvat samaan kansioon). Sen jälkeen lisää tiedostoon `~/.bashrc` seuraavan malliset rivit:

	export ORACLE_HOME=path/to/instantclient_xx_x  
 	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

Sulje ja käynnistä terminaali uudelleen, minkä jälkeen tee seuraava:

	cd path/to/instantclient_xx_x  
	ln -s libclntsh.so.xx.x libclntsh.so  
	ln -s libocci.so.xx.x libocci.so

Missä xx_x ja xx.x ovat versionumeroita.

Asenna seuraavat packaget `sudo apt-get install`in avulla:

	sudo apt-get update

	sudo apt-get install build-essential python3-dev python-pip python3-pip python-virtualenv git libaio1

Luo kansio, mihin aiot asentaa ympäristön esim.

	mkdir ~/pyyntojenhallinta

Siirry kansioon

	cd ~/pyyntojenhallinta

Kloonaa repositorio:

	git clone https://kayttajanimi@bitbucket.org/luomus/pyha.git

## 2 - Automaattinen asentaminen

Aja automaattista asentamista varten luotu skripti:

	install.sh

Mikäli automaattinen asennus onnistui, voit ylittää kohdan 3.

## 3 - Asentaminen käsin

Seuraava rivi luo uuden virtuaalienv-ympäristön python 3:lla omaan kansioon env:

	virtualenv -p python3 env

Avaa virtuaaliympäristö:

	source env/bin/activate

Asenna virtuaaliympäristöön järjestelmän vaatimat ohjelmat:

	pip install django
	pip install django_extensions
	pip install requests  
	pip install cx_Oracle  
	pip install gunicorn




