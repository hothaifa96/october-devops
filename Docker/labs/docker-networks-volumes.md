# Docker Volumes & Networks

Progressive Exercises from Easy to Extreme

---

## Exercise 1: Basic Named Volume

**Difficulty:** Easy

**Objective:** Understand persistent data with named volumes

### Task:

1. Create a named volume called `mydata`
2. Run an `nginx` container that uses this volume mounted at `/usr/share/nginx/html`
3. Create an `index.html` file in the volume with custom content
4. Stop and remove the container, then create a new one using the same volume
5. Verify your data persisted

**Remember:** nginx is accessible on port 80

---

## Exercise 2: Bind Mount Web Development

**Difficulty:** Easy

**Objective:** Use bind mounts for live development

### Task:

1. Create a local directory with a simple HTML file and a CSS file
2. Run an `nginx` container with a bind mount pointing your local directory to `/usr/share/nginx/html`
3. Modify the HTML file on your host machine
4. Verify changes appear immediately in the browser without restarting the container

**Challenge:** Make the container run on port 8080 of your host

---

## Exercise 3: Network Communication Between Containers

**Difficulty:** Medium

**Objective:** Connect two containers on a custom network

### Task:

1. Create a custom bridge network called `app-network`
2. Run a `mysql:8.0` container on this network with:
   - Container name: `mydb`
   - Environment variables for root password
   - A named volume for data persistence
3. Run an `adminer` (database management tool) container on the same network
4. Access adminer through your browser and connect to the mysql container using the container name as hostname

---

## Exercise 4: Volume Backup and Restore

**Difficulty:** Medium - Challenge

**Objective:** Learn to backup and restore volume data

### Task:

1. Create a named volume and run a `postgres:15` container with it
2. Use `docker exec` to create a database and table with some data
3. Write a bash/python script that:
   - Stops the postgres container
   - Creates a backup of the volume data to a tar file
   - Restarts the container
4. Delete the volume and container
5. Create a new volume and restore the data from your backup
6. Verify data integrity

**Deliverable:** A `backup.sh` and `restore.sh` script

---

## Exercise 5: Multi-Container Application with Shared Volume

**Difficulty:** Medium

**Objective:** Share data between containers using volumes

### Task:

1. Create a named volume called `shared-logs`
2. Run a container with `busybox` that writes the current timestamp to a file in the shared volume every 5 seconds (use a bash/sh loop)
3. Run an `nginx` container that mounts the same volume and serves the log file
4. Access the log file through nginx and watch it update

**Hint:** Use `tail -f` or configure nginx to serve the logs directory

---

## Exercise 6: Network Isolation Testing

**Difficulty:** Hard

**Objective:** Understand network isolation and security

### Task:

1. Create three custom bridge networks: `frontend`, `backend`, `database`
2. Run containers:
   - `nginx` connected to `frontend` only (name: web)
   - `python:3.9` connected to `frontend` and `backend` (name: api)
   - `redis` connected to `backend` and `database` (name: cache)
   - `postgres` connected to `database` only (name: db)
3. Test and document which containers can ping each other
4. Connect the API container to multiple networks and verify connectivity changes

**Deliverable:** Network diagram and connectivity test results

---

## Exercise 7: Read-Only Volumes and Security

**Difficulty:** Hard

**Objective:** Implement read-only mounts for security

### Task:

1. Create a Python script that reads configuration from a file and writes logs to another location
2. Run a `python:3.9` container with:
   - A read-only bind mount for the config file
   - A writable named volume for logs
   - A read-only mount for the Python script itself
3. Verify the application cannot modify the config file but can write logs
4. Try to modify the config from inside the container and document the behavior

**Deliverable:** Python script and documentation of read-only behavior

---

## Exercise 9: Inter-Network Communication with Port Mapping

**Difficulty:** Hard

**Objective:** Advanced networking with multiple networks and port exposure

### Task:

1. Create two networks: `public` and `private`
2. Run a `redis` container on the `private` network only
3. Run a `python:3.9` container connected to BOTH networks that:
   - Acts as a proxy/API between the networks
   - Exposes port 5000 to the host
   - Connects to redis on the private network
   - Serves HTTP requests on the public network
4. Write a Python Flask application that:
   - Receives HTTP POST requests with key-value pairs
   - Stores them in Redis
   - Retrieves them on GET requests
5. The redis container should NOT be directly accessible from the host

**Deliverable:** Python Flask app and documentation of the network architecture

---

## Exercise 10: Complete Application Stack with Volume Management

**Difficulty:** Extreme Challenge

**Objective:** Build a complete, production-like setup

Create a blogging platform with the following requirements:

### 1. Database Layer (network: db-net)

- `postgres:15` container with named volume for data
- Automated backup script that runs daily (simulate with a container)

### 2. Application Layer (networks: db-net, app-net)

- `wordpress:latest` container connected to both networks
- Bind mount for custom theme development
- Named volume for uploaded media

### 3. Reverse Proxy Layer (network: app-net)

- `nginx` container as reverse proxy
- Bind mount for custom nginx configuration
- SSL termination (self-signed certificate)

### 4. Monitoring (network: app-net)

- Container that monitors logs and saves analytics

### Requirements:

- Write a bash script that provisions the entire stack
- Implement health checks
- Document all volume mount points and their purposes
- Create a backup/restore strategy
- Network isolation: database should not be accessible from proxy layer

### Deliverable:

- Complete setup script
- Network and volume architecture diagram
- Backup/restore scripts
- Documentation

---