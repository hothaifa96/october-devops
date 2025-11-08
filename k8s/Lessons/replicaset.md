# Kubernetes ReplicaSet Tutorial

## What is a ReplicaSet?

A **ReplicaSet** ensures that a specified number of pod replicas are running at any given time. If a pod crashes or is deleted, the ReplicaSet automatically creates a new one.

```
┌─────────────────────────────────────────────────────────┐
│                    ReplicaSet (nginx-rs)                │
│                    Desired: 5 pods                      │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Pod 1   │  │ Pod 2   │  │ Pod 3   │  │ Pod 4   │     │
│  │ nginx   │  │ nginx   │  │ nginx   │  │ nginx   │     │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │
│                                                         │
│  ┌─────────┐                                            │
│  │ Pod 5   │  ← Pod 3 crashes? RS creates Pod 6 ─┐      │
│  │ nginx   │                                     │      │
│  └─────────┘                                     ▼      │
│                                            ┌─────────┐  │
│                                            │ Pod 6   │  │
│                                            │ nginx   │  │
│                                            └─────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Key Features
- Maintains desired number of pod replicas
- Self-healing (replaces failed pods automatically)
- Scaling up/down
- Label selector for pod management
- **Note**: In practice, use **Deployments** instead (they manage ReplicaSets for you)

---

## Dissecting Your Example

```yaml
apiVersion: apps/v1 # API version for ReplicaSet
kind: ReplicaSet
metadata:
  name: nginx-rs
  namespace: default
spec:
  replicas: 5
  selector:
    matchLabels:
      app: nginx
  template:
   metadata:
     name: nginx-pod
     labels:
      app: nginx
   spec:
    containers:
    - name: nginx-continer
      image: nginx
      ports:
        - containerPort: 80
```

### Breaking It Down

#### 1. API Version and Kind
```yaml
apiVersion: apps/v1  # ReplicaSet is in the apps/v1 API group
kind: ReplicaSet
```
- **apps/v1**: Stable API for workload controllers
- **kind**: Defines this as a ReplicaSet

#### 2. Metadata
```yaml
metadata:
  name: nginx-rs        # Name of the ReplicaSet
  namespace: default    # Namespace where it lives
```
- ReplicaSet name must be unique within namespace
- All pods created will have this RS as owner

#### 3. Replicas
```yaml
spec:
  replicas: 5  # Always maintain 5 pods
```
- **Desired state**: 5 pods should always be running
- If pod dies → RS creates new one
- If manually delete pod → RS recreates it
- Scale by changing this number

#### 4. Selector (CRITICAL)
```yaml
selector:
  matchLabels:
    app: nginx  # Select pods with label app=nginx
```
- **Purpose**: Tells ReplicaSet which pods it manages
- **Must match** the labels in template.metadata.labels
- **Immutable**: Cannot be changed after creation

#### 5. Template (Pod Template)
```yaml
template:
  metadata:
    name: nginx-pod     # Note: Actual pod names will be different
    labels:
      app: nginx        # MUST match selector.matchLabels
  spec:
    containers:
    - name: nginx-continer  # Typo: should be nginx-container
      image: nginx
      ports:
        - containerPort: 80
```
- **Template**: Blueprint for creating pods
- **Labels**: Must match selector
- **Pod naming**: Actual pods get names like `nginx-rs-xyz12`

---

## How ReplicaSet Works

### Creation Flow
```
1. You create ReplicaSet with replicas: 5
   │
   ▼
2. ReplicaSet Controller checks: How many pods with label app=nginx exist?
   │
   ▼
3. Found 0 pods → Need 5 more
   │
   ▼
4. Creates 5 pods using the template
   │
   ▼
5. Continuously monitors pod count
```

### Self-Healing
```
Running: 5 pods
   │
   ▼
Pod 3 crashes and dies
   │
   ▼
ReplicaSet detects: Only 4 pods running
   │
   ▼
Creates new pod to reach 5
   │
   ▼
Back to: 5 pods running
```

### Scaling
```bash
# Scale up to 10 replicas
kubectl scale replicaset nginx-rs --replicas=10

# Scale down to 2 replicas
kubectl scale replicaset nginx-rs --replicas=2
```

---

## Complete ReplicaSet Example (Corrected)

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-rs
  namespace: default
  labels:
    app: nginx
    tier: frontend
spec:
  # Number of pod replicas
  replicas: 5
  
  # Selector MUST match template labels
  selector:
    matchLabels:
      app: nginx
      tier: frontend
  
  # Pod template
  template:
    metadata:
      labels:
        app: nginx        # Must match selector
        tier: frontend    # Must match selector
        version: v1.0.0   # Additional labels OK
    spec:
      containers:
        - name: nginx-container  
          image: nginx:1.25.3    # Specific version
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
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

---

## Essential Commands

### Create and View
```bash
# Create ReplicaSet
kubectl apply -f replicaset.yaml

# View ReplicaSets
kubectl get replicaset
kubectl get rs  # Short form

# Detailed info
kubectl describe replicaset nginx-rs

# View with more details
kubectl get rs nginx-rs -o wide

# Watch in real-time
kubectl get pods -w -l app=nginx
```

### Scaling
```bash
# Scale to 10 replicas
kubectl scale replicaset nginx-rs --replicas=10

# Scale to 0 (stop all pods)
kubectl scale replicaset nginx-rs --replicas=0

# View scaling events
kubectl describe rs nginx-rs | grep -A 10 Events
```

### Pod Management
```bash
# View pods created by ReplicaSet
kubectl get pods -l app=nginx

# Delete a pod (ReplicaSet will recreate it)
kubectl delete pod nginx-rs-xyz12

# Watch pod recreation
kubectl get pods -w -l app=nginx
```

### Edit and Update
```bash
# Edit ReplicaSet (opens editor)
kubectl edit replicaset nginx-rs

# Update from file
kubectl apply -f replicaset.yaml

# Note: Changing template doesn't update existing pods!
# You must delete old pods manually for updates
```

### Delete
```bash
# Delete ReplicaSet and all its pods
kubectl delete replicaset nginx-rs

# Delete ReplicaSet but keep pods running
kubectl delete replicaset nginx-rs --cascade=orphan
```

---

## Hands-On Examples

### Example 1: Basic ReplicaSet
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web-rs
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
```

```bash
# Create
kubectl apply -f web-rs.yaml

# Verify 3 pods created
kubectl get pods -l app=web

# Test self-healing: delete a pod
kubectl delete pod web-rs-xxxxx

# Watch new pod being created
kubectl get pods -l app=web -w

# Cleanup
kubectl delete rs web-rs
```

### Example 2: Scaling Demo
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: scale-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scale-demo
  template:
    metadata:
      labels:
        app: scale-demo
    spec:
      containers:
        - name: busybox
          image: busybox:1.35
          command: ['sh', '-c', 'echo "Pod $HOSTNAME started"; sleep 3600']
```

```bash
# Create with 2 replicas
kubectl apply -f scale-demo.yaml
kubectl get pods -l app=scale-demo

# Scale up to 5
kubectl scale rs scale-demo --replicas=5
kubectl get pods -l app=scale-demo

# Scale down to 1
kubectl scale rs scale-demo --replicas=1
kubectl get pods -l app=scale-demo -w

# Cleanup
kubectl delete rs scale-demo
```

### Example 3: Advanced Selector
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: advanced-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
    matchExpressions:
      - key: environment
        operator: In
        values:
          - production
          - staging
      - key: tier
        operator: NotIn
        values:
          - cache
  template:
    metadata:
      labels:
        app: myapp
        environment: production
        tier: frontend
    spec:
      containers:
        - name: app
          image: nginx:1.25.3
```

---

## Common Issues and Solutions

### Issue 1: Pods Not Created
```bash
# Check ReplicaSet status
kubectl describe rs nginx-rs

# Look for errors in events
kubectl get events --sort-by=.metadata.creationTimestamp

# Common causes:
# - Selector doesn't match template labels
# - Invalid image name
# - Insufficient cluster resources
```

**Fix:**
```yaml
# Ensure labels match
selector:
  matchLabels:
    app: nginx  # Must match ↓
template:
  metadata:
    labels:
      app: nginx  # Must match ↑
```

### Issue 2: Can't Update Pods
```bash
# Problem: Changed template but pods still old

# ReplicaSet doesn't auto-update pods!
# Solution: Delete old pods manually
kubectl delete pods -l app=nginx

# Or use Deployment instead (recommended)
```

### Issue 3: Too Many Pods
```bash
# Manually created pods with same labels?
kubectl get pods -l app=nginx --show-labels

# ReplicaSet adopts ANY pod with matching labels
# Delete extra pods or change their labels
kubectl label pod extra-pod app-  # Remove label
```

### Issue 4: Can't Delete ReplicaSet
```bash
# ReplicaSet won't delete?
kubectl get rs nginx-rs -o yaml | grep finalizers

# Force delete
kubectl delete rs nginx-rs --grace-period=0 --force
```

---

## ReplicaSet vs Deployment

### Why Use Deployment Instead?

```
Deployment (Recommended)
    │
    ├─ Manages ReplicaSets
    │   │
    │   └─ ReplicaSet v1 (old version)
    │   └─ ReplicaSet v2 (new version) ← Active
    │       │
    │       └─ Pod 1
    │       └─ Pod 2
    │       └─ Pod 3
```

**Deployment Advantages:**
- ✅ Rolling updates
- ✅ Rollback capability
- ✅ Update strategy control
- ✅ Manages ReplicaSets for you
- ✅ Pause/Resume updates

**Use ReplicaSet directly when:**
- ❓ Almost never! Use Deployments instead
- ❓ Learning/understanding Kubernetes internals
- ❓ Very specific edge cases

---

## Quick Reference

### Create
```bash
kubectl apply -f replicaset.yaml
kubectl create -f replicaset.yaml
```

### View
```bash
kubectl get rs
kubectl get rs nginx-rs
kubectl describe rs nginx-rs
kubectl get rs -o wide
kubectl get rs --all-namespaces
```

### Scale
```bash
kubectl scale rs nginx-rs --replicas=5
kubectl scale rs nginx-rs --replicas=0
```

### Delete
```bash
kubectl delete rs nginx-rs
kubectl delete rs nginx-rs --cascade=orphan
kubectl delete rs --all
```

### Get Pods
```bash
kubectl get pods -l app=nginx
kubectl get pods --selector=app=nginx
```

### Edit
```bash
kubectl edit rs nginx-rs
kubectl apply -f replicaset.yaml
```

### Troubleshoot
```bash
kubectl describe rs nginx-rs
kubectl get events
kubectl logs <pod-name>
```

---

## Best Practices

### 1. ⚠️ Use Deployments, Not ReplicaSets
```yaml
#  Don't use ReplicaSet directly
kind: ReplicaSet

#  Use Deployment instead
kind: Deployment  # Deployment manages ReplicaSets
```

### 2. Always Set Resource Limits
```yaml
spec:
  template:
    spec:
      containers:
        - name: nginx
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "128Mi"
              cpu: "100m"
```

### 3. Use Health Checks
```yaml
spec:
  template:
    spec:
      containers:
        - name: nginx
          livenessProbe:
            httpGet:
              path: /
              port: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
```

### 4. Use Specific Image Tags
```yaml
# ❌ Bad
image: nginx

# ✅ Good
image: nginx:1.25.3
```

### 5. Label Everything
```yaml
metadata:
  labels:
    app: myapp
    version: v1.0.0
    environment: production
spec:
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
```

---

## Testing Self-Healing

```bash
# 1. Create ReplicaSet
kubectl apply -f replicaset.yaml

# 2. Watch pods
kubectl get pods -w -l app=nginx

# 3. In another terminal, delete a pod
kubectl delete pod nginx-rs-xxxxx

# 4. Watch ReplicaSet recreate it automatically!

# 5. Try deleting multiple pods
kubectl delete pods -l app=nginx --field-selector=status.phase=Running

# 6. All pods will be recreated!
```

---

## Summary

### Key Points
- ✅ ReplicaSet maintains desired number of pods
- ✅ Automatically replaces failed pods (self-healing)
- ✅ Selector must match template labels (immutable)
- ✅ Easy scaling with `kubectl scale`
- ⚠️ Doesn't update existing pods when template changes
- ⚠️ Use Deployments instead in production

### ReplicaSet Formula
```
Desired State (replicas: 5)
      │
      ▼
ReplicaSet Controller
      │
      ▼
Observes Current State (3 pods)
      │
      ▼
Takes Action (creates 2 more pods)
      │
      ▼
Current State = Desired State ✅
```

