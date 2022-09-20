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
