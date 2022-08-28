docker build -t backend ./django
docker build -t nginx ./react-ui
docker-compose up