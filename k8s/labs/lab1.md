# Kubernetes Exercises - Pods & ReplicaSets

## Exercise 1: Multi-Tier Application with Pods

### Scenario
You need to deploy a multi-tier application consisting of:
1. **Frontend**: Nginx web server
2. **Backend**: Python API server
3. **Cache**: Redis for caching

### Requirements

#### Part A: Create Individual Pods 

Create three separate pods with the following specifications:

**1. Frontend Pod (`frontend-pod.yaml`)**
- Image: `nginx`
- Port: 80

**2. Backend Pod (`backend-pod.yaml`)**
- Image: `python:3.11-slim`
- Command: `["python", "-m", "http.server", "8080"]`
- Port: 8080

**3. Cache Pod (`cache-pod.yaml`)**
- Image: `redis:7-alpine`
- Port: 6379

#### Part B: Verify and Test 

After creating the pods, perform these tasks:

1. Create the namespace first
2. Apply all three pod manifests
3. Verify all pods are running
4. Check the frontend pod logs
5. Execute into the backend pod and verify Python is running
7. Get the IP addresses of all three pods

---

## Exercise 2: Self-Healing Web Application with ReplicaSet

### Scenario
Deploy a scalable web application that can handle failures and scale based on demand.

### Requirements

#### Part A: Create ReplicaSet (`web-app-rs.yaml`) (15 points)

Create a ReplicaSet with these specifications:

- Replicas: 4
- image mongo

#### Part B: Operations and Testing

Perform the following operations and document your findings:

**1. Deployment and Verification**
```bash
# Create namespace
# Apply the ReplicaSet
# Verify exactly 4 pods are running
# Check ReplicaSet status
# View pod distribution across nodes (if multi-node)
```

**2. Self-Healing Test**
```bash
# Get list of all pods
# Delete 2 pods at random
# Watch pods being recreated
# Verify count returns to 4
# Document how long it took to heal
```

**3. Scaling Operations**
```bash
# Scale up to 8 replicas
# Wait for all pods to be ready
# Scale down to 2 replicas
# Observe which pods get terminated
# Scale back to 4 replicas
```

**5. Update Simulation**
```bash
# Edit the ReplicaSet to change image to nginx:1.25.4-alpine
# Check if existing pods updated (they won't)
# Delete all pods manually
# Verify new pods use updated image
```
