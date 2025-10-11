# Docker Run Command Labs

---

### Lab 1: Basic Web Server Deployment

#### Scenario

Your company needs a quick static website for testing. Deploy an Nginx web server accessible on port 8080.

#### Given Data

- **Image name:** nginx
- **Container port:** 80
- **Host port:** 8080
- **Mode:** Detached (background)

#### Your Task

Write the `docker run` command to deploy the Nginx web server according to the specifications above.

---

### Lab 2: Interactive Ubuntu Environment


#### Scenario

You need a temporary Ubuntu environment to test bash scripts without affecting your host machine.

#### Given Data

- **Image name:** ubuntu
- **Mode:** Interactive with terminal
- **Command:** bash
- **Container name:** test-ubuntu

#### Your Task

Write the `docker run` command to create an interactive Ubuntu container with the specifications above.

---

### Lab 3: Environment Variables Configuration


#### Scenario

Deploy a MySQL database with custom root password and database name for your development environment.

#### Given Data

- **Image name:** mysql:8.0
- **Root password:** DevPass123!
- **Database name:** testdb
- **Port:** 3306
- **Container name:** dev-mysql

#### Your Task

Write the `docker run` command to deploy MySQL with the specified environment variables and configuration.

**Hint:** MySQL requires specific environment variables:
- `MYSQL_ROOT_PASSWORD` for the root password
- `MYSQL_DATABASE` for the initial database name

---

### Lab 4: Automatic Container Cleanup


#### Scenario

Run temporary containers for testing that automatically remove themselves after execution to keep your system clean.

#### Given Data

- **Image name:** ubuntu
- **Mode:** Interactive
- **Cleanup:** Automatic removal on exit

#### Your Task

Write the `docker run` command that will automatically remove the container after you exit from it.

**Hint:** There's a specific flag that tells Docker to automatically remove the container when it stops.

---

### Lab 5: Restart Policy Configuration


#### Scenario

Deploy a Redis cache server that automatically restarts if it crashes or when the server reboots.

#### Given Data

- **Image name:** redis
- **Port:** 6379
- **Restart policy:** always
- **Container name:** cache-server

#### Your Task

Write the `docker run` command to deploy Redis with an automatic restart policy.

**Hint:** Docker has a `--restart` flag that accepts different policies:
- `no` (default)
- `on-failure`
- `always`
- `unless-stopped`

---


### Lab 6: Jenkins Admin Password Recovery


#### Scenario

Deploy Jenkins CI/CD server and retrieve the initial admin password for first-time setup. Your DevOps team needs to configure Jenkins but doesn't have the password yet.

#### Given Data

- **Image name:** jenkins/jenkins:lts
- **Web port:** 8080
- **Agent port:** 50000
- **Password file location:** /var/jenkins_home/secrets/initialAdminPassword
- **Container name:** jenkins-server

#### Your Task

1. Write the `docker run` command to deploy Jenkins with the specified configuration
2. Retrieve the initial admin password from the container

**Hint:** You'll need to:
- Map both ports (web interface and agent)
- Run in detached mode
- Use `docker exec` to access the password file after the container is running



### Lab 7: Multi-Port Web Application

#### Scenario

Deploy a Grafana monitoring dashboard that needs multiple ports exposed: the main web interface and a metrics endpoint. Your monitoring team needs both ports accessible from the host.

#### Given Data

- **Image name:** grafana/grafana:latest
- **Web UI port:** 3000 (map to host port 3000)
- **Metrics port:** 9090 (map to host port 9090)
- **Admin user:** admin
- **Admin password:** MonitorPass123
- **Container name:** grafana-monitor
- **Mode:** Detached

#### Your Task

Write the `docker run` command to deploy Grafana with multiple port mappings and custom admin credentials.

**Hint:** You can use multiple `-p` flags for different port mappings. Grafana uses `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` environment variables.

---
