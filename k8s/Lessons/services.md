# Kubernetes Service Tutorial

## What is a Service?

A **Service** is a stable network endpoint that provides access to a set of Pods. Pods are ephemeral and have changing IPs, but Services provide a consistent way to access them.

```
Without Service:
Pod 1 (IP: 10.1.1.5) ──┐
Pod 2 (IP: 10.1.1.8) ──┼──▶ Clients need to track changing IPs ❌
Pod 3 (IP: 10.1.1.9) ──┘

With Service:
                    ┌────────────────┐
                    │    Service     │
                    │  my-service    │
                    │  IP: 10.96.0.1 │ ◄── Stable IP ✅
                    └────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
    Pod 1              Pod 2              Pod 3
  (10.1.1.5)        (10.1.1.8)        (10.1.1.9)
```

### Why Use Services?

✅ **Stable endpoint** - Doesn't change when pods restart
✅ **Load balancing** - Distributes traffic across pods
✅ **Service discovery** - DNS names for services
✅ **Port abstraction** - Map service port to pod port

---

## Four Service Types

| Type | Access From | Use Case | External IP |
|------|-------------|----------|-------------|
| **ClusterIP** | Inside cluster only | Internal microservices | No |
| **NodePort** | Outside cluster via Node IP:Port | Development, testing | No (use Node IP) |
| **LoadBalancer** | Outside cluster via LoadBalancer | Production external access | Yes |
| **ExternalName** | Inside cluster to external DNS | External services | N/A |

---

## 1. ClusterIP (Default)

### What is ClusterIP?

- **Default service type**
- Accessible **only within the cluster**
- Gets internal cluster IP (e.g., 10.96.0.1)
- Perfect for internal communication between services

```
┌─────────────────────────────────────────────────────┐
│                    Cluster                          │
│                                                     │
│  ┌──────────┐         ┌─────────────────┐           │
│  │ Frontend │────────▶│ ClusterIP Svc   │           │
│  │   Pod    │         │  backend-svc    │           │
│  └──────────┘         │  10.96.0.10:80  │           │
│                       └─────────────────┘           │
│                              │                      │
│                    ┌─────────┴─────────┐            │
│                    ▼                   ▼            │
│              ┌─────────┐         ┌─────────┐        │
│              │Backend 1│         │Backend 2│        │
│              └─────────┘         └─────────┘        │
│                                                     │
│  ❌ Cannot access from outside cluster              │
└─────────────────────────────────────────────────────┘
```

### ClusterIP YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
spec:
  type: ClusterIP  # Default, can be omitted
  selector:
    app: backend   # Selects pods with this label
  ports:
    - name: http
      protocol: TCP
      port: 80           # Service port
      targetPort: 8080   # Pod port
```

### Create ClusterIP Service

```bash
# Method 1: Imperative
kubectl expose deployment backend --port=80 --target-port=8080

# Method 2: YAML
kubectl apply -f clusterip-service.yaml

# View service
kubectl get service backend-service
kubectl get svc backend-service  # Short form

# Describe service
kubectl describe svc backend-service

# Get service URL
kubectl get svc backend-service -o jsonpath='{.spec.clusterIP}'
```

### Test ClusterIP Service

```bash
# From inside cluster
kubectl run test --image=busybox:1.35 -it --rm -- wget -O- http://backend-service

# Using service DNS name
kubectl run test --image=busybox:1.35 -it --rm -- wget -O- http://backend-service.default.svc.cluster.local

# Port-forward to access from local machine
kubectl port-forward svc/backend-service 8080:80
# Access at http://localhost:8080
```

### Complete ClusterIP Example

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3
          ports:
            - containerPort: 80
---
# ClusterIP Service
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - port: 80
      targetPort: 80
```

```bash
# Apply
kubectl apply -f backend-app.yaml

# Test from another pod
kubectl run test --image=curlimages/curl -it --rm -- curl http://backend-service
```

---

## 2. NodePort

### What is NodePort?

- Exposes service on **each Node's IP** at a static port
- Accessible from **outside the cluster** using `<NodeIP>:<NodePort>`
- Port range: **30000-32767** (default)
- Good for development/testing, not production

```
┌─────────────────────────────────────────────────────┐
│                    Cluster                          │
│                                                     │
│  Node 1 (192.168.1.10)    Node 2 (192.168.1.11)     │
│       │                          │                  │
│       │ :30080                   │ :30080           │
│       └────────┬─────────────────┘                  │
│                ▼                                    │
│         ┌─────────────┐                             │
│         │  NodePort   │                             │
│         │   Service   │                             │
│         └─────────────┘                             │
│                │                                    │
│      ┌─────────┴─────────┐                          │
│      ▼                   ▼                          │
│  ┌───────┐           ┌───────┐                      │
│  │ Pod 1 │           │ Pod 2 │                      │
│  └───────┘           └───────┘                      │
└─────────────────────────────────────────────────────┘
         ▲                     ▲
         │                     │
    External Client can access via:
    http://192.168.1.10:30080
    http://192.168.1.11:30080
```

### NodePort YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - name: http
      protocol: TCP
      port: 80          # Service port (inside cluster)
      targetPort: 8080  # Pod port
      nodePort: 30080   # External port (optional, auto-assigned if omitted)
```

### Create NodePort Service

```bash
# Method 1: Imperative
kubectl expose deployment web --type=NodePort --port=80 --target-port=8080

# Method 2: YAML
kubectl apply -f nodeport-service.yaml

# Get assigned NodePort
kubectl get svc web-service
# Output: PORT(S) shows 80:30080/TCP

# Get Node IPs
kubectl get nodes -o wide
```

### Access NodePort Service

```bash
# Get Node IP
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')

# Get NodePort
NODE_PORT=$(kubectl get svc web-service -o jsonpath='{.spec.ports[0].nodePort}')

# Access service
curl http://$NODE_IP:$NODE_PORT

# In Minikube
minikube service web-service
minikube service web-service --url
```

### Complete NodePort Example

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3
          ports:
            - containerPort: 80
---
# NodePort Service
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080  # Optional: specify port (30000-32767)
```

```bash
# Apply
kubectl apply -f web-app.yaml

# Access (if using Minikube)
minikube service web-service

# Access (on cloud/bare metal)
curl http://<node-ip>:30080
```

---

## 3. LoadBalancer

### What is LoadBalancer?

- Exposes service **externally** using cloud provider's load balancer
- Gets a **public IP address** (External IP)
- Works with **AWS ELB, GCP LB, Azure LB**, etc.
- **Production-ready** for external access
- In Minikube, use `minikube tunnel`

```
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │  Load Balancer │
              │  52.1.2.3:80   │ ◄─── External IP
              └────────────────┘
                       │
┌──────────────────────┼──────────────────────┐
│         Cluster      │                      │
│                      ▼                      │
│              ┌───────────────┐              │
│              │ LoadBalancer  │              │
│              │    Service    │              │
│              └───────────────┘              │
│                      │                      │
│         ┌────────────┼────────────┐         │
│         ▼            ▼            ▼         │
│     ┌──────┐    ┌──────┐    ┌──────┐        │
│     │Pod 1 │    │Pod 2 │    │Pod 3 │        │
│     └──────┘    └──────┘    └──────┘        │
└─────────────────────────────────────────────┘
```

### LoadBalancer YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - name: http
      protocol: TCP
      port: 80          # External port
      targetPort: 8080  # Pod port
  # Optional: specific load balancer IP (cloud-specific)
  loadBalancerIP: 52.1.2.3
  # Optional: source IP ranges allowed
  loadBalancerSourceRanges:
    - 203.0.113.0/24
```

### Create LoadBalancer Service

```bash
# Method 1: Imperative
kubectl expose deployment web --type=LoadBalancer --port=80 --target-port=8080

# Method 2: YAML
kubectl apply -f loadbalancer-service.yaml

# Get service with external IP
kubectl get svc web-lb

# Wait for EXTERNAL-IP (takes 1-2 minutes on cloud)
kubectl get svc web-lb -w
```

### Access LoadBalancer Service

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc web-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access service
curl http://$EXTERNAL_IP

# On AWS (uses hostname instead of IP)
EXTERNAL_HOST=$(kubectl get svc web-lb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl http://$EXTERNAL_HOST
```

### LoadBalancer in Minikube

```bash
# Start tunnel (in separate terminal)
minikube tunnel

# Create LoadBalancer service
kubectl apply -f loadbalancer-service.yaml

# Get external IP (will be assigned by tunnel)
kubectl get svc web-lb
# EXTERNAL-IP will show actual IP (like 127.0.0.1)

# Access service
curl http://127.0.0.1
```

### Complete LoadBalancer Example

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3
          ports:
            - containerPort: 80
---
# LoadBalancer Service
apiVersion: v1
kind: Service
metadata:
  name: web-lb
  annotations:
    # Cloud-specific annotations
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"  # AWS
    # cloud.google.com/load-balancer-type: "Internal"        # GCP
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: https
      port: 443
      targetPort: 443
```

```bash
# Apply
kubectl apply -f web-lb-app.yaml

# Wait for external IP
kubectl get svc web-lb -w

# Access
curl http://<external-ip>
```

---

## 4. ExternalName

### What is ExternalName?

- Maps service to **external DNS name**
- No proxying or load balancing
- Returns **CNAME record** for external service
- Useful for accessing external databases, APIs, etc.

```
┌─────────────────────────────────────────────────────┐
│                    Cluster                          │
│                                                     │
│  ┌──────────┐                                       │
│  │   Pod    │                                       │
│  │          │                                       │
│  └──────────┘                                       │
│       │                                             │
│       │ Connects to: db-service                     │
│       ▼                                             │
│  ┌─────────────────┐                                │
│  │ ExternalName    │                                │
│  │   Service       │                                │
│  │  db-service     │───── Returns CNAME ───────┐    │
│  └─────────────────┘                           │    │
│                                                │    │
└────────────────────────────────────────────────┼────┘
                                                 │
                                                 ▼
                                    External Database
                                    mysql.example.com
```

### ExternalName YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: mysql.example.com  # External DNS name
  ports:
    - port: 3306  # Optional, for documentation
```

### Create ExternalName Service

```bash
# Imperative (limited options)
kubectl create service externalname external-db --external-name mysql.example.com

# YAML
kubectl apply -f externalname-service.yaml
```

### Use ExternalName Service

```yaml
# Pod using ExternalName service
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: mysql:8.0
      env:
        - name: MYSQL_HOST
          value: "external-db"  # Uses ExternalName service
        - name: MYSQL_PORT
          value: "3306"
```

```bash
# Test DNS resolution
kubectl run test --image=busybox:1.35 -it --rm -- nslookup external-db

# Output shows CNAME pointing to mysql.example.com
```

### Complete ExternalName Example

```yaml
# ExternalName Service for external database
apiVersion: v1
kind: Service
metadata:
  name: production-db
spec:
  type: ExternalName
  externalName: prod-mysql.us-east-1.rds.amazonaws.com
---
# Application using the service
apiVersion: v1
kind: Pod
metadata:
  name: backend
spec:
  containers:
    - name: app
      image: myapp:v1
      env:
        - name: DATABASE_HOST
          value: "production-db"  # Resolves to AWS RDS
        - name: DATABASE_PORT
          value: "3306"
```

---

## Service Discovery

### DNS Names for Services

Every service gets a DNS name:

```
# Format
<service-name>.<namespace>.svc.cluster.local

# Examples
backend-service.default.svc.cluster.local
web-service.production.svc.cluster.local
```

### Using Service Discovery

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend
spec:
  containers:
    - name: app
      image: frontend:v1
      env:
        # Short name (same namespace)
        - name: BACKEND_URL
          value: "http://backend-service"
        
        # Full name (different namespace)
        - name: API_URL
          value: "http://api-service.production.svc.cluster.local"
```

```bash
# Test DNS resolution
kubectl run test --image=busybox:1.35 -it --rm -- nslookup backend-service

# Test connectivity
kubectl run test --image=curlimages/curl -it --rm -- curl http://backend-service
```

---

## Service Endpoints

### What are Endpoints?

Endpoints are the actual pod IPs that a service routes to.

```bash
# View service endpoints
kubectl get endpoints
kubectl get ep  # Short form

# View specific service endpoints
kubectl describe ep backend-service

# Endpoints update automatically when pods change
```

### Manual Endpoints (Without Selector)

```yaml
# Service without selector
apiVersion: v1
kind: Service
metadata:
  name: external-service
spec:
  ports:
    - port: 80
      targetPort: 80
---
# Manual endpoints
apiVersion: v1
kind: Endpoints
metadata:
  name: external-service  # Must match service name
subsets:
  - addresses:
      - ip: 192.168.1.100
      - ip: 192.168.1.101
    ports:
      - port: 80
```

---

## Advanced Service Features

### 1. Session Affinity

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
  sessionAffinity: ClientIP  # Sticky sessions
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
```

### 2. Multi-Port Services

```yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port-service
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
    - name: https
      port: 443
      targetPort: 8443
    - name: metrics
      port: 9090
      targetPort: 9090
```

### 3. Headless Service (No Load Balancing)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: headless-service
spec:
  clusterIP: None  # Headless service
  selector:
    app: stateful-app
  ports:
    - port: 80
      targetPort: 80
```

```bash
# DNS returns all pod IPs (not service IP)
kubectl run test --image=busybox:1.35 -it --rm -- nslookup headless-service

# Use case: StatefulSets, direct pod access
```

### 4. External IPs

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-ip-service
spec:
  type: ClusterIP
  externalIPs:
    - 192.168.1.100  # Traffic to this IP routes to service
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
```

---

## Service Comparison

### Feature Comparison

| Feature | ClusterIP | NodePort | LoadBalancer | ExternalName |
|---------|-----------|----------|--------------|--------------|
| Internal access | ✅ | ✅ | ✅ | ✅ |
| External access | ❌ | ✅ | ✅ | N/A |
| Load balancing | ✅ | ✅ | ✅ | ❌ |
| External IP | ❌ | ❌ | ✅ | N/A |
| Cloud provider needed | ❌ | ❌ | ✅ | ❌ |
| Port range | Any | 30000-32767 | Any | N/A |

### When to Use What

| Scenario | Service Type |
|----------|--------------|
| Internal microservice | ClusterIP |
| Development/testing external access | NodePort |
| Production external access | LoadBalancer |
| Access external service | ExternalName |
| StatefulSet pod discovery | Headless (ClusterIP: None) |

---

## Complete Multi-Tier Example

```yaml
# Database (ClusterIP - internal only)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          env:
            - name: MYSQL_ROOT_PASSWORD
              value: password
---
apiVersion: v1
kind: Service
metadata:
  name: db-service
spec:
  type: ClusterIP
  selector:
    app: db
  ports:
    - port: 3306
      targetPort: 3306
---
# Backend API (ClusterIP - internal only)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: api
          image: backend:v1
          env:
            - name: DB_HOST
              value: "db-service"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - port: 80
      targetPort: 8080
---
# Frontend (LoadBalancer - external access)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: web
          image: frontend:v1
          env:
            - name: BACKEND_URL
              value: "http://backend-service"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
```

---

## Service Operations

### Create Service

```bash
# From deployment
kubectl expose deployment myapp --port=80 --target-port=8080 --type=ClusterIP

# From YAML
kubectl apply -f service.yaml

# Multiple services
kubectl apply -f services/
```

### View Services

```bash
# List all services
kubectl get services
kubectl get svc

# Specific service
kubectl get svc myapp-service
kubectl get svc myapp-service -o wide
kubectl get svc myapp-service -o yaml

# All namespaces
kubectl get svc --all-namespaces

# With labels
kubectl get svc -l app=web
```

### Describe Service

```bash
# Detailed info
kubectl describe svc myapp-service

# Shows:
# - Type, ClusterIP, External IP
# - Ports
# - Endpoints (pod IPs)
# - Session affinity
# - Events
```

### Edit Service

```bash
# Edit directly
kubectl edit svc myapp-service

# Update from file
kubectl apply -f service.yaml

# Patch specific field
kubectl patch svc myapp-service -p '{"spec":{"type":"LoadBalancer"}}'
```

### Delete Service

```bash
# Delete specific service
kubectl delete svc myapp-service

# Delete from file
kubectl delete -f service.yaml

# Delete multiple
kubectl delete svc service1 service2

# Delete all with label
kubectl delete svc -l app=web
```

---

## Troubleshooting Services

### Issue 1: Service Not Working

```bash
# Check service exists
kubectl get svc myapp-service

# Check endpoints (should have pod IPs)
kubectl get endpoints myapp-service
kubectl describe endpoints myapp-service

# If no endpoints, check selector
kubectl get pods -l app=myapp --show-labels

# Check if labels match
kubectl describe svc myapp-service | grep Selector
```

### Issue 2: Cannot Access Service

```bash
# Test from inside cluster
kubectl run test --image=busybox:1.35 -it --rm -- wget -O- http://myapp-service

# Check DNS
kubectl run test --image=busybox:1.35 -it --rm -- nslookup myapp-service

# Check pod is ready
kubectl get pods -l app=myapp

# Check pod logs
kubectl logs -l app=myapp
```

### Issue 3: LoadBalancer Pending

```bash
# Check if external IP is assigned
kubectl get svc myapp-lb

# If EXTERNAL-IP is <pending>:
# - Cloud provider not configured (on-premise)
# - No load balancer controller (need MetalLB for bare metal)
# - Permission issues with cloud provider

# For Minikube, start tunnel:
minikube tunnel
```

### Issue 4: Wrong Port

```bash
# Check service ports
kubectl describe svc myapp-service

# Output shows:
# Port:              80/TCP (service port)
# TargetPort:        8080/TCP (pod port)
# NodePort:          30080/TCP (node port, if NodePort type)

# Verify pod is listening on targetPort
kubectl exec <pod-name> -- netstat -tlnp
```

---

## Quick Reference

### Service Types Cheat Sheet

```bash
# ClusterIP (internal only)
kubectl expose deployment app --port=80 --type=ClusterIP

# NodePort (external via node IP)
kubectl expose deployment app --port=80 --type=NodePort

# LoadBalancer (external via LB)
kubectl expose deployment app --port=80 --type=LoadBalancer

# ExternalName (CNAME to external DNS)
kubectl create service externalname db --external-name mysql.example.com
```

### Common Commands

```bash
# Create
kubectl expose deployment NAME --port=PORT --type=TYPE
kubectl apply -f service.yaml

# View
kubectl get svc
kubectl describe svc NAME
kubectl get endpoints NAME

# Test
kubectl run test --image=curlimages/curl -it --rm -- curl http://SERVICE
kubectl port-forward svc/NAME 8080:80

# Edit
kubectl edit svc NAME
kubectl patch svc NAME -p '{"spec":{"type":"LoadBalancer"}}'

# Delete
kubectl delete svc NAME
```

### Service Ports Reference

```yaml
ports:
  - name: http              # Port name (optional)
    protocol: TCP           # TCP or UDP
    port: 80                # Service port (cluster IP)
    targetPort: 8080        # Pod port (where app listens)
    nodePort: 30080         # Node port (NodePort type only)
```

---

## Best Practices

### 1. Use Appropriate Service Type

```yaml
# ✅ Internal services
type: ClusterIP

# ✅ Production external
type: LoadBalancer

# ❌ Production external (not recommended)
type: NodePort
```

### 2. Name Ports

```yaml
# ✅ Good
ports:
  - name: http
    port: 80
  - name: https
    port: 443

# ❌ Bad
ports:
  - port: 80
  - port: 443
```

### 3. Set Resource Limits on Pods

Services route to pods, so pods need proper resources:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

### 4. Use Readiness Probes

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

Only ready pods receive traffic from service.

### 5. Label Everything Consistently

```yaml
# Deployment
metadata:
  labels:
    app: myapp
    version: v1

# Service selector
selector:
  app: myapp  # Must match deployment labels
```

### 6. Use DNS Names

```yaml
# ✅ Good - portable
env:
  - name: BACKEND_URL
    value: "http://backend-service"

# ❌ Bad - hardcoded IP
env:
  - name: BACKEND_URL
    value: "http://10.96.0.10"
```

### 7. Monitor Service Endpoints

```bash
# Regularly check
kubectl get endpoints

# Alert if no endpoints
```

---

## Summary

### Key Points

✅ **ClusterIP** - Internal only, default type
✅ **NodePort** - External via Node IP, development/testing
✅ **LoadBalancer** - External via cloud LB, production
✅ **ExternalName** - CNAME to external service
✅ **Services provide stable endpoints** - Pod IPs change, service IPs don't
✅ **DNS-based service discovery** - Use service names, not IPs
✅ **Load balancing built-in** - Traffic distributed across pods

### Decision Tree

```
Need external access?
├─ No  → ClusterIP
└─ Yes → 
    ├─ Development/Testing → NodePort
    ├─ Production → LoadBalancer
    └─ External service → ExternalName
```

---

