# Zadani
SQL Performance (1 student) STČ Whitehead
    Vytvořte konfigurace (docker-compose) pro single database Postgres (všechny kontejnery sdílí jednu databázi) 0 b, multiple databases Postgres (každý kontejner má svoji vlastní databázi) 5 b, pro Cocroach 5 b a pro Yugabyte 5 b.
    Využijte strukturu připravovaných gql dotazů (viz ostatní projekty, json popisy) a realizujte replikovatelná měření se statistickým vyhodnocením (jupyter notebooks, python scripts, knihovna aiohttp) 10 b, součástí statistického vyhodnocení jsou grafické výstupy (např. sloupcové grafy) 10 b, stanovte střední hodnoty a rozptyly. Srovnejte výkon. Potvrďte / vyvraťte hypotézu, že náhodná proměnná má Gaussovo rozdělení 10 b.

## Subukoly
zprovozneni databazi postgres
Cocroach - sestavit v docker file - kontejner
Yugabyte - sestavit v docker file - kontejner
do denicku jak vse instaluju

clusterova databaze - ???
multiple docker compose files

na githubu denicek a docker compose pro vsechny


dokumentace yugabyte, cockroach - 5433 implicitni heslo

connect cockroach to pgadmin

find out how to connect cockroachdb database with pgadmin (pgadmin sees the server at this point)

make sql evolution communicate with cockroach and yugabyte




pridat Apollo do kontejneru, dopsat do pole vsechny kontejnery (services), pak davam pozadavek na apollo

3 nodova databaze




Udelat statistiku, prumernej cas, rozptyl u vsech kontejneru na postgres, yugabyte





questions


multiple databases
    does every pg database need to have its own UG -> no



new questions
    what to do with cockroach - show container? - test UG - kavic
    multi cluster Yuga & Roach DBs or just single? - single cluster multi node
    what does frontend do - 
        which db should it use? should it have it's own db in multidb compose? - not important now - don't worry about it
        what is salt? - for security - not important now

pojede cockroach pokud nebude insecure a v connection string ssl=disable bude oddelan
    asi ne - pokud neni insecure sql pozadavek vypada takto:
        postgresql://root@localhost:26257?sslcert=certs%2Fclient.root.crt&sslkey=certs%2Fclient.root.key&sslmode=verify-full&sslrootcert=certs%2Fca.crt





# Casovy harmonogram
9. 10. 2023 zveřejnění harmonogramu prací na projektu (z pohledu programátora), určení repository url (nebo alespoň root např. https://github.com/hrbolek)
16. 10. 2023 projektový den, Prezentace porozumění projektu, jeho struktura, deskripce entit („live dokumentace v GQL API – Voyager / GraphiQL“)
27. 11. 2023 projektový den, Prezentace alespoň RU operací
15. 1. 2024 projektový den, Alfa verze
21. 1. 2024 uzavření projektu
22. 1. 2024 počátek zkouškového období,
?. 3. 2024 konec zkouškového období.

# Notes
Notes for getting all containers set up correctly.

## Postgres
Use container ip address as host.

### Done
Runs
can connect to pgadmin
created database "data"




## Cockroachdb

Inabiliity to connect to CockroachDB via asyncpg
    https://github.com/sqlalchemy/sqlalchemy/issues/6825

After running dokcer compose, run: 

    docker exec -it roach1 ./cockroach --host=roach1:26357 init --insecure

for one-time initialization. Even if you add or remove a node you don't have to run this again as long as the database is running.


Use 

    docker exec -it roach1 grep 'node starting' cockroach-data/logs/cockroach.log -A 11 

to check the startup parameters of the cluster.



Use 

    cockroach workload run movr --duration=5m 

in node1 container for a test of the cluster.



Use

    docker exec -it roach1 ./cockroach sql --host=roach2:26258 --insecure

for sql queries.



To add a node, run: 

    docker run -d \
    --name roach4 \
    --network sql_performance_roachnet \
    -v roach4:/mnt/cockroach/cockroach-data \
    --label com.stack=sql_performance \
    cockroachdb/cockroach:v23.1.11 start --insecure --join=roach1,roach2,roach3,roach4

Make sure to change --name, --network, --label specifies the docker stack "--label com.stack={stack}", --join correct nodes (containers) in network


use container ip or container name as host
host roach1
port 26257
maintenance database defaultdb
username root
in parameters disable ssl mode



Start SQL shell (roach1):
    
    docker exec -it roach1 ./cockroach sql --host=roach2:26258 --insecure


### Done
Runs
Connects to pgadmin (sort of)



## yugabyte

Connect to yb-tserver-n1
Use container ip address as host.
default name: yugabyte
default password: yugabyte
port: 5433:5433

Check the cluster status:
    
    docker exec -it yugabyte yugabyted status

To open YSQL shell:

    docker exec -it yugabyte bash -c '/home/yugabyte/bin/ysqlsh --echo-queries --host yugabyte'
    docker exec -it yugabyte1 bash -c '/home/yugabyte/bin/ysqlsh --echo-queries --host yugabyte1'


Set replication factor:
    docker exec -it yugabyte1 /bin/bash -c './bin/yugabyted configure data_placement --rf=3'


### Done
Runs
can connect to pgadmin
communicates with gql evolution



# test SQL
## create database

CREATE DATABASE data; 

## create table
CREATE TABLE data.Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Department VARCHAR(50),
    Salary DECIMAL(10, 2)
);

## insert data
INSERT INTO Employees (EmployeeID, FirstName, LastName, Department, Salary) 
VALUES (1, 'John', 'Doe', 'Sales', 50000.00);

INSERT INTO Employees (EmployeeID, FirstName, LastName, Department, Salary) 
VALUES (2, 'Jane', 'Smith', 'HR', 60000.00);

## selecting data
SELECT * FROM Employees;

## updating data
UPDATE Employees
SET Salary = 55000.00
WHERE EmployeeID = 1;

## deleting data
DELETE FROM Employees
WHERE EmployeeID = 2;

## filtering data
SELECT * FROM Employees
WHERE Department = 'Sales';

## aggregating data
SELECT Department, AVG(Salary) as AverageSalary
FROM Employees
GROUP BY Department;

## joining tables
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