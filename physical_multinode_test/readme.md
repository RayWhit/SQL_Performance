## Test two machines with a simple db-container setup
1. Run docker-compose-test-db.yml on the first machine and make sure postgres is running
2. Edit the environment variable `POSTGRES_HOST=IP_ADDRESS:PORT` to match the first machine
3. Run docker-compose-test-container.yml on the second machine. Make sure that all containters (gql_ug) are running. If apollo has exited, restart it manually.

### Notes
- no need to run containers in `network_mode: host` (host mode), port forwarding is sufficient 