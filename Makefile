.PHONY: build test run-integration shell clean

IMAGE_NAME=arthashree:local

build:
	docker build -t $(IMAGE_NAME) .

test:
	docker run --rm -v $(PWD):/home/arthuser/app -w /home/arthuser/app $(IMAGE_NAME) python -m pytest -q

run-integration:
	docker run --rm -v $(PWD):/home/arthuser/app -w /home/arthuser/app $(IMAGE_NAME) python tools/ci_integration.py ${SAMPLE:-sample1.csv}

shell:
	docker run --rm -it -v $(PWD):/home/arthuser/app -w /home/arthuser/app $(IMAGE_NAME) /bin/bash

clean:
	rm -rf tools/artifacts
