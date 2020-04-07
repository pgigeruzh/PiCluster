# Postgres Cluster on Docker Swarm

To run a postgres cluster on Docker Swarm, you first need to have a "Postgres" image. However, the official image does not support replication out of the box and commercial solutions such as Patroni/Citus couldn't be compiled on the Raspberry Pi. The only RPi-compatible image we found was a private open-source project from: https://github.com/sameersbn/docker-postgresql. You can either build it yourself or use our build: https://hub.docker.com/repository/docker/pgigeruzh/postgres

```bash
# Run Master on cluster1raspberry0
docker service create --name postgresmaster --network spark --publish 54320:5432 --constraint=node.hostname==cluster1raspberry0 --env PG_PASSWORD=password --env REPLICATION_USER=postgres --env REPLICATION_PASS=password pgigeruzh/postgres

# Run Slave1 on cluster1raspberry1
docker service create --name postgresslave1 --network spark --publish 54321:5432 --constraint=node.hostname==cluster1raspberry1 --env REPLICATION_MODE=slave --env REPLICATION_SSLMODE=prefer --env REPLICATION_HOST=postgresmaster --env REPLICATION_PORT=5432 --env REPLICATION_USER=postgres --env REPLICATION_PASS=password pgigeruzh/postgres

# Run Slave2 on cluster1raspberry2
docker service create --name postgresslave2 --network spark --publish 54322:5432 --constraint=node.hostname==cluster1raspberry2 --env REPLICATION_MODE=slave --env REPLICATION_SSLMODE=prefer --env REPLICATION_HOST=postgresmaster --env REPLICATION_PORT=5432 --env REPLICATION_USER=postgres --env REPLICATION_PASS=password pgigeruzh/postgres

# Run Slave3 on cluster1raspberry3
docker service create --name postgresslave3 --network spark --publish 54323:5432 --constraint=node.hostname==cluster1raspberry3 --env REPLICATION_MODE=slave --env REPLICATION_SSLMODE=prefer --env REPLICATION_HOST=postgresmaster --env REPLICATION_PORT=5432 --env REPLICATION_USER=postgres --env REPLICATION_PASS=password pgigeruzh/postgres
```

It has to be noted that the databases have to be constraint (--constraint=node.hostname) to a certain node because Docker Swarm doesn't move/share volumes accross nodes (see GlusterFS). For persistent storage, mount the local filesystem to /var/lib/postgresql.

To take advantage of the streaming replication, a load balancer can be added. [Pgpool](https://www.pgpool.net/) is a load balancer for Postgres and support automatic failovers in case a node dies. The documentation can be found here: https://github.com/pgigeruzh/pgpool