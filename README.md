# Pyha

## Finnish Biodiversity Information Facility (FinBIF) system for handling data requests

Links:
- [Documentation](docs/Documentation.md)
- [Installation instructions](docs/Asennus.md)
- [Upgrade instructions](docs/Update.md)

## Using docker

Prerequisites are docker and docker-compose installed on the running machine.

1. Follow the instructions to install [oracle instant client](oracle/README.md)
2. Add dev.env file with the environment variables in it
3. Run command `docker-compose up`
4. Open `http://localhost:8000`