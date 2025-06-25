docker compose down -v --remove-orphans
docker container prune -f

sudo rm -r -f clickhouse/clickhouse1/data/ clickhouse/clickhouse2/data/
docker compose down -v
docker volume prune
docker volume rm $(docker volume ls -q)
docker system prune -a --volumes
docker image prune -a -f
docker volume prune -f
docker network prune -f
docker system prune -a --volumes -f
