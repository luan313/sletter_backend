CONTAINER_NAME = sletter-backend
IMAGE_NAME = api_sletter

homolog_build:
	docker build -t $(IMAGE_NAME) .

homolog_up:
	docker run -d --name $(CONTAINER_NAME) -p 8080:8000 --env-file .env $(IMAGE_NAME)

homolog_down:
	docker rm -f $(CONTAINER_NAME) || true

homolog_hdown:
	docker rm -f -v $(CONTAINER_NAME) || true

homolog_logs:
	docker logs -f $(CONTAINER_NAME)

homolog_deployl:
	make homolog_down
	make homolog_build
	make homolog_up
	make homolog_logs

homolog_deploy:
	make homolog_down
	make homolog_build
	make homolog_up