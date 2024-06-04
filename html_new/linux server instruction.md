# Linux Server Setup Documentation

## Connecting to the Server

Use any command window and following authentication to SSH into the Linux server we built for this project.


ssh your_firstname_all_lowercase@24.21.129.24


**Public IP:** 24.21.129.24

If you are working on the server, let me know and I will change the username to your name.

**Password:** 0000

## Log in to MariaDB (MariaDB is a better version of MySQL while the operation/commands are the same).

Log in to the MariaDB command line as the root user:

```bash
sudo mariadb -u root -p
```

### Create a Database and User

Inside the MariaDB prompt, create a database and a user with privileges:

#### Create a new database:

```sql
CREATE DATABASE your_db_name;
```

#### Create a new user and grant privileges (replace `remote_user`, `your_password`, and `your_db_name` with your own values):

```sql
GRANT ALL PRIVILEGES ON your_db_name.* TO 'remote_user'@'%' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
```

### Restart MariaDB

Restart the service to apply the changes:

```bash
sudo systemctl restart mariadb
```

### Test Connection

```bash
mysql -h server_ip -u remote_user -p
```

## MongoDB

### Start the MongoDB Service

```bash
sudo systemctl start mongod
```

### Check that MongoDB has started successfully

```bash
sudo systemctl status mongod
```

### Enable MongoDB to start on boot

```bash
sudo systemctl enable mongod
```

## Basic MongoDB Commands

Access the MongoDB shell:

```bash
mongo
```

Create a new database:

```mongodb
use myNewDB
```

Create a new collection and insert data:

```mongodb
db.myCollection.insert({"name": "John Doe", "age": 30})
```

Find data in a collection:

```mongodb
db.myCollection.find()
```

Update data:

```mongodb
db.myCollection.update({"name": "John Doe"}, {$set: {"age": 31}})
```

Delete data:

```mongodb
db.myCollection.remove({"name": "John Doe"})
```

## Basic Administration

View all databases:

```mongodb
show dbs
```

View the current database you're working in:

```mongodb
db
```

Switch between databases:

```mongodb
use anotherDB
```
```
