#!/bin/bash

set -e

cd ~ || exit

pip install vmraid-bench

bench init vmraid-bench --skip-assets --python "$(which python)" --vmraid-path "${GITHUB_WORKSPACE}"

mkdir ~/vmraid-bench/sites/test_site
cp "${GITHUB_WORKSPACE}/.github/helper/consumer_db/$DB.json" ~/vmraid-bench/sites/test_site/site_config.json

if [ "$TYPE" == "server" ]; then
      mkdir ~/vmraid-bench/sites/test_site_producer;
      cp "${GITHUB_WORKSPACE}/.github/helper/producer_db/$DB.json" ~/vmraid-bench/sites/test_site_producer/site_config.json;
fi

if [ "$DB" == "mariadb" ];then
      mysql --host 127.0.0.1 --port 3306 -u root -e "SET GLOBAL character_set_server = 'utf8mb4'";
      mysql --host 127.0.0.1 --port 3306 -u root -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'";

      mysql --host 127.0.0.1 --port 3306 -u root -e "CREATE DATABASE test_vmraid_consumer";
      mysql --host 127.0.0.1 --port 3306 -u root -e "CREATE USER 'test_vmraid_consumer'@'localhost' IDENTIFIED BY 'test_vmraid_consumer'";
      mysql --host 127.0.0.1 --port 3306 -u root -e "GRANT ALL PRIVILEGES ON \`test_vmraid_consumer\`.* TO 'test_vmraid_consumer'@'localhost'";

      mysql --host 127.0.0.1 --port 3306 -u root -e "CREATE DATABASE test_vmraid_producer";
      mysql --host 127.0.0.1 --port 3306 -u root -e "CREATE USER 'test_vmraid_producer'@'localhost' IDENTIFIED BY 'test_vmraid_producer'";
      mysql --host 127.0.0.1 --port 3306 -u root -e "GRANT ALL PRIVILEGES ON \`test_vmraid_producer\`.* TO 'test_vmraid_producer'@'localhost'";

      mysql --host 127.0.0.1 --port 3306 -u root -e "UPDATE mysql.user SET Password=PASSWORD('travis') WHERE User='root'";
      mysql --host 127.0.0.1 --port 3306 -u root -e "FLUSH PRIVILEGES";
    fi

if [ "$DB" == "postgres" ];then
    echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE DATABASE test_vmraid_consumer" -U postgres;
    echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE USER test_vmraid_consumer WITH PASSWORD 'test_vmraid'" -U postgres;

    echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE DATABASE test_vmraid_producer" -U postgres;
    echo "travis" | psql -h 127.0.0.1 -p 5432 -c "CREATE USER test_vmraid_producer WITH PASSWORD 'test_vmraid'" -U postgres;
fi

cd ./vmraid-bench || exit

sed -i 's/^watch:/# watch:/g' Procfile
sed -i 's/^schedule:/# schedule:/g' Procfile

if [ "$TYPE" == "server" ]; then sed -i 's/^socketio:/# socketio:/g' Procfile; fi
if [ "$TYPE" == "server" ]; then sed -i 's/^redis_socketio:/# redis_socketio:/g' Procfile; fi

if [ "$TYPE" == "ui" ]; then bench setup requirements --node; fi

# install node-sass which is required for website theme test
cd ./apps/vmraid || exit
yarn add node-sass@4.13.1
cd ../..

bench start &
bench --site test_site reinstall --yes
if [ "$TYPE" == "server" ]; then bench --site test_site_producer reinstall --yes; fi
bench build --app vmraid