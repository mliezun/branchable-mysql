# Branchable MySQL

Create branches on your MySQL databases to have multiple dev environments.

When teams start to grow, having a single dev environment becomes an issue. People start stepping on each others toes.
A common problem is that two people want to apply incompatible migrations on the database. That problem is impossible 
to fix if folks are working on parallel branches.
If we can have a database for each branch of a project, that will remove much of the pain of having multiple devs applying
changes to the db.


## Usage

Create a file like the one located in `examples/docker-compose.yml`

```yaml
version: "3"

services:
  mysql:
    image: mliezun/branchable-mysql
    platform: linux/amd64
    privileged: true
    restart: always
    volumes:
      - appdata:/app/

volumes:
  appdata:
```

Execute `docker compose up` to initialize the container.

Then you can access handful scripts inside the container.


### Connect to the `base` database inside the container

```shell
$ docker compose exec mysql mysql -uroot -h127.0.0.1 --skip-password -P33061
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.0.30-0ubuntu0.22.04.1 (Ubuntu)

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```


### Create branch from database

```shell
$ docker compose exec mysql /app/scripts/create_branch.sh base feature/abc
{"branch_name":"feature/abc", "base_branch":"base", "port":33062}
```

To be able to use the new branch connect using the new port: 

```shell
$ docker compose exec mysql mysql -uroot -h127.0.0.1 --skip-password -P33062
```

### List branches

```shell
$ docker compose exec mysql /app/scripts/list_branches.sh
[{"branch_name":"base"}, {"branch_name":"feature/abc"}]
```

### Delete branch from database (will drop all the data)

```shell
$ docker compose exec mysql /app/scripts/delete_branch.sh feature/abc
{"branch_name":"feature/abc"}
```

