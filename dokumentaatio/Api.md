# Rajapinnat (/api/)


###(/request)

Vastaanottaa uusia pyyntöjä jsonissa. Esimerkkejä käytetystä json-rakenteesta löytyy testikansiosta mocks.py tiedostosta.

###(/download?<pyynnön_id>)

Vastaanottaa ilmoituksen latauksen valmistumisesta pyynnölle.

###(/newcount?<käyttäjätunnisteen_id>)

Kertoo annetun käyttäjätunnisteen käsittelemättömät pyynnöt lukumääränä (html-bodyssa).

###(/{ZABBIX_STATUS_SUB_DIR})

Kertoo pyha-palvelun tilan html-status koodina.


Mikäli rajapinta pyytää tunnusta ja salasanaa. 
Ne ovat PYHA_API_USER:PYHA_API_PASSWORD ympäristömuuttujien arvot.