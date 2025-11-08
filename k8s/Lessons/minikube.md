# Minikube Complete Tutorial

## Table of Contents
1. [What is Minikube?](#what-is-minikube)
2. [Minikube Architecture](#minikube-architecture)
3. [Installation](#installation)
4. [Working with Docker Driver](#working-with-docker-driver)
5. [Essential Commands](#essential-commands)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

---

## What is Minikube?

Minikube is a tool that runs a single-node Kubernetes cluster locally on your computer. It's perfect for:
- Learning Kubernetes
- Local development
- Testing Kubernetes applications
- CI/CD pipelines

### Key Features
- Runs on Linux, macOS, and Windows
- Multiple driver support (Docker, VirtualBox, KVM, etc.)
- Multiple Kubernetes versions support
- Add-ons for common Kubernetes features
- LoadBalancer emulation
- Multiple cluster support

---

## Minikube Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Host Machine                          │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Minikube CLI (minikube)                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Docker Driver                         │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │         Docker Container (minikube)             │   │ │
│  │  │                                                 │   │ │
│  │  │  ┌──────────────────────────────────────────┐   │   │ │
│  │  │  │    Kubernetes Control Plane              │   │   │ │
│  │  │  │  • kube-apiserver                        │   │   │ │
│  │  │  │  • kube-controller-manager               │   │   │ │
│  │  │  │  • kube-scheduler                        │   │   │ │
│  │  │  │  • etcd                                  │   │   │ │
│  │  │  └──────────────────────────────────────────┘   │   │ │
│  │  │                                                 │   │ │
│  │  │  ┌──────────────────────────────────────────┐   │   │ │
│  │  │  │    Kubernetes Node                       │   │   │ │
│  │  │  │  • kubelet                               │   │   │ │
│  │  │  │  • kube-proxy                            │   │   │ │
│  │  │  │  • Container Runtime (containerd/docker) │   │   │ │
│  │  │  └──────────────────────────────────────────┘   │   │ │
│  │  │                                                 │   │ │
│  │  │  ┌──────────────────────────────────────────┐   │   │ │
│  │  │  │    Your Pods & Applications              │   │   │ │
│  │  │  │  • Pod 1                                 │   │   │ │
│  │  │  │  • Pod 2                                 │   │   │ │
│  │  │  │  • Pod 3                                 │   │   │ │
│  │  │  └──────────────────────────────────────────┘   │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              kubectl CLI                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Components

1. **Host Machine**: Your local computer
2. **Minikube CLI**: Command-line tool to manage Minikube
3. **Driver**: Runs the Kubernetes cluster (Docker, VirtualBox, etc.)
4. **Control Plane**: Manages the Kubernetes cluster
5. **Node**: Worker node that runs your applications
6. **Pods**: Your containerized applications

---

## Installation

### Prerequisites
- Docker Desktop (for Docker driver)
- 2 CPUs or more
- 2GB of free memory
- 20GB of free disk space
- Internet connection

### Install Minikube

#### Linux
```bash
# Download and install
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

#### macOS
```bash
# Using Homebrew
brew install minikube

# Or using curl
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

#### Windows
```powershell
# Using Chocolatey
choco install minikube

# Or download installer from:
# https://storage.googleapis.com/minikube/releases/latest/minikube-installer.exe

# Verify installation
minikube version
```

### Install kubectl
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# macOS
brew install kubectl

# Windows
choco install kubernetes-cli

# Verify
kubectl version --client
```

---

## Working with Docker Driver

### Why Use Docker Driver?

 **Advantages:**
- No VM overhead (faster)
- Better resource utilization
- Easier to use
- No need for hypervisor
- Works on all platforms

 **Limitations:**
- No support for `minikube mount`
- Some networking features limited
- LoadBalancer type services need tunnel

### Start Minikube with Docker Driver

```bash
# Start with Docker driver (default on most systems)
minikube start --driver=docker

# Start with specific configuration
minikube start --driver=docker \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --kubernetes-version=v1.28.0

# Make Docker the default driver
minikube config set driver docker
```

### Docker Driver Architecture

```
Host Machine
    │
    ├── Docker Engine
    │   │
    │   └── Minikube Container (minikube)
    │       │
    │       ├── Kubernetes Control Plane
    │       │   ├── API Server (port 8443)
    │       │   ├── Controller Manager
    │       │   ├── Scheduler
    │       │   └── etcd
    │       │
    │       ├── Kubernetes Node
    │       │   ├── kubelet
    │       │   ├── kube-proxy
    │       │   └── containerd
    │       │
    │       └── Your Applications (Pods)
    │
    └── kubectl → connects to API Server
```

### Verify Docker Driver

```bash
# Check Docker containers
docker ps | grep minikube

# SSH into Minikube container
minikube ssh

# Inside Minikube container
docker ps  # See Kubernetes containers
exit
```

---

## Essential Commands

### Cluster Management

```bash
# Start cluster
minikube start

# Start with specific driver
minikube start --driver=docker

# Stop cluster (preserves state)
minikube stop

# Delete cluster
minikube delete

# Delete all clusters
minikube delete --all

# Pause cluster (saves resources)
minikube pause

# Unpause cluster
minikube unpause

# Get cluster status
minikube status

# Get cluster IP
minikube ip

# SSH into cluster
minikube ssh
```

### Multiple Clusters

```bash
# Create named cluster
minikube start -p cluster1

# Create second cluster
minikube start -p cluster2

# List all clusters
minikube profile list

# Switch between clusters
minikube profile cluster1
kubectl get nodes

minikube profile cluster2
kubectl get nodes

# Delete specific cluster
minikube delete -p cluster1
```

### Configuration

```bash
# Set default driver
minikube config set driver docker

# Set default CPU count
minikube config set cpus 4

# Set default memory
minikube config set memory 8192

# View all config
minikube config view

# Unset config
minikube config unset driver
```

### Addons

```bash
# List all addons
minikube addons list

# Enable addon
minikube addons enable dashboard
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable registry

# Disable addon
minikube addons disable dashboard

# Check addon status
minikube addons list | grep enabled
```

### Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard

# Get dashboard URL only
minikube dashboard --url

# Access in background
minikube dashboard &
```

### Service Access

```bash
# Get service URL
minikube service <service-name>

# Get service URL without opening browser
minikube service <service-name> --url

# List all service URLs
minikube service list

# Example
kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0
kubectl expose deployment hello-minikube --type=NodePort --port=8080
minikube service hello-minikube
```

### LoadBalancer Services (Tunnel)

```bash
# Start tunnel (requires separate terminal)
minikube tunnel

# Now LoadBalancer services get external IPs
kubectl get svc

# Example
kubectl create deployment web --image=nginx
kubectl expose deployment web --type=LoadBalancer --port=80
minikube tunnel  # In another terminal
kubectl get svc web  # Should show EXTERNAL-IP
```

### Docker Integration

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Now docker commands use Minikube's Docker
docker ps
docker images

# Build and use images directly
docker build -t my-app:v1 .
kubectl run my-app --image=my-app:v1 --image-pull-policy=Never

# Revert to host Docker
eval $(minikube docker-env -u)
```

### Registry

```bash
# Enable local registry
minikube addons enable registry

# Get registry address
minikube service registry -n kube-system --url

# Push image to Minikube registry
docker tag my-image:v1 localhost:5000/my-image:v1
docker push localhost:5000/my-image:v1

# Use image in pod
kubectl run my-app --image=localhost:5000/my-image:v1
```

### Logs and Debugging

```bash
# View Minikube logs
minikube logs

# Follow logs
minikube logs -f

# Last 50 lines
minikube logs --length=50

# View specific component logs
minikube logs --file=kubelet

# SSH and check system
minikube ssh
systemctl status kubelet
journalctl -u kubelet
```

### Node Management

```bash
# Add node (multi-node cluster)
minikube node add

# List nodes
minikube node list

# Delete node
minikube node delete <node-name>

# Start multi-node cluster
minikube start --nodes 3
```

### Version Management

```bash
# List available Kubernetes versions
minikube update-check

# Start with specific version
minikube start --kubernetes-version=v1.28.0

# Upgrade cluster
minikube delete
minikube start --kubernetes-version=v1.29.0
```

### Resource Management

```bash
# Update resources
minikube start --cpus=4 --memory=8192

# Check current resources
docker stats $(docker ps -q -f name=minikube)

# View Minikube system info
minikube ssh
free -h
df -h
```

---

## Advanced Usage

### Custom Kubernetes Configuration

```bash
# Start with custom API server flags
minikube start --extra-config=apiserver.enable-admission-plugins="PodSecurityPolicy"

# Start with custom kubelet config
minikube start --extra-config=kubelet.max-pods=100

# Multiple custom configs
minikube start \
  --extra-config=apiserver.enable-admission-plugins="NamespaceLifecycle,LimitRanger" \
  --extra-config=kubelet.max-pods=110 \
  --extra-config=scheduler.address=0.0.0.0
```

### Mounting Host Directories

```bash
# Mount host directory (not supported with Docker driver)
# Use this workaround instead:

# 1. Copy files into Minikube
minikube cp /path/on/host/file.txt /path/in/minikube/file.txt

# 2. Or use kubectl cp after creating pod
kubectl cp /path/on/host/file.txt pod-name:/path/in/pod/

# 3. Use ConfigMaps for small files
kubectl create configmap my-config --from-file=/path/to/file
```

### Network Configuration

```bash
# Start with custom subnet
minikube start --subnet=192.168.100.0/24

# Expose specific ports
minikube start --ports=8443:8443

# Custom DNS
minikube start --dns-domain=my.cluster.local
```

### Cache Management

```bash
# Pre-download images
minikube cache add nginx:latest
minikube cache add redis:alpine

# List cached images
minikube cache list

# Delete cached image
minikube cache delete nginx:latest

# Reload cached images
minikube cache reload
```

### Ingress Setup

```bash
# Enable Ingress addon
minikube addons enable ingress

# Verify Ingress controller
kubectl get pods -n ingress-nginx

# Create example deployment and service
kubectl create deployment web --image=nginx
kubectl expose deployment web --port=80

# Create Ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: hello-world.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
EOF

# Add to /etc/hosts
echo "$(minikube ip) hello-world.local" | sudo tee -a /etc/hosts

# Test
curl http://hello-world.local
```

### Metrics Server

```bash
# Enable metrics-server
minikube addons enable metrics-server

# Wait for metrics to be available (takes 1-2 minutes)
kubectl top nodes
kubectl top pods
```

### Persistent Volumes

```bash
# Create PersistentVolume and PersistentVolumeClaim
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF

# Use in Pod
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
        - mountPath: "/usr/share/nginx/html"
          name: storage
  volumes:
    - name: storage
      persistentVolumeClaim:
        claimName: my-pvc
EOF

# Data persists even after pod deletion
kubectl exec mypod -- sh -c "echo 'Hello' > /usr/share/nginx/html/index.html"
kubectl delete pod mypod
kubectl apply -f pod.yaml
kubectl exec mypod -- cat /usr/share/nginx/html/index.html
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Minikube Won't Start

```bash
# Check Docker is running
docker ps

# Check logs
minikube logs

# Delete and restart
minikube delete
minikube start --driver=docker

# Check for port conflicts
sudo netstat -tulpn | grep :8443

# Start with verbose output
minikube start --driver=docker -v=7
```

#### 2. Docker Driver Issues

```bash
# Verify Docker permissions
docker ps

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker
sudo systemctl restart docker  # Linux
# or restart Docker Desktop on Mac/Windows

# Clean Docker system
docker system prune -a
```

#### 3. Insufficient Resources

```bash
# Check current allocation
docker stats $(docker ps -q -f name=minikube)

# Increase resources
minikube delete
minikube start --cpus=4 --memory=8192 --disk-size=40g
```

#### 4. Networking Issues

```bash
# Check cluster IP
minikube ip

# Test connectivity
ping $(minikube ip)

# Restart tunnel
minikube tunnel

# Check service connectivity
minikube service list
minikube service <service-name> --url
```

#### 5. Image Pull Errors

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build locally
docker build -t myapp:v1 .

# Use with Never pull policy
kubectl run myapp --image=myapp:v1 --image-pull-policy=Never

# Or enable registry addon
minikube addons enable registry
```

#### 6. Cluster Not Responding

```bash
# Check status
minikube status

# Restart cluster
minikube stop
minikube start

# If still not working, delete and recreate
minikube delete
minikube start
```

#### 7. Addon Issues

```bash
# List addon status
minikube addons list

# Disable and re-enable
minikube addons disable dashboard
minikube addons enable dashboard

# Check addon pods
kubectl get pods -n kube-system
kubectl get pods -n ingress-nginx
```

### Diagnostic Commands

```bash
# Full cluster info
minikube status
kubectl cluster-info
kubectl get nodes
kubectl get pods -A

# Check Minikube version
minikube version
kubectl version

# System logs
minikube logs --length=100

# SSH and investigate
minikube ssh
docker ps
systemctl status kubelet
journalctl -u kubelet -f

# Check resource usage
kubectl top nodes
kubectl top pods -A

# Network debugging
minikube ssh
ping 8.8.8.8
curl google.com
```

### Reset Everything

```bash
# Complete reset
minikube delete --all --purge
rm -rf ~/.minikube
rm -rf ~/.kube

# Reinstall (if needed)
# ... reinstall minikube and kubectl

# Start fresh
minikube start --driver=docker
```

---

## Quick Reference Cheat Sheet

### Cluster Operations
```bash
minikube start                    # Start cluster
minikube stop                     # Stop cluster
minikube delete                   # Delete cluster
minikube status                   # Check status
minikube pause                    # Pause cluster
minikube unpause                  # Unpause cluster
minikube ip                       # Get cluster IP
```

### Addons
```bash
minikube addons list              # List all addons
minikube addons enable <name>     # Enable addon
minikube addons disable <name>    # Disable addon
```

### Services
```bash
minikube service <name>           # Open service in browser
minikube service <name> --url     # Get service URL
minikube service list             # List all services
minikube tunnel                   # Start LoadBalancer tunnel
```

### Docker Integration
```bash
eval $(minikube docker-env)       # Use Minikube's Docker
eval $(minikube docker-env -u)    # Revert to host Docker
minikube cache add <image>        # Cache image
```

### Debugging
```bash
minikube logs                     # View logs
minikube ssh                      # SSH into cluster
minikube dashboard                # Open dashboard
kubectl get pods -A               # View all pods
```

### Configuration
```bash
minikube config set driver docker # Set default driver
minikube config set cpus 4        # Set default CPUs
minikube config set memory 8192   # Set default memory
minikube config view              # View configuration
```

---

## Best Practices

1. **Resource Allocation**: Start with sufficient resources (4 CPUs, 8GB RAM minimum)
2. **Use Docker Driver**: Fastest and most compatible on modern systems
3. **Enable Metrics**: `minikube addons enable metrics-server`
4. **Use Local Registry**: Enable registry addon for faster image access
5. **Persistent Storage**: Be aware that data persists in the Minikube container
6. **Regular Updates**: Keep Minikube and kubectl updated
7. **Clean Up**: Delete unused clusters to free resources
8. **Version Consistency**: Use matching kubectl and Kubernetes versions

---

## Useful Resources

- **Official Documentation**: https://minikube.sigs.k8s.io/
- **GitHub Repository**: https://github.com/kubernetes/minikube
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Docker Documentation**: https://docs.docker.com/

---

## Complete Example Workflow

```bash
# 1. Start Minikube
minikube start --driver=docker --cpus=4 --memory=8192

# 2. Enable addons
minikube addons enable metrics-server
minikube addons enable ingress

# 3. Use Minikube's Docker
eval $(minikube docker-env)

# 4. Create application
kubectl create deployment web --image=nginx --replicas=3

# 5. Expose service
kubectl expose deployment web --type=LoadBalancer --port=80

# 6. Access service (in new terminal)
minikube tunnel  # Keep running
kubectl get svc web  # Get EXTERNAL-IP

# 7. Test application
curl http://<EXTERNAL-IP>

# 8. Scale application
kubectl scale deployment web --replicas=5

# 9. Check metrics
kubectl top nodes
kubectl top pods

# 10. Clean up
kubectl delete deployment web
kubectl delete service web
minikube stop
```
