N�m� ohjeet on kirjoitettu Ubuntulle, ja et�n� k�ytett�v�lle Oracle tietokantapalvelimelle.

## 1 - Oracle client asentaminen

Asenna *Oracle Instant Client Basic Linux 12.1.0.2.0* ja *Instant Client SDK Linux 12.1.0.2.0* seuraavasti. Lataa ne [t��lt�](https://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html). Pura arkistot (ne purkautuvat samaan kansioon). Sen j�lkeen lis�� tiedostoon `~/.bashrc` seuraavan malliset rivit:

	export ORACLE_HOME=path/to/instantclient_12_1  
 	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

Aja terminaalissa:

	source ~/.bashrc

Tai k�ynnist� terminaali uudelleen, ett� `~/.bashrc` asennetut ymp�rist�muuttujat tulevat voimaan.

T�m�n j�lkeen tee seuraava:

	cd path/to/instantclient_12_1  
	ln -s libclntsh.so.12.1 libclntsh.so  
	ln -s libocci.so.12.1 libocci.so

## 2 - Kehitysymp�rist�n pystytt�minen

Asenna seuraavat packaget `sudo apt-get install`in avulla:

	sudo apt-get update

	sudo apt-get install build-essential python3-dev python-pip python3-pip python-virtualenv git libaio1

Luo kansio, mihin aiot asentaa ymp�rist�n esim.

	mkdir ~/pyyntojenhallinta

Siirry kansioon

	cd ~/pyyntojenhallinta

Kloonaa repositorio:

	git clone https://kayttajanimi@bitbucket.org/luomus/pyha.git

## 3 - Automaattinen asentaminen

Aja automaattista asentamista varten luotu skripti:

	install.sh

Mik�li automaattinen asennus onnistui, voit ylitt�� kohdan 3.

## 4 - Asentaminen k�sin

Seuraava rivi luo uuden virtuaalienv-ymp�rist�n python 3:lla omaan kansioon env:

	virtualenv -p python3 env

Avaa python virtuaaliymp�rist�:

	source env/bin/activate

Asenna python virtuaaliymp�rist��n j�rjestelm�n vaatimat ohjelmat:

	pip install -r Requirements.txt








