# Assignment
## SQL Performance (1 student) STČ
Create configurations (docker-compose) for single DB Postgres (all containers share one DB) 10 pts, multiple DBs Postgres (each container has its own DB) 5 pts, for Cocroach 5 pts, and for Yugabyte 5 pts.
Use the structure of the prepared gql queries (see other projects, json descriptions) and implement replicable measurements with statistical evaluation (jupyter notebooks, python scripts, aiohttp library) 10 b, include graphical outputs (e.g. bar charts) 10 b, determine means and variances. Compare performance. Confirm/refute the hypothesis that a random variable has a Gaussian distribution 10 pts.



# Postgres single DB
All containers connect to a single postgres DB.

## Connect to PGAdmin
    user: root
    password: root
    host: postgres
    port: 5432
    maintenance database: postgres

## Usage
Compose the yml file `docker-compose-p.yml`

Wait for every container to connect to postgres DB

Make sure that `apollo` is running

Run `request_queries.py`.

Run `generate_statistics.py`

## Troubleshoot
If `apollo` not running because of a gql container error, remove this container from `SERVICES` in `apollo` in `docker-compose-p.yml` and restart apollo. You might need to repeat this process multiple times because some gql containers depend on each other with model definitions.


# Postgres multi DB
Each container connects to its own postgres DB

## Connect to PGAdmin
    user: root
    password: root
    host: postgres_[container_name]
    port: 5432
    maintenance database: postgres

## Usage
Compose the yml file `docker-compose-pm.yml`

Wait for every container to connect to postgres DB

Make sure that `apollo` is running

Run `request_queries.py`

Run `generate_statistics.py`

## Troubleshoot
If `apollo` not running because of a gql container error, remove this container from `SERVICES` in `apollo` in `docker-compose-p.yml` and restart apollo. You might need to repeat this process multiple times because some gql containers depend on each other with model definitions.


# Yugabyte
Creates a 3 node Yugabyte cluster. `yugabyte-init` initializes the cluster by creating the databese `data` that each container assumes the existance of. All containers then connect to this cluster. Has it's own GUI at `localhost:15433`.

## Connect to PGAdmin
    user: yugabyte
    password: yugabyte
    host: yugabyte1
    port: 5433
    maintenance database: postgres

## Usage
Compose the yml file `docker-compose-y.yml`

Wait for every container to connect to postgres DB

Make sure that `apollo` is running - restart if needed

Run `request_queries.py`

Run `generate_statistics.py`

## Troubleshoot
After you compose the yml file, all containers will try to connect to the cluster at once. Wait for containers to stop or stop them manually and run them one by one by hand. Make sure that each container connects to Yugabyte before starting the next one. You might need to run the containers in the same order as in `docker-compose-y.yml`.

If `apollo` not running because of a gql container error, remove this container from `SERVICES` in `apollo` in `docker-compose-y.yml` and restart apollo. You might need to repeat this process multiple times because some gql containers depend on each other with model definitions.

## Handy Yugabyte commands
Check the cluster status:
    
    docker exec -it yugabyte yugabyted status

Open YSQL shell:

    docker exec -it yugabyte1 bash -c '/home/yugabyte/bin/ysqlsh --echo-queries --host yugabyte1'


Set cluster replication factor --rf=3:

    docker exec -it yugabyte1 /bin/bash -c './bin/yugabyted configure data_placement --rf=3'


## CockroachDB
Creates a 3 node CockroachDB cluster that runs in insecure mode. Experimental - I was not able to connect uois gql containers to this cluster with the same connection string as Postgres and Yugabyte. By adding few lines of code to `gql_ug` in `DBDefinitions/__init__.py/ComposeConnecttionString()` and adding an environmental variable `IS_COCKROACH`, we were able to connect successfully. Has it's own GUI at `localhost:8080`.

Code change in gql_ug:
```python
def ComposeConnectionString():
    """Odvozuje connectionString z promennych prostredi (nebo z Docker Envs, coz je fakticky totez).
    Lze predelat na napr. konfiguracni file.
    """
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "example")
    database = os.environ.get("POSTGRES_DB", "data")
    hostWithPort = os.environ.get("POSTGRES_HOST", "localhost:5432")

    isCockroach = os.environ.get("IS_COCKROACH", "False")
    
    # if statement added to change connection string
    if isCockroach == "False":
        driver = "postgresql+asyncpg"  # "postgresql+psycopg2"
        connectionstring = f"{driver}://{user}:{password}@{hostWithPort}/{database}"

    if isCockroach == "True":
        driver = "cockroachdb+asyncpg"  # "postgresql+psycopg2"
        connectionstring = f"{driver}://{user}:{password}@{hostWithPort}/{database}?ssl=disable"

    print(connectionstring)

    return connectionstring
```

## Connect to PGAdmin
By default cockroach does not have a password in insecure mode

    user: root
    password: 
    host: roach1
    port: 26257
    maintenance database: defaultdb
    in parameters: disable ssl mode

## Usage
Compose the yml file `docker-compose-c.yml`

Run a one time init command to initialize the cluster

    docker exec -it roach1 ./cockroach --host=roach1:26357 init --insecure

Restart every container (only gql_ug for now) and make sure it connects to the cluster

Restart `apollo` and make sure it's running

Run `request_queries.py`

Run `generate_statistics.py`

## Handy Cockroach commands
Check the startup parameters of the cluster:

    docker exec -it roach1 grep 'node starting' cockroach-data/logs/cockroach.log -A 11 

Open SQL shell (roach1):

    docker exec -it roach1 ./cockroach sql --host=roach2:26258 --insecure

Test the cluster with a mock workload form 5 minutes. Run in container roach1:

    cockroach workload run movr --duration=5m 

Add a node. Make sure to change --name, --network, "--label com.stack={stack}" (specifies the docker stack), --join correct nodes (containers) in network:

    docker run -d \
    --name roach4 \
    --network sql_performance_roachnet \
    -v roach4:/mnt/cockroach/cockroach-data \
    --label com.stack=sql_performance \
    cockroachdb/cockroach:latest start --insecure --join=roach1,roach2,roach3,roach4

# request_queries.py
Script for sending queries (saved in `gql_queries.json`) to the project DB through apollo (header set by default in `send_queries()`) and saves their times into a folder. A file will be generated for each container and will be saved in said folder. In `main()` set number of queries and a name of the folder you want to save them to. `generate_statistics.py` assumes that each folder will be named `queries_times_[DB_type_name]`.

# generate_statistics.py
Scrip for generating statistics from data generated by `request_queries.py`. In `main()` edit paths to folders containing files with times. This script generates a `statistics.docx` file for each folder, containing statistics of times in that folder only. Another file called `overall_stats.docx` will be generated in root folder, which will hold the overall statistics for all folders. The script assumes that each folder holds times for one DB type and that it's named `queries_times_[DB_type_name]`.

# Handy SQL commands to test the DBs
create database

    CREATE DATABASE data; 

create table

    CREATE TABLE data.Employees (
        EmployeeID INT PRIMARY KEY,
        FirstName VARCHAR(50),
        LastName VARCHAR(50),
        Department VARCHAR(50),
        Salary DECIMAL(10, 2)
    );

insert data

    INSERT INTO Employees (EmployeeID, FirstName, LastName, Department, Salary) 
    VALUES (1, 'John', 'Doe', 'Sales', 50000.00);

    INSERT INTO Employees (EmployeeID, FirstName, LastName, Department, Salary) 
    VALUES (2, 'Jane', 'Smith', 'HR', 60000.00);

select data

    SELECT * FROM Employees;

update data

    UPDATE Employees
    SET Salary = 55000.00
    WHERE EmployeeID = 1;

delete data

    DELETE FROM Employees
    WHERE EmployeeID = 2;

filter data

    SELECT * FROM Employees
    WHERE Department = 'Sales';

aggregate data

    SELECT Department, AVG(Salary) as AverageSalary
    FROM Employees
    GROUP BY Department;

join tables

    CREATE TABLE Projects (
        ProjectID INT PRIMARY KEY,
        ProjectName VARCHAR(50),
        EmployeeID INT,
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
    );

    SELECT Employees.FirstName, Employees.LastName, Projects.ProjectName
    FROM Employees
    INNER JOIN Projects
    ON Employees.EmployeeID = Projects.EmployeeID;