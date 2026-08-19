# Arthashree


## Running with Docker

Build the local image:

    make build

Run the integration runner inside the container (uses sample1.csv by default):

    make run-integration SAMPLE=sample1.csv

Open a shell inside the container:

    make shell

Using docker-compose:

    docker-compose up --build

Artifacts will be written to tools/artifacts/ in the repository root.
