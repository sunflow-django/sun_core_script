#!/bin/bash
set -a
source ../.env
set +a

cat <<EOF > set_priviledge_on_test_db.sql
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\`;
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE_TEST}\`;

GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE_TEST}\`.* TO '${MYSQL_USER}'@'%';

FLUSH PRIVILEGES;
EOF
