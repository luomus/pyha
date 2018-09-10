Nämä ohjeet on kirjoitettu Ubuntulle, ja etänä käytettävälle Oracle tietokantapalvelimelle.

## 1 - Oracle client asentaminen

Asenna *Oracle Instant Client Basic Linux 12.1.0.2.0* ja *Instant Client SDK Linux 12.1.0.2.0* seuraavasti. Lataa ne [täältä](https://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html). Pura arkistot (ne purkautuvat samaan kansioon). Sen jälkeen lisää tiedostoon `~/.bashrc` seuraavan malliset rivit:

	export ORACLE_HOME=path/to/instantclient_12_1  
 	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

Aja terminaalissa:

	source ~/.bashrc

Tai käynnistä terminaali uudelleen, että `~/.bashrc` asennetut ympäristömuuttujat tulevat voimaan.

Tämän jälkeen tee seuraava:

	cd path/to/instantclient_12_1  
	ln -s libclntsh.so.12.1 libclntsh.so  
	ln -s libocci.so.12.1 libocci.so

## 2 - Kehitysympäristön pystyttäminen

Asenna seuraavat packaget `sudo apt-get install`in avulla:

	sudo apt-get update

	sudo apt-get install build-essential python3-dev python-pip python3-pip python-virtualenv git libaio1

Luo kansio, mihin aiot asentaa ympäristön esim.

	mkdir ~/pyyntojenhallinta

Siirry kansioon

	cd ~/pyyntojenhallinta

Kloonaa repositorio:

	git clone https://kayttajanimi@bitbucket.org/luomus/pyha.git

## 3 - Automaattinen asentaminen

Aja automaattista asentamista varten luotu skripti:

	install.sh

Mikäli automaattinen asennus onnistui, voit ylittää kohdan 3.

## 4 - Asentaminen käsin

Seuraava rivi luo uuden virtuaalienv-ympäristön python 3:lla omaan kansioon env:

	virtualenv -p python3 env

Avaa python virtuaaliympäristö:

	source env/bin/activate

Asenna python virtuaaliympäristöön järjestelmän vaatimat ohjelmat:

	pip install -r Requirements.txt








