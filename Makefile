format:
	black app
	isort app

lint:
	black --check app
	isort --check-only app
	flake8 app


dev-run:
	docker compose up -d --build
	sleep 5
	docker compose exec testwork_bot python3 load_test_data.py /sampleDB

run:
	docker build --target=production .
	# для запуска "production" локально
	docker compose -f docker-compose.yml up -d --build
	sleep 5
	docker compose exec testwork_bot python3 load_test_data.py /sampleDB
