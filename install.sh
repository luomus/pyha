virtualenv -p python3 env

env/bin/pip install -r Requirements.txt

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
KEYS=(DJANGO_SECRET_KEY "Hash salt used by django" \
		PYHA_LISTEN_PORT "Port listened by pyyntojenhallinta" \
		EMAIL_LINK_URL "Path included in emails linking to certain pyyntojenhallinta request ex. https://fmnh-ws-test.it.helsinki.fi/pyha/request/" \
		LAJI_AUTH_URL 0 \
		LAJI_ETL_FILE_DOWNLOAD_URL 0 \
		TRIPLESTORE_URL 0 \
		TRIPLESTORE_USER 0 \
		TRIPLESTORE_PASSWORD 0 \
		PDF_API_URL 0 \
		PDF_API_USER 0 \
		PDF_API_PASSWORD 0 \
		APILAJIFI_URL 0 \
		APILAJIFI_TOKEN 0 \
		LAJI_AUTH_TARGET 0 \
		PYHA_API_USER 0 \
		PYHA_API_PASSWORD 0 \
		OBSERVATION_LINK_PREFIX 0 \
		OFFICIAL_OBSERVATION_LINK_PREFIX 0 \
		DB_NAME 0 \
		DB_USER 0 \
		DB_PASSWORD 0 \
		PID 0 \
		)
		
# get length of an array
arraylength=${#KEYS[@]}

echo "Environmental variables will be stored in the services/pyha.service file"

# use for loop to read all values and indexes
for (( i=1; i<${arraylength}+1; i+=2 ));
do
  if [[ 0 != ${KEYS[$i]} ]] 
  then 
	echo
	echo ${KEYS[$i]}
  fi
  echo
  read -p ${KEYS[$i-1]}":" ${KEYS[$i-1]}_var
done



for (( i=1; i<${arraylength}+1; i+=2 ));
do
  LINE=${KEYS[$i-1]}_var
  CONTENT=$CONTENT"export "${KEYS[$i-1]}"='"${!LINE}"'"$'\r'
done
CONTENT=$CONTENT"export DB_ENGINE='django.db.backends.oracle'"

echo $CONTENT > env_variables.sh

echo "Created env_variables.sh file"

SERVICECONTENT=$SERVICECONTENT\
"[Unit]"$'\r'\
"Description=pyha"$'\r'\
"Requires=pyha.socket"$'\r'\
"After=network.target"$'\r'\
$'\r'\
"[Service]"$'\r'\
"PIDFile=/run/pyha/pid"$'\r'\
"WorkingDirectory="DIR$'\r'$'\r'

for (( i=1; i<${arraylength}+1; i+=2 ));
do
  LINE=${KEYS[$i-1]}_var
  SERVICECONTENT=$SERVICECONTENT"Environment='"${KEYS[$i-1]}"="${!LINE}"'"$'\r'
done
SERVICECONTENT=$SERVICECONTENT"Environment='DB_ENGINE=django.db.backends.oracle'"

SERVICECONTENT=$SERVICECONTENT\
"ExecStart="DIR"/env/bin/gunicorn --threads 3 --timeout 600 --pid /run/pyha/pid project.wsgi"$'\r'\
"ExecReload=/bin/kill -s HUP $MAINPID"$'\r'\
"ExecStop=/bin/kill -s TERM $MAINPID"$'\r'\
"PrivateTmp=true"$'\r'\

mkdir services
echo $SERVICECONTENT > services/pyha.service

echo "Created services/pyha.service file"

SOCKETCONTENT=$SOCKETCONTENT\
"[Unit]"$'\r'\
"Description=pyha socket"$'\r'\
$'\r'\
"[Socket]"$'\r'\
"ListenStream=/run/pyha/socket"$'\r'\
$'\r'\
"[Install]"$'\r'\
"WantedBy=sockets.target"$'\r'\

echo "Created services/pyha.socket file"

PIDCONTENT=$PIDCONTENT\
PID
echo "Created services/pyha.pid file"
. updateserver.sh
echo "Installation has finished"