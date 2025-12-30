# Kubernetes Architecture Tutorial

## Table of Contents
1. [Introduction to Kubernetes](#introduction-to-kubernetes)
2. [Kubernetes Cluster Architecture](#kubernetes-cluster-architecture)
3. [Single Node vs Multi-Node Architecture](#single-node-vs-multi-node-architecture)
4. [Master Node (Control Plane)](#master-node-control-plane)
5. [Worker Nodes](#worker-nodes)
6. [Component Communication Flow](#component-communication-flow)
7. [Architecture Best Practices](#architecture-best-practices)

---

## Introduction to Kubernetes

Kubernetes (K8s) is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It was originally developed by Google and is now maintained by the Cloud Native Computing Foundation (CNCF).

### Key Features
- **Automated Rollouts and Rollbacks**: Deploy changes automatically with rollback capabilities
- **Service Discovery and Load Balancing**: Expose containers using DNS names or IP addresses
- **Storage Orchestration**: Automatically mount storage systems of your choice
- **Self-Healing**: Restart failed containers and replace unhealthy nodes
- **Secret and Configuration Management**: Manage sensitive information securely
- **Horizontal Scaling**: Scale applications up or down based on demand

---

## Kubernetes Cluster Architecture

A Kubernetes cluster consists of a set of machines (physical or virtual) called nodes. These nodes are categorized into two types:

1. **Master Node (Control Plane)**: Manages the cluster
2. **Worker Nodes**: Run the actual application workloads

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │           Master Node (Control Plane)              │     │
│  │  ┌──────────┐  ┌──────┐  ┌───────────┐ ┌────────┐  │     │
│  │  │API Server│  │ etcd │  │ Scheduler │ │Control-│  │     │
│  │  │          │  │      │  │           │ │ler Mgr │  │     │
│  │  └──────────┘  └──────┘  └───────────┘ └────────┘  │     │
│  └────────────────────────────────────────────────────┘     │
│                           ↕                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Worker Node 1  │  │  Worker Node 2  │  │Worker Node N │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │┌───────────┐ │ │
│  │  │ Kubelet   │  │  │  │ Kubelet   │  │  ││ Kubelet   │ │ │
│  │  │ Kube-proxy│  │  │  │ Kube-proxy│  │  ││ Kube-proxy│ │ │
│  │  │ Container │  │  │  │ Container │  │  ││ Container │ │ │
│  │  │ Runtime   │  │  │  │ Runtime   │  │  ││ Runtime   │ │ │
│  │  └───────────┘  │  │  └───────────┘  │  │└───────────┘ │ │
│  │  [Pods]         │  │  [Pods]         │  │[Pods]        │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Single Node vs Multi-Node Architecture

### Single Node Architecture

In a single-node setup, both the master and worker components run on the same machine. This is typically used for:
- Development and testing environments
- Learning Kubernetes concepts
- Local development with tools like Minikube, kind, or Docker Desktop

**Characteristics:**
- All control plane components run on one node
- Worker components also run on the same node
- Limited scalability and no high availability
- Lower resource requirements
- Easy to set up and manage

```
┌─────────────────────────────────────────┐
│      Single Node Kubernetes Cluster     │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │       Control Plane Components     │ │
│  │  • API Server                      │ │
│  │  • etcd                            │ │
│  │  • Scheduler                       │ │
│  │  • Controller Manager              │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │       Worker Components            │ │
│  │  • Kubelet                         │ │
│  │  • Kube-proxy                      │ │
│  │  • Container Runtime               │ │
│  │  • Pods                            │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Use Cases:**
- Local development with Minikube
- CI/CD testing environments
- Learning and experimentation
- Resource-constrained scenarios

---

### Multi-Node Architecture

A production-grade setup with separate master and worker nodes providing high availability, scalability, and fault tolerance.

**Characteristics:**
- Master nodes dedicated to control plane operations
- Multiple worker nodes for running applications
- High availability through multiple master nodes
- Horizontal scalability by adding worker nodes
- Better resource isolation and security

```
┌──────────────────────────────────────────────────────────────┐
│              Multi-Node Kubernetes Cluster                   │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Master 1   │  │  Master 2   │  │  Master 3   │           │
│  │ (Active)    │  │ (Standby)   │  │ (Standby)   │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│         │                │                 │                 │
│         └────────────────┴─────────────────┘                 │
│                          │                                   │
│              ┌───────────┴───────────┐                       │
│              │    Load Balancer      │                       │
│              └───────────┬───────────┘                       │
│                          │                                   │
│         ┌────────────────┼────────────────┐                  │
│         │                │                │                  │
│  ┌──────▼─────┐  ┌──────▼─────┐  ┌──────▼─────┐              │
│  │  Worker 1  │  │  Worker 2  │  │  Worker N  │              │
│  │  [Pods]    │  │  [Pods]    │  │  [Pods]    │              │
│  └────────────┘  └────────────┘  └────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

**Use Cases:**
- Production environments
- High availability requirements
- Large-scale applications
- Enterprise deployments

---

## Master Node (Control Plane)

The master node hosts the control plane components that manage the entire Kubernetes cluster. It makes global decisions about the cluster and detects and responds to cluster events.

### Components of Master Node

#### 1. API Server

**Component Name:** `kube-apiserver`

The API Server is the front-end of the Kubernetes control plane and the central management entity.

**Key Functions:**
- Exposes the Kubernetes API (RESTful interface)
- All cluster operations go through the API server
- Authenticates and validates requests
- Processes RESTful requests and updates etcd
- Acts as the gateway for all cluster communications

**Communication:**
- Users interact via `kubectl` commands
- Other control plane components communicate through API server
- Worker nodes' kubelet talks to API server
- External systems integrate via API

**Example Interaction:**
```bash
# When you run:
kubectl create deployment nginx --image=nginx

# The kubectl command sends an HTTP request to the API Server
# API Server validates the request, stores it in etcd,
# and triggers the scheduler to assign the pod to a node
```

**Key Features:**
- **Authentication**: Verifies user identity
- **Authorization**: Checks if user has permission
- **Admission Control**: Validates and mutates requests
- **API Versioning**: Supports multiple API versions
- **Horizontal Scaling**: Can run multiple instances for HA

---

#### 2. etcd

**Component Name:** `etcd`

etcd is a distributed, consistent key-value store used as Kubernetes' backing store for all cluster data.

**Key Functions:**
- Stores all cluster configuration data
- Maintains the desired state of the cluster
- Stores information about pods, services, secrets, config maps, etc.
- Provides distributed consensus using the Raft algorithm
- Acts as the single source of truth for the cluster

**Data Stored in etcd:**
- Cluster state and metadata
- Configuration data
- Secrets and ConfigMaps
- Service discovery information
- Node information
- Pod specifications and status

**Critical Characteristics:**
- **Consistency**: Strong consistency guarantees
- **Reliability**: Distributed across multiple nodes in HA setups
- **Watch API**: Allows components to watch for changes
- **Backup Critical**: Regular backups essential for disaster recovery

**Example Data Structure:**
```
/registry/
  ├── pods/
  │   ├── default/nginx-pod
  │   └── kube-system/coredns-pod
  ├── services/
  │   └── default/my-service
  ├── deployments/
  │   └── default/nginx-deployment
  └── nodes/
      ├── worker-node-1
      └── worker-node-2
```

**Best Practices:**
- Run etcd on dedicated nodes in production
- Regular automated backups
- Use TLS for secure communication
- Monitor etcd health and performance

---

#### 3. Scheduler

**Component Name:** `kube-scheduler`

The scheduler watches for newly created pods that have no assigned node and selects a node for them to run on.

**Key Functions:**
- Watches for unscheduled pods via API server
- Selects the best node for each pod
- Considers resource requirements and constraints
- Implements scheduling policies and priorities
- Updates pod definition with selected node

**Scheduling Process:**

1. **Filtering**: Eliminate nodes that don't meet requirements
   - Insufficient CPU/memory
   - Node selector constraints
   - Taints and tolerations
   - Affinity/anti-affinity rules

2. **Scoring**: Rank remaining nodes based on priorities
   - Resource availability
   - Load balancing
   - Data locality
   - Custom priorities

3. **Binding**: Assign pod to highest-scored node

**Scheduling Criteria:**
- **Resource Requirements**: CPU, memory, storage
- **Quality of Service (QoS)**: Guaranteed, Burstable, BestEffort
- **Affinity/Anti-affinity**: Pod and node preferences
- **Taints and Tolerations**: Node restrictions
- **Node Selectors**: Explicit node selection
- **Data Locality**: Proximity to data

**Example:**
```yaml
# Pod with resource requests
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

The scheduler will find a node with at least 64Mi memory and 250m CPU available.

---

#### 4. Controller Manager

**Component Name:** `kube-controller-manager`

The controller manager runs controller processes that regulate the state of the cluster and move the current state toward the desired state.

**Key Functions:**
- Runs multiple controllers as a single process
- Continuously monitors cluster state via API server
- Takes corrective actions to maintain desired state
- Handles cluster-level functions
- Manages lifecycle of various Kubernetes objects

**Major Controllers:**

##### Node Controller
- Monitors node health
- Detects node failures
- Marks nodes as unavailable
- Evicts pods from unhealthy nodes

##### Replication Controller
- Ensures correct number of pod replicas
- Creates or deletes pods to match desired count
- Handles scaling operations

##### Endpoints Controller
- Populates endpoint objects (joins Services and Pods)
- Updates endpoints when pods change

##### Service Account & Token Controllers
- Creates default service accounts for namespaces
- Generates API access tokens

##### Deployment Controller
- Manages deployments and rollouts
- Handles updates and rollbacks
- Maintains desired replica count

##### StatefulSet Controller
- Manages stateful applications
- Maintains pod ordering and uniqueness

##### Job Controller
- Manages batch jobs
- Ensures jobs run to completion

##### DaemonSet Controller
- Ensures pods run on all (or selected) nodes
- Useful for node-level operations

**Control Loop Pattern:**
```
┌─────────────────────────────────────────┐
│                                          │
│  1. Observe Current State                │
│         ↓                                │
│  2. Compare with Desired State           │
│         ↓                                │
│  3. Take Action if Different             │
│         ↓                                │
│  4. Update Status                        │
│         ↓                                │
│  [Repeat Continuously]                   │
│                                          │
└─────────────────────────────────────────┘
```

**Example Scenario:**
```yaml
# Desired State: 3 nginx replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
```

If one pod crashes:
1. Controller detects 2 pods running (vs 3 desired)
2. Controller creates a new pod via API server
3. Scheduler assigns the pod to a node
4. Kubelet on that node starts the pod
5. Controller updates status to 3/3 replicas

---

## Worker Nodes

Worker nodes are the machines where your containerized applications actually run. Each worker node contains the necessary services to run pods and is managed by the control plane.

### Components of Worker Node

#### 1. Kubelet

**Component Name:** `kubelet`

The kubelet is the primary node agent that runs on each worker node and ensures containers are running in pods.

**Key Functions:**
- Registers node with the API server
- Watches for pod assignments from the API server
- Ensures containers in pods are running and healthy
- Reports node and pod status back to control plane
- Executes container lifecycle hooks
- Manages volume mounting
- Collects and reports resource metrics

**Responsibilities:**
- **Pod Lifecycle Management**: Start, stop, and monitor containers
- **Health Checks**: Run liveness and readiness probes
- **Resource Monitoring**: Track CPU, memory, disk usage
- **Volume Management**: Mount and unmount volumes
- **Image Management**: Pull container images
- **Pod Status Reporting**: Update pod status in API server

**How Kubelet Works:**

1. Watches API server for pod assignments
2. Receives pod specifications (PodSpec)
3. Instructs container runtime to pull images
4. Creates and starts containers
5. Monitors container health
6. Reports status back to API server
7. Restarts containers if they fail (based on restart policy)

**Communication:**
```
API Server ←→ Kubelet ←→ Container Runtime
                ↓
            [Pods/Containers]
```

**Health Monitoring:**
- **Liveness Probe**: Is the container alive?
- **Readiness Probe**: Is the container ready to serve traffic?
- **Startup Probe**: Has the container started successfully?

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 3
```

Kubelet will execute the liveness probe every 3 seconds and restart the container if it fails.

---

#### 2. Kube-proxy

**Component Name:** `kube-proxy`

Kube-proxy is a network proxy that runs on each node and maintains network rules for pod communication.

**Key Functions:**
- Implements Kubernetes Service abstraction
- Maintains network rules on nodes
- Enables pod-to-pod and external-to-pod communication
- Performs connection forwarding
- Load balances traffic across pod replicas
- Handles service discovery

**Network Modes:**

##### 1. iptables Mode (Default)
- Uses Linux iptables rules
- Randomly selects backend pod
- Lower overhead
- More scalable

##### 2. IPVS Mode
- Uses IP Virtual Server
- More efficient for large clusters
- Better performance
- Multiple load balancing algorithms (round-robin, least connection, etc.)

##### 3. Userspace Mode (Legacy)
- Runs proxy in userspace
- Higher overhead
- Less commonly used

**How Services Work:**

```
External Client
    ↓
Service IP (ClusterIP: 10.96.0.1)
    ↓
Kube-proxy (on any node)
    ↓
Load balances to one of:
    → Pod 1 (10.244.1.5)
    → Pod 2 (10.244.2.8)
    → Pod 3 (10.244.3.2)
```

**Example Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

Kube-proxy will:
1. Watch for service creation via API server
2. Create iptables/IPVS rules
3. Route traffic from service IP to backend pods
4. Distribute load across healthy pods

**Service Types Handled:**
- **ClusterIP**: Internal cluster communication
- **NodePort**: Exposes service on each node's IP
- **LoadBalancer**: External load balancer (cloud providers)
- **ExternalName**: Maps service to DNS name

---

#### 3. Container Runtime

The container runtime is the software responsible for running containers. Kubernetes supports several container runtimes through the Container Runtime Interface (CRI).

**Supported Runtimes:**

##### Docker (via containerd)
- Most popular traditionally
- Now uses containerd as the underlying runtime
- Familiar to most developers

##### containerd
- Industry-standard container runtime
- Graduated CNCF project
- Lightweight and efficient
- Default in many Kubernetes distributions

##### CRI-O
- Lightweight runtime specifically for Kubernetes
- Implements CRI specification
- Optimized for Kubernetes workloads

**Key Functions:**
- Pull container images from registries
- Unpack container images
- Create and start containers
- Stop and delete containers
- Monitor container status
- Manage container resources (CPU, memory, etc.)
- Execute commands inside containers

**Container Lifecycle:**
```
Image Pull → Container Creation → Container Start
    ↓
Running State ←→ Health Checks
    ↓
Container Stop → Container Removal
```

**Container Runtime Interface (CRI):**
```
Kubelet ←→ CRI API ←→ Container Runtime
                          ↓
                      [Containers]
```

The CRI allows Kubernetes to work with different container runtimes without modification.

---

#### 4. Pods

While not a component per se, pods are the smallest deployable units in Kubernetes and run on worker nodes.

**Pod Characteristics:**
- Smallest unit in Kubernetes
- One or more containers
- Shared network namespace (same IP)
- Shared storage volumes
- Scheduled together on same node
- Ephemeral by nature

**Pod Networking:**
- Each pod gets unique IP address
- Containers in pod communicate via localhost
- Pods communicate directly with other pods
- No NAT required for pod-to-pod communication

**Example Multi-Container Pod:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
  - name: log-aggregator
    image: fluent/fluentd
    volumeMounts:
    - name: logs
      mountPath: /var/log
  volumes:
  - name: logs
    emptyDir: {}
```

---

## Component Communication Flow

Understanding how components communicate is crucial for troubleshooting and optimizing Kubernetes clusters.

### Request Flow for Pod Creation

```
1. kubectl create deployment nginx --image=nginx
   ↓
2. kubectl → API Server (HTTPS REST call)
   ↓
3. API Server authenticates and authorizes request
   ↓
4. API Server validates the request
   ↓
5. API Server stores deployment in etcd
   ↓
6. Deployment Controller watches API server
   ↓
7. Deployment Controller creates ReplicaSet
   ↓
8. ReplicaSet Controller creates Pod(s)
   ↓
9. Scheduler watches for unscheduled pods
   ↓
10. Scheduler selects best node
    ↓
11. Scheduler updates pod with node assignment
    ↓
12. Kubelet on assigned node watches API server
    ↓
13. Kubelet sees pod assignment
    ↓
14. Kubelet instructs container runtime
    ↓
15. Container runtime pulls image
    ↓
16. Container runtime creates and starts container
    ↓
17. Kubelet reports status to API server
    ↓
18. API Server updates pod status in etcd
```

### Network Traffic Flow

```
User Request
    ↓
External Load Balancer (if LoadBalancer service)
    ↓
NodePort (if NodePort service)
    ↓
Kube-proxy (iptables/IPVS rules)
    ↓
Service ClusterIP
    ↓
Pod IP (selected by kube-proxy)
    ↓
Container Port
    ↓
Application
```

### Component Dependencies

```
etcd ←→ API Server ←→ kubectl
         ↕              
    ┌────┴────┐
    ↓         ↓
Scheduler  Controller Manager
    ↓         ↓
    └────┬────┘
         ↓
    API Server ←→ Kubelet ←→ Container Runtime
         ↕           ↕              ↓
    Kube-proxy    Pods         [Containers]
```

### Information Flow

**Watch Mechanism:**
Most components use the watch mechanism to stay updated:

```
Component → Watch API Server → Receive Events → Take Action
```

**Example Events:**
- Pod created → Scheduler assigns node
- Pod assigned → Kubelet starts pod
- Service created → Kube-proxy creates rules
- Node failure → Controller Manager reschedules pods

---

## Architecture Best Practices

### High Availability (HA) Setup

#### Master Node HA
- Run at least 3 master nodes (odd number for etcd quorum)
- Use load balancer for API server endpoints
- Distribute masters across availability zones
- Use separate etcd cluster for large deployments

```
┌─────────────────────────────────────┐
│       Load Balancer (HA Proxy)      │
│                                      │
│   API Server Endpoint: api.k8s.com  │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    ↓         ↓         ↓
┌────────┐ ┌────────┐ ┌────────┐
│Master 1│ │Master 2│ │Master 3│
│(Leader)│ │        │ │        │
└────────┘ └────────┘ └────────┘
```

#### etcd HA
- Minimum 3 nodes for HA
- 5 nodes for critical production systems
- Never use even numbers (can cause split-brain)
- Regular backups (automated)
- Monitor etcd health continuously

#### Worker Node HA
- Minimum 3 worker nodes for small clusters
- Spread pods across multiple nodes
- Use pod anti-affinity for critical workloads
- Configure pod disruption budgets

### Resource Management

#### Control Plane Sizing
**Small Cluster (< 10 nodes):**
- 2 CPU cores
- 4 GB RAM
- 20 GB disk

**Medium Cluster (10-100 nodes):**
- 4 CPU cores
- 8 GB RAM
- 50 GB disk

**Large Cluster (100+ nodes):**
- 8+ CPU cores
- 16+ GB RAM
- 100+ GB disk

#### Worker Node Sizing
- Depends on workload requirements
- Leave 10-20% overhead for system processes
- Monitor and adjust based on actual usage
- Consider memory-optimized or CPU-optimized instances

### Security Best Practices

#### API Server
- Enable RBAC (Role-Based Access Control)
- Use TLS for all communication
- Restrict API server access to necessary IPs
- Enable audit logging
- Use admission controllers

#### etcd
- Use TLS for client-server communication
- Use TLS for peer-to-peer communication
- Restrict access to etcd endpoints
- Regular encrypted backups
- Store backups securely

#### Network Security
- Use Network Policies to restrict pod communication
- Implement Pod Security Standards
- Use private container registries
- Scan images for vulnerabilities
- Enable encryption for secrets

### Monitoring and Observability

#### Key Metrics to Monitor

**Control Plane:**
- API server latency and throughput
- etcd latency and disk I/O
- Scheduler scheduling latency
- Controller manager work queue depth

**Worker Nodes:**
- CPU and memory utilization
- Disk I/O and capacity
- Network bandwidth
- Pod count and status
- Container restart count

**Tools:**
- Prometheus for metrics collection
- Grafana for visualization
- ELK/EFK stack for logging
- Jaeger or Zipkin for tracing

### Backup and Disaster Recovery

#### What to Backup
- etcd data (most critical)
- Cluster configuration
- Application manifests
- Persistent volume data

#### Backup Strategy
```bash
# Example etcd backup
ETCDCTL_API=3 etcdctl snapshot save backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

#### Recovery Plan
- Document recovery procedures
- Test recovery process regularly
- Automate backup process
- Store backups in multiple locations
- Maintain backup retention policy

### Scalability Considerations

#### Horizontal Scaling
- Add worker nodes for application scaling
- Add master nodes for control plane HA
- Consider cluster federation for multi-cluster management

#### Vertical Scaling
- Increase node resources as needed
- Monitor resource utilization trends
- Plan for capacity ahead of demand

#### Cluster Limits
- Maximum 5,000 nodes per cluster
- Maximum 150,000 pods per cluster
- Maximum 300,000 containers per cluster
- Maximum 100 pods per node

---
