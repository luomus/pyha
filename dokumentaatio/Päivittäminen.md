Nämä päivitys ohjeet on kirjoitettu Ubuntulle, ja etänä käytettävälle Oracle tietokantapalvelimelle.
Ohjeet edellyttävät että kaikki käyttäjäkohtaiset (ei sudo) komennot suoritetaan pyha-järjestelmää varten luodulla omalla käyttäjällä. 
Esim. pyha käyttäjä ja pyha ryhmä.

(12.6.2019) Merkittävimmät päivityskomentoja vaativat muutokset ovat:
- Tietokantamuutokset.
- EI ympäristömuuttuja muutoksia.
- Uusi asennettava python kirjasto (schedule)
- Kielimuutokset.
- Staattiset verkko elementit.


## 0 - Alku

Siirry terminaalissa pyha git-projektin juurihakemistoon.


## 1 - Automatisoitu päivittäminen

Aja terminaalissa:

	bash updateserver.sh
	

## 2 - Manuaalinen päivittäminen

Tutki updateserver.sh:n sisällä olevat komennot /tai

Avaa python virtuaaliympäristö:

	source env/bin/activate
	
Aseta ympäristömuuttujat ympäristöön.
	
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
	
	













