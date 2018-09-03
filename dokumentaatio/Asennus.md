## 1 - Kehitysympäristön pystyttäminen

Nämä ohjeet on kirjoitettu Ubuntulle, ja etänä käytettävälle Oracle tietokantapalvelimelle.

Luo kansio, mihin aiot asentaa ympäristön esim.

	mkdir ~/pyyntojenhallinta

Siirry kansioon

	cd ~/pyyntojenhallinta

Asenna *Oracle Instant Client* ja *Instant Client SDK* seuraavasti. Lataa ne [täältä](http://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html). Pura arkistot (ne purkautuvat samaan kansioon). Sen jälkeen lisää tiedostoon `~/.bashrc` seuraavan malliset rivit:

	export ORACLE_HOME=~/Downloads/instantclient_12_1  
 	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

Ja tee seuraava:

	cd ~/Downloads/instantclient_12_1  
	ln -s libclntsh.so.12.1 libclntsh.so  
	ln -s libocci.so.12.1 libocci.so

Kloonaa repositorio:

	git clone https://kayttajanimi@bitbucket.org/luomus/pyha.git

## 2 - Automaattinen asentaminen

Aja automaattista asentamista varten luotu skripti:

	install.sh

Mikäli automaattinen asennus onnistui, voit ylittää kohdan 3.

## 3 - Asentaminen käsin

Aluksi asenna seuraavat packaget `sudo apt-get install`in avulla:

	build-essential  
	python3-dev  
	python-pip  
	python3-pip  
	python-virtualenv

Seuraava rivi luo uuden virtuaalienv-ympäristön python 3:lla omaan kansioon env:

	virtualenv -p python3 env

Avaa virtuaaliympäristö:

	source env/bin/activate

Asenna virtuaaliympäristöön järjestelmän vaatimat ohjelmat:

	pip install django
	pip install requests  
	pip install cx_Oracle  
	pip install gunicorn




