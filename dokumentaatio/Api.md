# Rajapinnat (/api/)


###(/request)

Vastaanottaa uusia pyynt�j� jsonissa. Esimerkkej� k�ytetyst� json-rakenteesta l�ytyy testikansiosta mocks.py tiedostosta.

###(/download?<pyynn�n_id>)

Vastaanottaa ilmoituksen latauksen valmistumisesta pyynn�lle.

###(/newcount?<k�ytt�j�tunnisteen_id>)

Kertoo annetun k�ytt�j�tunnisteen k�sittelem�tt�m�t pyynn�t lukum��r�n� (html-bodyssa).

###(/{ZABBIX_STATUS_SUB_DIR})

Kertoo pyha-palvelun tilan html-status koodina.


Mik�li rajapinta pyyt�� tunnusta ja salasanaa. 
Ne ovat PYHA_API_USER:PYHA_API_PASSWORD ymp�rist�muuttujien arvot.