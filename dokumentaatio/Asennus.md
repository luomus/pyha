## 1 - Kehitysymp�rist�n pystytt�minen

N�m� ohjeet on kirjoitettu Ubuntulle, ja et�n� k�ytett�v�lle Oracle tietokantapalvelimelle.

Luo kansio, mihin aiot asentaa ymp�rist�n esim.

	mkdir ~/pyyntojenhallinta

Siirry kansioon

	cd ~/pyyntojenhallinta

Asenna *Oracle Instant Client* ja *Instant Client SDK* seuraavasti. Lataa ne [t��lt�](http://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html). Pura arkistot (ne purkautuvat samaan kansioon). Sen j�lkeen lis�� tiedostoon `~/.bashrc` seuraavan malliset rivit:

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

Mik�li automaattinen asennus onnistui, voit ylitt�� kohdan 3.

## 3 - Asentaminen k�sin

Aluksi asenna seuraavat packaget `sudo apt-get install`in avulla:

	build-essential  
	python3-dev  
	python-pip  
	python3-pip  
	python-virtualenv

Seuraava rivi luo uuden virtuaalienv-ymp�rist�n python 3:lla omaan kansioon env:

	virtualenv -p python3 env

Avaa virtuaaliymp�rist�:

	source env/bin/activate

Asenna virtuaaliymp�rist��n j�rjestelm�n vaatimat ohjelmat:

	pip install django
	pip install requests  
	pip install cx_Oracle  
	pip install gunicorn




