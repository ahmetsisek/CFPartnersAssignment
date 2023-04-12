## Purpose

This repo is developed to fulfill the requirements mentioned in the Home Task pdf file.

## Files & Folders

**jobs/scripts:** To keep Python scripts for the required job which is to bring some csv data with header or without header to a Delta Table.

**jobs/data/input:** To keep source csv files either with or without a header. A default file with header for Person data is initially there. Mapped as a volume in Docker compose file.

**jobs/data/output:** This folder which is initially not there will be created to keep the raw Delta files (in Parquet format or other). Mapped as a volume in Docker compose file.

**spark/conf:** Includes Spark defaults for the containers. Mapped as a volume in Docker compose file.

**spark/logs:** To keep log files. Mapped as a volume in Docker compose file.

**spark/work:** To keep Worker container log files. Mapped as a volume in Docker compose file.

**spark/Dockerfile:** To base Spark master and worker images with necessary library setup.

**docker-compose.yml:** To define services, volumes, networks for the Docker Application. 
Includes 4 services for the Spark application:
- *spark-master:* Master node
- *spark-worker:* Worker node
- *spark-history:* History server
- *my-pyspark-job:* Application server to trigger the job

# How to reproduce the environment and jobs:
Use `docker compose build` to initially build the services.
Use `docker compose up` and `docker compose down` to activate and deactivate containers.
The job (*IngestCSVToDelta.py*) takes 3 arguments: path to input files, path to write the output and header flag.
If the source files do not have a header, set the header flag (third argument) to ***false*** in docker compose file like:
`command: "/opt/spark/bin/spark-submit --packages io.delta:delta-core_2.12:1.2.1 --master spark://spark-master:7077 /app/IngestCSVToDelta.py /tmp/data/input /tmp/data/output false"` and rebuild.