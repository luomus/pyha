N�m� p�ivitys ohjeet on kirjoitettu Ubuntulle, ja et�n� k�ytett�v�lle Oracle tietokantapalvelimelle.
Ohjeet edellytt�v�t ett� kaikki k�ytt�j�kohtaiset (ei sudo) komennot suoritetaan pyha-j�rjestelm�� varten luodulla omalla k�ytt�j�ll�. 
Esim. pyha k�ytt�j� ja pyha ryhm�.

(12.6.2019) Merkitt�vimm�t p�ivityskomentoja vaativat muutokset ovat:
- Tietokantamuutokset.
- EI ymp�rist�muuttuja muutoksia.
- Uusi asennettava python kirjasto (schedule)
- Kielimuutokset.
- Staattiset verkko elementit.


## 0 - Alku

Siirry terminaalissa pyha git-projektin juurihakemistoon.


## 1 - Automatisoitu p�ivitt�minen

Aja terminaalissa:

	bash updateserver.sh
	

## 2 - Manuaalinen p�ivitt�minen

Tutki updateserver.sh:n sis�ll� olevat komennot /tai

Avaa python virtuaaliymp�rist�:

	source env/bin/activate
	
Aseta ymp�rist�muuttujat ymp�rist��n.
	
Aja seuraavat komennot:

	pip install -r Requirements.txt (Python kirjastot)
	
	ja/tai
	
	pip3 install -r Requirements.txt (Python kirjastot)
	
	rm -r project/static (staattiset verkko elementit)
	
    python project/manage.py collectstatic (staattiset verkko elementit)
	
    python project/manage.py makemigrations (Tietokantamuutokset)
	
    python project/manage.py migrate (Tietokantamuutokset)
	
    python project/manage.py createcachetable (Tietokantamuutokset)
	
    python project/manage.py makemessages -a (Kielimuutokset)
	
    python project/manage.py compilemessages (Kielimuutokset)
	
	













