cd  ../../..
set -a
source .env
set +a
mysql -h 127.0.0.1 -P 3306 -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" -e "SHOW GRANTS;"
