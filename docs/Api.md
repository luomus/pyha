# Interfaces (/api/)


###(/request)

Receives new requests in json format. 
Examples of the json structure that is used can be found in the test folder in the mocks.py file.

###(/download?<request_id>)

Receives a notification when the download is complete for request_id.

###(/newcount?<user_id>)

Indicates the number of unprocessed requests (in the html body) for the given user_id.

###(/{ZABBIX_STATUS_SUB_DIR})

Indicates the status of the Pyha service as html status code.

The interface login (user id and password) is defined by the values of the PYHA_API_USER: PYHA_API_PASSWORD environment variables.