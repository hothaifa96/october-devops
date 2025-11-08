# Kubernetes Pods - Complete Tutorial

## Table of Contents
1. [What is a Pod?](#what-is-a-pod)
2. [Pod Architecture](#pod-architecture)
3. [How Pods Work](#how-pods-work)
4. [Dissecting Your Example](#dissecting-your-example)
6. [Pod Lifecycle](#pod-lifecycle)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)
9. [Hands-On Examples](#hands-on-examples)
10. [Troubleshooting](#troubleshooting)

---

## What is a Pod?

A **Pod** is the smallest deployable unit in Kubernetes. Think of it as a wrapper around one or more containers.

### Key Concepts

```
┌─────────────────────────────────────────────────────────┐
│                         POD                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Shared Network Namespace             │  │
│  │              (localhost, same IP)                 │  │
│  │  ┌─────────────────┐    ┌─────────────────┐       │  │
│  │  │   Container 1   │    │   Container 2   │       │  │
│  │  │   (nginx)       │    │   (sidecar)     │       │  │
│  │  │                 │    │                 │       │  │
│  │  │  Port: 80       │    │  Port: 9090     │       │  │
│  │  └─────────────────┘    └─────────────────┘       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Shared Storage Volumes               │  │
│  │  ┌─────────────┐  ┌─────────────┐                 │  │
│  │  │  Volume 1   │  │  Volume 2   │                 │  │
│  │  └─────────────┘  └─────────────┘                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Important Facts

✅ **Atomic Unit**: Pods are created and destroyed as a single unit
✅ **Shared Network**: All containers in a pod share the same IP address
✅ **Shared Storage**: Containers can share volumes
✅ **Ephemeral**: Pods are disposable and replaceable
✅ **Single Host**: All containers in a pod run on the same node
✅ **Local Communication**: Containers communicate via `localhost`

---

## Pod Architecture

### How Containers Share Resources in a Pod

```
Node (Physical/Virtual Machine)
│
├── Pod: my-app
│   │
│   ├── Pause Container (Infrastructure Container)
│   │   └── Creates network namespace
│   │       └── IP: 10.244.1.5
│   │
│   ├── Main Container (nginx)
│   │   ├── Shares network with pause container
│   │   ├── Can bind to port 80
│   │   └── Accessible at 10.244.1.5:80
│   │
│   ├── Sidecar Container (log-collector)
│   │   ├── Shares network with pause container
│   │   ├── Can access nginx via localhost:80
│   │   └── Can bind to different port (9090)
│   │
│   └── Shared Volumes
│       ├── /var/log (logs volume)
│       └── /app/config (config volume)
```

## How Pods Work

### Pod Creation Flow

```
1. User submits Pod YAML to API Server
   │
   ▼
2. API Server validates and stores in etcd
   │
   ▼
3. Scheduler assigns Pod to a Node
   │
   ▼
4. Kubelet on Node receives Pod assignment
   │
   ▼
5. Kubelet tells Container Runtime to:
   - Pull images
   - Create pause container
   - Create application containers
   - Set up networking
   - Mount volumes
   │
   ▼
6. Pod starts running
```

### Network Communication

```
┌──────────────────────────────────────────────────────────┐
│                        Cluster                           │
│                                                          │
│  ┌────────────────┐              ┌────────────────┐      │
│  │  Pod A         │              │  Pod B         │      │
│  │  IP: 10.1.1.5  │─────────────▶│  IP: 10.1.1.6  │      │
│  │                │  Direct IP   │                │      │
│  │  Container 1   │  routing     │  Container 1   │      │
│  │  Container 2   │              │  Container 2   │      │
│  └────────────────┘              └────────────────┘      │
│         │                                                │
│         │ localhost                                      │
│         ▼                                                │
│  Containers within same pod                              │
│  communicate via localhost                               │
└──────────────────────────────────────────────────────────┘
```

### Storage in Pods

```
Pod
│
├── Container 1
│   └── Mount: /app/data → Volume "shared-data"
│
├── Container 2
│   └── Mount: /logs/app → Volume "shared-data"
│
└── Volumes
    └── shared-data (EmptyDir)
        └── Data persists during pod lifetime
        └── Deleted when pod is deleted
```

---

## Dissecting Your Example

Let's tear apart your example line by line:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: default
  labels:
    app: nginx
spec:
  containers:
    - name: nginx-continer
      image: nginx
      ports:
        - containerPort: 80
```

### Line-by-Line Breakdown

#### 1. API Version
```yaml
apiVersion: v1
```
- **What it is**: Specifies which version of the Kubernetes API to use
- **For Pods**: Always use `v1` (stable since Kubernetes 1.0)
- **Why it matters**: Different API versions have different features
- **Other examples**: 
  - `apps/v1` for Deployments
  - `batch/v1` for Jobs
  - `networking.k8s.io/v1` for Ingress

#### 2. Kind
```yaml
kind: Pod
```
- **What it is**: The type of Kubernetes object you're creating
- **Options**: Pod, Deployment, Service, ConfigMap, Secret, etc.
- **Case-sensitive**: Must be exactly `Pod` (capital P)

#### 3. Metadata Section
```yaml
metadata:
  name: nginx-pod
  namespace: default
  labels:
    app: nginx
```

##### 3a. Name
```yaml
name: nginx-pod
```
- **What it is**: Unique identifier for this pod within the namespace
- **Rules**:
  - Must be unique within namespace
  - Lowercase alphanumeric characters, `-` or `.`
  - Must start and end with alphanumeric character
  - Max 253 characters
- **Examples**:
  - ✅ `nginx-pod`, `web-app-1`, `api.service`
  - ❌ `Nginx-Pod` (uppercase), `_nginx` (underscore), `-nginx` (starts with dash)

##### 3b. Namespace
```yaml
namespace: default
```
- **What it is**: Logical cluster partition for organizing resources
- **Default**: If omitted, uses `default` namespace
- **Common namespaces**:
  - `default`: Default namespace for resources
  - `kube-system`: Kubernetes system components
  - `kube-public`: Publicly accessible resources
  - `kube-node-lease`: Node heartbeat data
- **Best practice**: Create custom namespaces for projects
```bash
kubectl create namespace production
kubectl create namespace development
```

##### 3c. Labels
```yaml
labels:
  app: nginx
```
- **What it is**: Key-value pairs for organizing and selecting resources
- **Purpose**:
  - Organize resources
  - Select resources with label selectors
  - Group resources logically
- **Best practices**:
  ```yaml
  labels:
    app: nginx                    # Application name
    version: v1.0.0               # Version
    environment: production       # Environment
    tier: frontend                # Architecture tier
    team: platform                # Owning team
    component: web-server         # Component
  ```
- **Usage**:
  ```bash
  # Select pods by label
  kubectl get pods -l app=nginx
  kubectl get pods -l environment=production,tier=frontend
  
  # Delete pods by label
  kubectl delete pods -l app=nginx
  ```

#### 4. Spec Section
```yaml
spec:
  containers:
    - name: nginx-continer
      image: nginx
      ports:
        - containerPort: 80
```

##### 4a. Containers Array
```yaml
containers:
  - name: nginx-continer
```
- **What it is**: List of containers that run in this pod
- **Array syntax**: The `-` indicates this is a list item
- **Multiple containers**:
  ```yaml
  containers:
    - name: nginx        # Container 1
      image: nginx
    - name: sidecar      # Container 2
      image: busybox
  ```

##### 4b. Container Name
```yaml
name: nginx-continer
```
- **What it is**: Name of the container within the pod
- **Must be unique**: Within the pod (not cluster-wide)
- **Used for**:
  - Logs: `kubectl logs nginx-pod -c nginx-continer`
  - Exec: `kubectl exec nginx-pod -c nginx-continer -- ls`
  - Identifying container in multi-container pods
- **Note**: Your example has a typo - should be `nginx-container`

##### 4c. Image
```yaml
image: nginx
```
- **What it is**: Docker image to run in this container
- **Format**: `[registry/][namespace/]image[:tag]`
- **Examples**:
  ```yaml
  image: nginx                          # nginx:latest from Docker Hub
  image: nginx:1.25.3                   # Specific version
  image: gcr.io/my-project/my-app:v1    # Google Container Registry
  image: my-registry.com/app:latest     # Private registry
  image: docker.io/library/nginx:alpine # Full format
  ```
- **Best practice**: Always specify exact version tag
  ```yaml
  # ❌ Bad - unpredictable
  image: nginx
  
  # ✅ Good - predictable
  image: nginx:1.25.3
  ```

##### 4d. Ports
```yaml
ports:
  - containerPort: 80
```
- **What it is**: Ports that the container exposes
- **Important**: This is **documentation only**, not enforcement
  - Container can listen on any port
  - This just informs Kubernetes which ports are in use
- **Full format**:
  ```yaml
  ports:
    - name: http          # Name for the port (optional)
      containerPort: 80   # Port container listens on
      protocol: TCP       # TCP or UDP (default: TCP)
      hostPort: 8080      # Port on node (rarely used)
  ```

---


## Pod Lifecycle

### Pod Phase States

```
┌──────────┐
│ Pending  │  Pod accepted but not running yet
└────┬─────┘  (downloading images, scheduling)
     │
     ▼
┌──────────┐
│ Running  │  At least one container is running
└────┬─────┘  or starting or restarting
     │
     ├──────▶ ┌───────────┐
     │        │ Succeeded │  All containers terminated successfully
     │        └───────────┘  (for Jobs, batch tasks)
     │
     └──────▶ ┌───────────┐
              │  Failed   │  At least one container failed
              └───────────┘  (exit code != 0)
```

### Container States

```
┌──────────┐
│ Waiting  │  Container is not running
└────┬─────┘  (pulling image, waiting for resources)
     │
     ▼
┌──────────┐
│ Running  │  Container is executing
└────┬─────┘
     │
     ▼
┌────────────┐
│ Terminated │  Container finished execution
└────────────┘  (success or failure)
```

### Detailed Lifecycle Example

```bash
# 1. Create pod
kubectl apply -f pod.yaml
# Status: Pending

# 2. Scheduler assigns to node
# Status: Pending → ContainerCreating

# 3. Kubelet pulls image
# Status: ContainerCreating

# 4. Container starts
# Status: Running

# 5. Liveness probe fails 3 times
# Container restarts

# 6. After restart limit exceeded
# Status: CrashLoopBackOff

# 7. Delete pod
kubectl delete pod my-pod
# Status: Terminating

# 8. PreStop hook executes
# Grace period countdown (30s default)

# 9. SIGTERM sent to containers
# Wait for graceful shutdown

# 10. If still running after grace period
# SIGKILL sent

# 11. Pod removed
```

### Check Pod Lifecycle

```bash
# View pod status
kubectl get pod nginx-pod

# Detailed pod info
kubectl describe pod nginx-pod

# Watch pod status changes
kubectl get pod nginx-pod -w

# View pod events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check container status
kubectl get pod nginx-pod -o jsonpath='{.status.containerStatuses[*].state}'

# View pod phase
kubectl get pod nginx-pod -o jsonpath='{.status.phase}'
```

---

## Best Practices

### 1. Always Specify Resource Requests and Limits

```yaml
#  Bad - No resource limits
containers:
  - name: nginx
    image: nginx

#  Good - Resource limits defined
containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
```

**Why?**
- Prevents one pod from consuming all node resources
- Helps scheduler make better placement decisions
- Enables cluster autoscaling

### 2. Use Specific Image Tags

```yaml
#  Bad - Uses latest
image: nginx

#  Bad - Unpredictable
image: nginx:latest

#  Good - Specific version
image: nginx:1.25.3

#  Better - Specific digest
image: nginx@sha256:a1b2c3d4...
```

**Why?**
- Reproducible deployments
- Prevents unexpected changes
- Easier rollback

### 3. Implement Health Checks

```yaml
#  Always implement health checks
containers:
  - name: nginx
    image: nginx:1.25.3
    livenessProbe:
      httpGet:
        path: /healthz
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 80
      initialDelaySeconds: 10
      periodSeconds: 5
```

**Why?**
- Automatic restart of unhealthy containers
- Traffic only sent to ready containers
- Faster problem detection

### 4. Use Labels Effectively

```yaml
#  Good labeling strategy
metadata:
  labels:
    app: myapp              # Application name
    version: v1.0.0         # Version
    environment: production # Environment
    tier: frontend          # Architecture tier
    component: web-server   # Component
    managed-by: helm        # Management tool
```

**Why?**
- Easy resource selection
- Better organization
- Enables automation

### 5. Don't Run as Root

```yaml
#  Good - Non-root user
securityContext:
  runAsUser: 1000
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

**Why?**
- Security best practice
- Reduces attack surface
- Prevents privilege escalation

### 6. Use Namespace for Organization

```yaml
#  Good - Use specific namespace
metadata:
  name: nginx-pod
  namespace: production  # Not default
```

```bash
# Create namespaces
kubectl create namespace production
kubectl create namespace development
kubectl create namespace staging
```

**Why?**
- Logical separation
- Resource quotas per namespace
- Access control per namespace

### 7. Set Resource Quotas

```yaml
# ResourceQuota for namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "100"
```

### 8. Use ConfigMaps and Secrets

```yaml
#  Bad - Hardcoded values
env:
  - name: DB_HOST
    value: "mysql.prod.internal"
  - name: DB_PASSWORD
    value: "supersecret123"  # NEVER DO THIS!

#  Good - External configuration
env:
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: db-config
        key: host
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password
```

### 9. Use Init Containers for Dependencies

```yaml
#  Good - Wait for dependencies
initContainers:
  - name: wait-for-db
    image: busybox:1.35
    command: ['sh', '-c', 'until nc -z db-service 5432; do sleep 2; done']
```

### 10. Set Appropriate Termination Grace Period

```yaml
#  Good - Allow graceful shutdown
spec:
  terminationGracePeriodSeconds: 60  # Give app time to finish
  containers:
    - name: app
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 5"]  # Drain connections
```

---

## Common Patterns

### Pattern 1: Single Container Pod (Most Common)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: simple-app
  labels:
    app: simple-app
spec:
  containers:
    - name: app
      image: nginx:1.25.3
      ports:
        - containerPort: 80
      resources:
        requests:
          memory: "128Mi"
          cpu: "100m"
        limits:
          memory: "256Mi"
          cpu: "200m"
```

### Pattern 2: Sidecar Pattern

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-example
spec:
  containers:
    # Main application
    - name: app
      image: myapp:v1
      ports:
        - containerPort: 8080
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
    
    # Sidecar: Log collector
    - name: log-collector
      image: fluentd:v1
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
          readOnly: true
  
  volumes:
    - name: logs
      emptyDir: {}
```

**Use cases:**
- Log collection
- Metrics collection
- Service mesh proxies (Istio, Linkerd)
- Configuration synchronization

### Pattern 3: Ambassador Pattern

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ambassador-example
spec:
  containers:
    # Main application
    - name: app
      image: myapp:v1
      env:
        - name: REDIS_HOST
          value: "localhost"  # Connect via ambassador
        - name: REDIS_PORT
          value: "6379"
    
    # Ambassador: Redis proxy
    - name: redis-ambassador
      image: redis-proxy:v1
      ports:
        - containerPort: 6379
```

**Use cases:**
- Database connection pooling
- API gateway
- Protocol translation
- Load balancing

### Pattern 4: Adapter Pattern

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: adapter-example
spec:
  containers:
    # Main application (legacy format)
    - name: app
      image: legacy-app:v1
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
    
    # Adapter: Convert logs to standard format
    - name: log-adapter
      image: log-formatter:v1
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
          readOnly: true
```

**Use cases:**
- Log format conversion
- Metrics standardization
- API adaptation

### Pattern 5: Init Container Pattern

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-example
spec:
  initContainers:
    # Download configuration
    - name: init-config
      image: busybox:1.35
      command: ['sh', '-c']
      args:
        - |
          wget -O /config/app.conf http://config-server/app.conf
      volumeMounts:
        - name: config
          mountPath: /config
    
    # Wait for database
    - name: wait-db
      image: busybox:1.35
      command: ['sh', '-c', 'until nc -z db 5432; do sleep 2; done']
  
  containers:
    - name: app
      image: myapp:v1
      volumeMounts:
        - name: config
          mountPath: /etc/config
  
  volumes:
    - name: config
      emptyDir: {}
```

---

## Hands-On Examples

### Example 1: Basic Web Server

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
  labels:
    app: nginx
    tier: frontend
spec:
  containers:
    - name: nginx
      image: nginx:1.25.3
      ports:
        - name: http
          containerPort: 80
      resources:
        requests:
          memory: "64Mi"
          cpu: "50m"
        limits:
          memory: "128Mi"
          cpu: "100m"
      livenessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 10
        periodSeconds: 5
      readinessProbe:
        httpGet:
          path: /
          port: 80
        initialDelaySeconds: 5
        periodSeconds: 3
```

```bash
# Create the pod
kubectl apply -f web-server.yaml

# Check status
kubectl get pod web-server

# Test the pod
kubectl port-forward pod/web-server 8080:80
# Visit http://localhost:8080

# View logs
kubectl logs web-server

# Delete pod
kubectl delete pod web-server
```

### Example 2: Database Pod with Persistent Storage

```yaml
# First create PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
# Then create pod
apiVersion: v1
kind: Pod
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  containers:
    - name: mysql
      image: mysql:8.0
      env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
      ports:
        - containerPort: 3306
      volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
      resources:
        requests:
          memory: "256Mi"
          cpu: "200m"
        limits:
          memory: "512Mi"
          cpu: "500m"
  volumes:
    - name: mysql-storage
      persistentVolumeClaim:
        claimName: mysql-pvc
```

```bash
# Create secret first
kubectl create secret generic mysql-secret --from-literal=password=MyPassword123

# Create PVC and pod
kubectl apply -f mysql-pod.yaml

# Check pod
kubectl get pod mysql

# Connect to MySQL
kubectl exec -it mysql -- mysql -u root -p

# Delete
kubectl delete pod mysql
kubectl delete pvc mysql-pvc
kubectl delete secret mysql-secret
```

### Example 3: Multi-Container Pod (WordPress + MySQL)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: wordpress
  labels:
    app: wordpress
spec:
  containers:
    # WordPress container
    - name: wordpress
      image: wordpress:6.3
      env:
        - name: WORDPRESS_DB_HOST
          value: "127.0.0.1"  # MySQL on localhost
        - name: WORDPRESS_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: wp-secret
              key: db-password
      ports:
        - name: http
          containerPort: 80
      resources:
        requests:
          memory: "128Mi"
          cpu: "100m"
        limits:
          memory: "256Mi"
          cpu: "200m"
    
    # MySQL container (sidecar)
    - name: mysql
      image: mysql:8.0
      env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: wp-secret
              key: db-password
        - name: MYSQL_DATABASE
          value: wordpress
      ports:
        - containerPort: 3306
      resources:
        requests:
          memory: "256Mi"
          cpu: "200m"
        limits:
          memory: "512Mi"
          cpu: "500m"
```

```bash
# Create secret
kubectl create secret generic wp-secret --from-literal=db-password=SecurePass123

# Create pod
kubectl apply -f wordpress-pod.yaml

# Port forward
kubectl port-forward pod/wordpress 8080:80

# Visit http://localhost:8080

# Delete
kubectl delete pod wordpress
kubectl delete secret wp-secret
```

### Example 4: Job-like Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-job
spec:
  restartPolicy: Never  # Don't restart on completion
  containers:
    - name: job
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "Starting batch job..."
          for i in $(seq 1 10); do
            echo "Processing item $i"
            sleep 1
          done
          echo "Job completed successfully!"
      resources:
        requests:
          memory: "64Mi"
          cpu: "50m"
        limits:
          memory: "128Mi"
          cpu: "100m"
```

```bash
# Create pod
kubectl apply -f batch-job.yaml

# Watch completion
kubectl get pod batch-job -w

# View logs
kubectl logs batch-job

# Check exit code
kubectl get pod batch-job -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}'

# Delete
kubectl delete pod batch-job
```

### Example 5: Pod with ConfigMap and Secret

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.properties: |
    server.port=8080
    app.name=MyApp
    log.level=INFO
  database.properties: |
    db.host=mysql.default.svc.cluster.local
    db.port=3306
    db.name=mydb
---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  username: admin
  password: SecurePassword123
  api-key: "my-secret-api-key-12345"
---
# Pod
apiVersion: v1
kind: Pod
metadata:
  name: config-demo
spec:
  containers:
    - name: app
      image: busybox:1.35
      command: ["sh", "-c", "sleep 3600"]
      
      # Environment from ConfigMap
      env:
        - name: SERVER_PORT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: app.properties
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: password
      
      # Volume mounts
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
        - name: secret-volume
          mountPath: /etc/secrets
          readOnly: true
  
  volumes:
    - name: config-volume
      configMap:
        name: app-config
    - name: secret-volume
      secret:
        secretName: app-secret
```

```bash
# Apply all
kubectl apply -f config-demo.yaml

# Verify environment variables
kubectl exec config-demo -- env | grep -E "SERVER_PORT|DB_USER|DB_PASSWORD"

# Check mounted config files
kubectl exec config-demo -- ls -la /etc/config
kubectl exec config-demo -- cat /etc/config/app.properties

# Check mounted secrets
kubectl exec config-demo -- ls -la /etc/secrets
kubectl exec config-demo -- cat /etc/secrets/username

# Cleanup
kubectl delete pod config-demo
kubectl delete configmap app-config
kubectl delete secret app-secret
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Pod Stuck in Pending

```bash
# Check pod status
kubectl describe pod <pod-name>

# Common causes:
# - Insufficient resources
# - No nodes match selector
# - PVC not bound
# - Image pull secrets missing
```

**Solution:**
```bash
# Check node resources
kubectl describe nodes

# Check PVC status
kubectl get pvc

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### 2. ImagePullBackOff / ErrImagePull

```bash
# Check pod events
kubectl describe pod <pod-name> | grep -A 10 Events

# Common causes:
# - Image doesn't exist
# - Wrong image name/tag
# - Private registry without credentials
# - Network issues
```

**Solution:**
```bash
# Verify image exists
docker pull nginx:1.25.3

# Check image pull secrets
kubectl get secrets

# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password>

# Use in pod
spec:
  imagePullSecrets:
    - name: regcred
```

#### 3. CrashLoopBackOff

```bash
# View container logs
kubectl logs <pod-name>

# View previous container logs
kubectl logs <pod-name> --previous

# Common causes:
# - Application crashes on startup
# - Misconfigured environment variables
# - Missing dependencies
# - Incorrect command/args
```

**Solution:**
```bash
# Debug with shell
kubectl run debug --image=busybox:1.35 -it --rm -- sh

# Check application logs
kubectl logs <pod-name> --tail=50

# Describe pod for events
kubectl describe pod <pod-name>
```

#### 4. Pod Running but Not Responding

```bash
# Check if pod is actually running
kubectl get pod <pod-name>

# Test connectivity
kubectl exec <pod-name> -- wget -O- http://localhost:80

# Check liveness/readiness probes
kubectl describe pod <pod-name> | grep -A 5 "Liveness\|Readiness"

# Common causes:
# - Wrong port number
# - Application not listening on 0.0.0.0
# - Firewall rules
# - Probe configuration wrong
```

**Solution:**
```bash
# Port forward to test
kubectl port-forward pod/<pod-name> 8080:80

# Check what's listening
kubectl exec <pod-name> -- netstat -tlnp

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh
```

#### 5. Permission Denied Errors

```bash
# Check security context
kubectl get pod <pod-name> -o yaml | grep -A 10 securityContext

# Common causes:
# - Running as non-root without permissions
# - ReadOnlyRootFilesystem without proper volumes
# - Missing capabilities
```

**Solution:**
```yaml
securityContext:
  runAsUser: 1000
  fsGroup: 2000  # Group for volumes
  runAsNonRoot: true
```

#### 6. Out of Memory (OOMKilled)

```bash
# Check container status
kubectl describe pod <pod-name> | grep -A 3 "Last State"

# Will show: OOMKilled

# Check memory limits
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'
```

**Solution:**
```yaml
resources:
  requests:
    memory: "256Mi"  # Increase
  limits:
    memory: "512Mi"  # Increase
```

### Debugging Commands Reference

```bash
# Get pod details
kubectl get pod <pod-name> -o yaml
kubectl get pod <pod-name> -o json
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>  # Specific container
kubectl logs <pod-name> --previous            # Previous instance
kubectl logs <pod-name> --tail=50             # Last 50 lines
kubectl logs <pod-name> -f                    # Follow logs

# Execute commands
kubectl exec <pod-name> -- ls -la
kubectl exec <pod-name> -c <container> -- ps aux
kubectl exec -it <pod-name> -- /bin/sh       # Interactive shell

# Port forwarding
kubectl port-forward pod/<pod-name> 8080:80

# Copy files
kubectl cp <pod-name>:/path/to/file ./local-file
kubectl cp ./local-file <pod-name>:/path/to/file

# View events
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events --field-selector involvedObject.name=<pod-name>

# Check resource usage
kubectl top pod <pod-name>

# Debug with ephemeral container (K8s 1.23+)
kubectl debug <pod-name> -it --image=busybox:1.35

# Create debug pod
kubectl run debug --image=nicolaka/netshoot -it --rm -- /bin/bash
```

---

## Quick Reference

### Pod Lifecycle Commands

```bash
# Create pod
kubectl apply -f pod.yaml
kubectl run nginx --image=nginx:1.25.3

# View pods
kubectl get pods
kubectl get pods -o wide
kubectl get pods --all-namespaces
kubectl get pods -l app=nginx

# Describe pod
kubectl describe pod <pod-name>

# Logs
kubectl logs <pod-name>
kubectl logs <pod-name> -f

# Execute
kubectl exec -it <pod-name> -- /bin/sh

# Delete pod
kubectl delete pod <pod-name>
kubectl delete pod <pod-name> --grace-period=0 --force

# Port forward
kubectl port-forward pod/<pod-name> 8080:80

# Edit pod
kubectl edit pod <pod-name>

# Export pod
kubectl get pod <pod-name> -o yaml > pod.yaml
```

### Pod Status Values

```bash
Pending          # Pod accepted, not running yet
Running          # Pod bound to node, containers running
Succeeded        # All containers terminated successfully
Failed           # All containers terminated, at least one failed
Unknown          # Pod state cannot be obtained
```

### Restart Policy

```yaml
restartPolicy: Always     # Always restart (default)
restartPolicy: OnFailure  # Restart only if fails
restartPolicy: Never      # Never restart
```

### Common Pod Patterns

```bash
# Single container
kubectl run nginx --image=nginx:1.25.3

# With environment variable
kubectl run nginx --image=nginx --env="ENV=prod"

# With resource limits
kubectl run nginx --image=nginx --requests='cpu=100m,memory=128Mi' --limits='cpu=200m,memory=256Mi'

# With labels
kubectl run nginx --image=nginx --labels="app=nginx,tier=frontend"

# With port
kubectl run nginx --image=nginx --port=80

# Dry run (generate YAML)
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Run temporarily
kubectl run test --image=busybox -it --rm -- /bin/sh
```

---
