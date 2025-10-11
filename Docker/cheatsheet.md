# Complete Docker Command Cheat Sheet

## Container Lifecycle Commands

### docker run
Creates and starts a new container from an image.
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
docker run -d nginx                    # Run container in detached mode
docker run -it ubuntu bash             # Run interactively with terminal
docker run -p 8080:80 nginx            # Map port 8080 (host) to 80 (container)
docker run --name myapp nginx          # Assign custom name
docker run -v /host/path:/container/path  # Mount volume
docker run -e VAR=value nginx          # Set environment variable
docker run --rm nginx                  # Auto-remove container when stopped
```

### docker start
Starts one or more stopped containers.
```bash
docker start [OPTIONS] CONTAINER [CONTAINER...]
docker start mycontainer               # Start a stopped container
docker start -a mycontainer            # Start and attach to container
docker start -i mycontainer            # Start with interactive mode
```

### docker stop
Stops one or more running containers gracefully (sends SIGTERM).
```bash
docker stop [OPTIONS] CONTAINER [CONTAINER...]
docker stop mycontainer                # Stop a container
docker stop $(docker ps -q)            # Stop all running containers
docker stop -t 30 mycontainer          # Wait 30 seconds before force stop
```

### docker restart
Restarts one or more containers.
```bash
docker restart [OPTIONS] CONTAINER [CONTAINER...]
docker restart mycontainer             # Restart a container
```

### docker pause
Pauses all processes within a container.
```bash
docker pause CONTAINER [CONTAINER...]
docker pause mycontainer               # Pause container processes
```

### docker unpause
Unpauses all processes within a container.
```bash
docker unpause CONTAINER [CONTAINER...]
docker unpause mycontainer             # Resume paused container
```

### docker kill
Forces a container to stop immediately (sends SIGKILL).
```bash
docker kill [OPTIONS] CONTAINER [CONTAINER...]
docker kill mycontainer                # Force kill a container
docker kill -s SIGINT mycontainer      # Send specific signal
```

### docker rm
Removes one or more stopped containers.
```bash
docker rm [OPTIONS] CONTAINER [CONTAINER...]
docker rm mycontainer                  # Remove a stopped container
docker rm -f mycontainer               # Force remove running container
docker rm $(docker ps -aq)             # Remove all stopped containers
docker rm -v mycontainer               # Remove container and its volumes
```

### docker rename
Renames a container.
```bash
docker rename CONTAINER NEW_NAME
docker rename oldname newname          # Rename a container
```

## Container Information Commands

### docker ps
Lists running containers.
```bash
docker ps [OPTIONS]
docker ps                              # Show running containers
docker ps -a                           # Show all containers (running and stopped)
docker ps -q                           # Show only container IDs
docker ps -s                           # Show container sizes
docker ps --filter "status=exited"     # Filter by status
docker ps --format "table {{.Names}}\t{{.Status}}"  # Custom format
docker ps -n 5                         # Show last 5 containers
```

### docker logs
Fetches logs from a container.
```bash
docker logs [OPTIONS] CONTAINER
docker logs mycontainer                # View container logs
docker logs -f mycontainer             # Follow log output (live)
docker logs --tail 100 mycontainer     # Show last 100 lines
docker logs --since 1h mycontainer     # Show logs from last hour
docker logs -t mycontainer             # Show timestamps
```

### docker inspect
Returns detailed information about a container or image.
```bash
docker inspect [OPTIONS] CONTAINER|IMAGE
docker inspect mycontainer             # Get detailed container info (JSON)
docker inspect --format='{{.State.Running}}' mycontainer  # Get specific info
```

### docker top
Displays running processes in a container.
```bash
docker top CONTAINER [ps OPTIONS]
docker top mycontainer                 # Show processes in container
```

### docker stats
Displays live resource usage statistics.
```bash
docker stats [OPTIONS] [CONTAINER...]
docker stats                           # Show stats for all running containers
docker stats mycontainer               # Show stats for specific container
docker stats --no-stream               # Display stats once without streaming
```

### docker port
Lists port mappings for a container.
```bash
docker port CONTAINER [PRIVATE_PORT[/PROTO]]
docker port mycontainer                # Show all port mappings
docker port mycontainer 80             # Show mapping for specific port
```

## Image Commands

### docker pull
Downloads an image from a registry.
```bash
docker pull [OPTIONS] NAME[:TAG|@DIGEST]
docker pull nginx                      # Pull latest nginx image
docker pull nginx:1.21                 # Pull specific version
docker pull ubuntu:20.04               # Pull Ubuntu 20.04
```

### docker images
Lists all locally stored images.
```bash
docker images [OPTIONS]
docker images                          # List all images
docker images -a                       # Show all images (including intermediates)
docker images -q                       # Show only image IDs
docker images --filter "dangling=true" # Show untagged images
```

### docker rmi
Removes one or more images.
```bash
docker rmi [OPTIONS] IMAGE [IMAGE...]
docker rmi nginx                       # Remove an image
docker rmi -f nginx                    # Force remove an image
docker rmi $(docker images -q)         # Remove all images
```

### docker build
Builds an image from a Dockerfile.
```bash
docker build [OPTIONS] PATH | URL
docker build -t myapp:1.0 .            # Build image with tag
docker build --no-cache -t myapp .     # Build without cache
docker build -f Dockerfile.dev .       # Use specific Dockerfile
```

### docker tag
Creates a tag for an image.
```bash
docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]
docker tag myapp:1.0 myapp:latest      # Tag an image
docker tag myapp myregistry.com/myapp  # Tag for registry
```

### docker push
Uploads an image to a registry.
```bash
docker push [OPTIONS] NAME[:TAG]
docker push myregistry.com/myapp:1.0   # Push image to registry
```

### docker history
Shows the history of an image.
```bash
docker history [OPTIONS] IMAGE
docker history nginx                   # Show image layer history
```

### docker save
Saves an image to a tar archive.
```bash
docker save [OPTIONS] IMAGE [IMAGE...]
docker save -o myapp.tar myapp:1.0     # Save image to file
```

### docker load
Loads an image from a tar archive.
```bash
docker load [OPTIONS]
docker load -i myapp.tar               # Load image from file
```

## Container Interaction Commands

### docker exec
Executes a command in a running container.
```bash
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
docker exec -it mycontainer bash       # Open bash shell in container
docker exec mycontainer ls /app        # Run command in container
docker exec -u root mycontainer bash   # Execute as specific user
```

### docker attach
Attaches to a running container's main process.
```bash
docker attach [OPTIONS] CONTAINER
docker attach mycontainer              # Attach to container
```

### docker cp
Copies files between container and host.
```bash
docker cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH
docker cp [OPTIONS] SRC_PATH CONTAINER:DEST_PATH
docker cp mycontainer:/app/file.txt .  # Copy from container to host
docker cp ./file.txt mycontainer:/app  # Copy from host to container
```

### docker diff
Shows changes to container's filesystem.
```bash
docker diff CONTAINER
docker diff mycontainer                # Show filesystem changes
```

### docker commit
Creates a new image from container's changes.
```bash
docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]
docker commit mycontainer myapp:2.0    # Create image from container
```

### docker export
Exports container's filesystem as tar archive.
```bash
docker export [OPTIONS] CONTAINER
docker export mycontainer > backup.tar # Export container filesystem
```

### docker import
Creates image from tarball.
```bash
docker import [OPTIONS] file|URL [REPOSITORY[:TAG]]
docker import backup.tar myapp:restored # Import from tarball
```

## Network Commands

### docker network ls
Lists all networks.
```bash
docker network ls                      # List all networks
```

### docker network create
Creates a new network.
```bash
docker network create [OPTIONS] NETWORK
docker network create mynetwork        # Create bridge network
docker network create --driver bridge mynet  # Create with specific driver
```

### docker network connect
Connects a container to a network.
```bash
docker network connect [OPTIONS] NETWORK CONTAINER
docker network connect mynetwork mycontainer  # Connect container to network
```

### docker network disconnect
Disconnects a container from a network.
```bash
docker network disconnect [OPTIONS] NETWORK CONTAINER
docker network disconnect mynetwork mycontainer  # Disconnect from network
```

### docker network rm
Removes one or more networks.
```bash
docker network rm NETWORK [NETWORK...]
docker network rm mynetwork            # Remove a network
```

### docker network inspect
Displays detailed network information.
```bash
docker network inspect NETWORK
docker network inspect mynetwork       # Inspect network details
```

## Volume Commands

### docker volume ls
Lists all volumes.
```bash
docker volume ls                       # List all volumes
docker volume ls -q                    # List volume names only
```

### docker volume create
Creates a new volume.
```bash
docker volume create [OPTIONS] [VOLUME]
docker volume create myvolume          # Create a volume
```

### docker volume rm
Removes one or more volumes.
```bash
docker volume rm VOLUME [VOLUME...]
docker volume rm myvolume              # Remove a volume
```

### docker volume inspect
Displays detailed volume information.
```bash
docker volume inspect VOLUME [VOLUME...]
docker volume inspect myvolume         # Inspect volume details
```

### docker volume prune
Removes all unused volumes.
```bash
docker volume prune [OPTIONS]
docker volume prune                    # Remove unused volumes
docker volume prune -f                 # Force remove without prompt
```

## System Commands

### docker version
Shows Docker version information.
```bash
docker version                         # Display Docker version
```

### docker info
Displays system-wide information.
```bash
docker info                            # Show Docker system info
```

### docker system df
Shows Docker disk usage.
```bash
docker system df                       # Show disk usage
docker system df -v                    # Verbose disk usage
```

### docker system prune
Removes unused data (containers, networks, images).
```bash
docker system prune [OPTIONS]
docker system prune                    # Remove unused data
docker system prune -a                 # Remove all unused images too
docker system prune -f                 # Force without confirmation
docker system prune --volumes          # Also remove unused volumes
```

### docker login
Logs in to a Docker registry.
```bash
docker login [OPTIONS] [SERVER]
docker login                           # Login to Docker Hub
docker login myregistry.com            # Login to private registry
```

### docker logout
Logs out from a Docker registry.
```bash
docker logout [SERVER]
docker logout                          # Logout from Docker Hub
```

## Docker Compose Commands

### docker-compose up
Creates and starts containers defined in docker-compose.yml.
```bash
docker-compose up                      # Start services
docker-compose up -d                   # Start in detached mode
docker-compose up --build              # Rebuild images before starting
```

### docker-compose down
Stops and removes containers, networks.
```bash
docker-compose down                    # Stop and remove containers
docker-compose down -v                 # Also remove volumes
```

### docker-compose ps
Lists containers for a Compose project.
```bash
docker-compose ps                      # Show compose containers
```

### docker-compose logs
Views output from containers.
```bash
docker-compose logs                    # View logs
docker-compose logs -f                 # Follow log output
docker-compose logs service_name       # Logs for specific service
```

### docker-compose exec
Executes command in running service container.
```bash
docker-compose exec service_name bash  # Open bash in service
```

### docker-compose build
Builds or rebuilds services.
```bash
docker-compose build                   # Build all services
docker-compose build service_name      # Build specific service
```

### docker-compose restart
Restarts services.
```bash
docker-compose restart                 # Restart all services
docker-compose restart service_name    # Restart specific service
```

### docker-compose stop
Stops running services.
```bash
docker-compose stop                    # Stop all services
```

### docker-compose start
Starts existing service containers.
```bash
docker-compose start                   # Start services
```

## Useful Docker Run Options

- `-d, --detach`: Run container in background
- `-it`: Interactive terminal
- `-p, --publish`: Publish container port to host
- `-v, --volume`: Bind mount a volume
- `-e, --env`: Set environment variables
- `--name`: Assign container name
- `--rm`: Automatically remove container when stopped
- `--network`: Connect to network
- `-u, --user`: Username or UID
- `--restart`: Restart policy (no, on-failure, always, unless-stopped)
- `-w, --workdir`: Working directory inside container
- `--memory`: Memory limit
- `--cpus`: Number of CPUs
- `--env-file`: Read environment variables from file

## Quick Tips

**Clean up everything:**
```bash
docker system prune -a --volumes -f
```

**Stop and remove all containers:**
```bash
docker stop $(docker ps -aq) && docker rm $(docker ps -aq)
```

**Remove all images:**
```bash
docker rmi $(docker images -q) -f
```

**View container IP address:**
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name
```

**Follow logs of multiple containers:**
```bash
docker logs -f container1 & docker logs -f container2
```