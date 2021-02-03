.PHONY: init start restart

init:
	docker network create rabbit_net
	cd rabbitmq && docker-compose up -d

start:
	docker network create rabbit_net
	docker-compose up --build -d

restart:
	docker-compose down
	sleep 2
	docker-compose up --build -d
