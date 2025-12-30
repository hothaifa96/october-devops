# Kubernetes Deployment Tutorial

## Table of Contents
1. [What is a Deployment?](#what-is-a-deployment)
2. [Deployment Architecture](#deployment-architecture)
3. [Basic Deployment](#basic-deployment)
4. [Rolling Updates](#rolling-updates)
5. [Rollback Strategies](#rollback-strategies)
6. [Horizontal Scaling](#horizontal-scaling)
7. [Vertical Scaling](#vertical-scaling)
8. [Update Strategies](#update-strategies)
9. [Hands-On Examples](#hands-on-examples)
10. [Best Practices](#best-practices)

---

## What is a Deployment?

A **Deployment** provides declarative updates for Pods and ReplicaSets. It's the recommended way to deploy applications in Kubernetes.

### Why Use Deployments Instead of ReplicaSets?

```
 ReplicaSet Alone:
   - Manual pod updates
   - No rollback capability
   - No update strategy
   - Manual version management

 Deployment:
   - Automatic rolling updates
   - Easy rollback
   - Update strategies (RollingUpdate, Recreate)
   - Version history
   - Manages ReplicaSets automatically
```

### Deployment Hierarchy

```
┌─────────────────────────────────────────────────────┐
│              Deployment (nginx-deployment)          │
│              Manages versions and updates           │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌─────────────────┐           ┌─────────────────┐
│ ReplicaSet v1   │           │ ReplicaSet v2   │
│ (Old version)   │           │ (New version)   │
│ replicas: 0     │           │ replicas: 3     │
└─────────────────┘           └─────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
               ┌────────┐        ┌────────┐       ┌────────┐
               │ Pod 1  │        │ Pod 2  │       │ Pod 3  │
               │ v2     │        │ v2     │       │ v2     │
               └────────┘        └────────┘       └────────┘
```

---

## Deployment Architecture

### How Deployments Work

```
User updates Deployment
        │
        ▼
Deployment Controller creates new ReplicaSet (v2)
        │
        ├─► Gradually scales up new ReplicaSet
        │   (adds new pods)
        │
        └─► Gradually scales down old ReplicaSet
            (removes old pods)
```

### Rolling Update Process

```
Initial State:
ReplicaSet v1: [Pod] [Pod] [Pod] (3 pods)

Step 1:
ReplicaSet v1: [Pod] [Pod] [Pod]
ReplicaSet v2: [Pod]              ← New pod created

Step 2:
ReplicaSet v1: [Pod] [Pod]        ← Old pod terminated
ReplicaSet v2: [Pod] [Pod]

Step 3:
ReplicaSet v1: [Pod]
ReplicaSet v2: [Pod] [Pod] [Pod]

Final State:
ReplicaSet v1: (empty - 0 pods)
ReplicaSet v2: [Pod] [Pod] [Pod]  ← All new pods
```

---

## Basic Deployment

### Simple Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
  labels:
    app: nginx
spec:
  # Number of pod replicas
  replicas: 3
  
  # Selector must match template labels
  selector:
    matchLabels:
      app: nginx
  
  # Pod template
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
```

### Create and Manage

```bash
# Create deployment
kubectl apply -f deployment.yaml

# View deployments
kubectl get deployments
kubectl get deploy  # Short form

# View details
kubectl describe deployment nginx-deployment

# View pods created by deployment
kubectl get pods -l app=nginx

# View ReplicaSets
kubectl get rs

# Delete deployment
kubectl delete deployment nginx-deployment
```

---

## Rolling Updates

### What is a Rolling Update?

A **rolling update** gradually replaces old pods with new ones, ensuring zero downtime.

### Rolling Update Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 10
  
  # Update strategy
  strategy:
    t RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max pods above desired during update
      maxUnavailable: 1  # Max pods unavailable during update
  
  # Minimum time pod must be ready
  minReadySeconds: 5
  
  # How long to wait for rollout to progress
  progressDeadlineSeconds: 600
  
  # Number of old ReplicaSets to keep
  revisionHistoryLimit: 10
  
  selector:
    matchLabels:
      app: nginx
  
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Understanding maxSurge and maxUnavailable

```
Initial: 10 replicas running

maxSurge: 2 (can have up to 12 pods during update)
maxUnavailable: 1 (minimum 9 pods must be available)

Update Process:
Step 1: Create 2 new pods (total: 12)
Step 2: Wait for new pods to be ready
Step 3: Terminate 1 old pod (total: 11)
Step 4: Create 1 new pod (total: 12)
Step 5: Repeat until all pods updated
```

### Performing Rolling Updates

#### Method 1: Update Image
```bash
# Update image to new version
kubectl set image deployment/nginx-deployment nginx=nginx:1.25.4

# Alternative: using --record flag (deprecated but useful)
kubectl set image deployment/nginx-deployment nginx=nginx:1.25.4 --record
```

#### Method 2: Edit Deployment
```bash
# Edit deployment directly
kubectl edit deployment nginx-deployment

# Change image version in editor
# Save and exit - update starts automatically
```

#### Method 3: Apply Updated YAML
```yaml
# Update your YAML file
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.4  # Changed version
```

```bash
# Apply changes
kubectl apply -f deployment.yaml
```

### Monitor Rolling Update

```bash
# Watch rollout status
kubectl rollout status deployment/nginx-deployment

# Watch pods during update
kubectl get pods -w -l app=nginx

# View rollout history
kubectl rollout history deployment/nginx-deployment

# View specific revision
kubectl rollout history deployment/nginx-deployment --revision=2

# Describe deployment (shows events)
kubectl describe deployment nginx-deployment
```

### Rolling Update Example

```bash
# Create initial deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
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
EOF

# Watch current state
kubectl get pods -l app=web -w

# In another terminal, perform update
kubectl set image deployment/web-app nginx=nginx:1.25.4

# Observe rolling update:
# - New pods created
# - Old pods terminated gradually
# - Always maintains minimum availability
```

---

## Rollback Strategies

### Why Rollback?

- New version has bugs
- Performance issues
- Configuration errors
- Failed health checks

### Rollback Commands

```bash
# Rollback to previous version
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=2

# View rollout history
kubectl rollout history deployment/nginx-deployment

# Pause rollout (stop in the middle)
kubectl rollout pause deployment/nginx-deployment

# Resume rollout
kubectl rollout resume deployment/nginx-deployment

# Restart deployment (recreate all pods)
kubectl rollout restart deployment/nginx-deployment
```

### Rollback Example

```bash
# 1. Create deployment (v1)
kubectl create deployment app --image=nginx:1.25.3 --replicas=3

# 2. Update to v2
kubectl set image deployment/app nginx=nginx:1.25.4 --record

# 3. Update to v3 (bad version)
kubectl set image deployment/app nginx=nginx:bad-version --record

# 4. Check rollout status (will fail)
kubectl rollout status deployment/app

# 5. View history
kubectl rollout history deployment/app

# 6. Rollback to v2
kubectl rollout undo deployment/app

# 7. Verify rollback
kubectl get pods
kubectl describe deployment app
```

### Automatic Rollback on Failure

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 5
  
  # Stop rollout if it doesn't progress within 10 minutes
  progressDeadlineSeconds: 600
  
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime
  
  template:
    spec:
      containers:
        - name: app
          image: myapp:v2
          
          # Readiness probe - prevents bad pods from receiving traffic
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
          
          # Liveness probe - restarts unhealthy pods
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
```

---

## Horizontal Scaling

### What is Horizontal Scaling?

**Horizontal scaling** = Adding or removing pod replicas (scale out/in)

```
Scale Up (3 → 5 pods):
Before: [Pod] [Pod] [Pod]
After:  [Pod] [Pod] [Pod] [Pod] [Pod]

Scale Down (5 → 2 pods):
Before: [Pod] [Pod] [Pod] [Pod] [Pod]
After:  [Pod] [Pod]
```

### Manual Horizontal Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment nginx-deployment --replicas=5

# Scale to 0 (stop all pods)
kubectl scale deployment nginx-deployment --replicas=0

# Conditional scaling (only if current replicas = 3)
kubectl scale deployment nginx-deployment --current-replicas=3 --replicas=5

# Scale multiple deployments
kubectl scale deployment app1 app2 app3 --replicas=5

# Scale all deployments with label
kubectl scale deployment -l app=web --replicas=10
```

### Horizontal Pod Autoscaler (HPA)

**HPA** automatically scales based on metrics (CPU, memory, custom metrics)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
    # Scale based on CPU
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # Target 70% CPU
    
    # Scale based on Memory
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80  # Target 80% memory
  
  # Scaling behavior
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
        - type: Percent
          value: 50  # Scale down by 50% of current pods
          periodSeconds: 15
        - type: Pods
          value: 2   # Or remove 2 pods
          periodSeconds: 15
      selectPolicy: Min  # Use the policy that scales less
    
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
        - type: Percent
          value: 100  # Double the pods
          periodSeconds: 15
        - type: Pods
          value: 4    # Or add 4 pods
          periodSeconds: 15
      selectPolicy: Max  # Use the policy that scales more
```

### HPA Commands

```bash
# Create HPA (simple)
kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80

# Create HPA from YAML
kubectl apply -f hpa.yaml

# View HPA
kubectl get hpa
kubectl get hpa nginx-hpa
kubectl describe hpa nginx-hpa

# Watch HPA in action
kubectl get hpa -w

# Delete HPA
kubectl delete hpa nginx-hpa
```

### HPA Example with Load Testing

```bash
# 1. Create deployment
kubectl create deployment web --image=nginx:1.25.3 --replicas=1

# 2. Set resource requests (required for CPU-based HPA)
kubectl set resources deployment web --requests=cpu=100m,memory=128Mi --limits=cpu=200m,memory=256Mi

# 3. Expose deployment
kubectl expose deployment web --port=80

# 4. Create HPA
kubectl autoscale deployment web --min=1 --max=10 --cpu-percent=50

# 5. Generate load (in separate terminal)
kubectl run -it load-generator --rm --image=busybox:1.35 --restart=Never -- /bin/sh
# Inside the pod:
while true; do wget -q -O- http://web; done

# 6. Watch HPA scale up
kubectl get hpa web -w

# 7. Stop load generator (Ctrl+C)
# Watch HPA scale down after cooldown period
```

### HPA with Custom Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: custom-metrics-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 20
  metrics:
    # Custom metric: requests per second
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"  # 1000 RPS per pod
    
    # External metric: SQS queue length
    - type: External
      external:
        metric:
          name: sqs_queue_length
          selector:
            matchLabels:
              queue: jobs
        target:
          type: Value
          value: "100"  # 100 messages per pod
```

---

## Vertical Scaling

### What is Vertical Scaling?

**Vertical scaling** = Changing resource requests/limits per pod (scale up/down)

```
Before:
[Pod]
CPU: 100m
Memory: 128Mi

After (Scaled Up):
[Pod]
CPU: 500m
Memory: 512Mi
```

### Manual Vertical Scaling

```bash
# Update resources
kubectl set resources deployment nginx-deployment \
  --requests=cpu=200m,memory=256Mi \
  --limits=cpu=500m,memory=512Mi

# This triggers a rolling update to restart pods with new resources
```

### Vertical Pod Autoscaler (VPA)

**VPA** automatically adjusts CPU and memory requests/limits

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  
  # Update mode
  updatePolicy:
    updateMode: "Auto"  # Options: Off, Initial, Recreate, Auto
  
  # Resource policy
  resourcePolicy:
    containerPolicies:
      - containerName: nginx
        minAllowed:
          cpu: 50m
          memory: 64Mi
        maxAllowed:
          cpu: 1
          memory: 1Gi
        controlledResources:
          - cpu
          - memory
        # Controlled values
        controlledValues: RequestsAndLimits  # or RequestsOnly
```

### VPA Update Modes

```
Off:
  - Only provides recommendations
  - No automatic changes

Initial:
  - Sets resources when pod is created
  - No updates to running pods

Recreate:
  - Evicts and recreates pods with new resources
  - Causes downtime

Auto:
  - Updates during eviction (e.g., node maintenance)
  - No forced downtime
```

### VPA Example

```bash
# 1. Install VPA (if not installed)
# Follow: https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler

# 2. Create deployment
kubectl create deployment app --image=nginx:1.25.3 --replicas=2

# 3. Create VPA
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: nginx
        minAllowed:
          cpu: 100m
          memory: 128Mi
        maxAllowed:
          cpu: 500m
          memory: 512Mi
EOF

# 4. View VPA recommendations
kubectl describe vpa app-vpa

# 5. Check pod resources after VPA adjusts them
kubectl get pods
kubectl describe pod <pod-name> | grep -A 10 "Requests:"
```

### HPA + VPA Together

```
┌──────────────────────────────────────────┐
│          Your Application                │
│                                          │
│  HPA: Scales number of pods ←──────┐    │
│  VPA: Scales resources per pod ←───┤    │
│                                     │    │
│  [Pod 100m/128Mi] [Pod 100m/128Mi] │    │
│         ↓ VPA increases             │    │
│  [Pod 200m/256Mi] [Pod 200m/256Mi] │    │
│         ↓ HPA adds more pods        │    │
│  [Pod 200m/256Mi] [Pod 200m/256Mi] │    │
│  [Pod 200m/256Mi] [Pod 200m/256Mi] │    │
└──────────────────────────────────────────┘
```

**Best Practice**: Use HPA for horizontal scaling, use VPA for initial sizing

---

## Update Strategies

### 1. RollingUpdate (Default)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%        # Can be percentage or number
    maxUnavailable: 25%  # Can be percentage or number
```

**When to use:**
- Most applications
- Need zero downtime
- Stateless applications

### 2. Recreate

```yaml
strategy:
  type: Recreate
```

**Process:**
1. Terminate all old pods
2. Wait for termination
3. Create all new pods

**When to use:**
- Cannot run old and new versions simultaneously
- Database migrations
- Stateful apps with volume conflicts
- Acceptable downtime

### 3. Blue-Green Deployment (Manual)

```yaml
# Blue (current version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
        - name: app
          image: myapp:v1
---
# Green (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
        - name: app
          image: myapp:v2
---
# Service (switch between blue and green)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: blue  # Switch to 'green' to cutover
  ports:
    - port: 80
```

```bash
# Deploy green version
kubectl apply -f app-green.yaml

# Test green version
kubectl port-forward deployment/app-green 8080:80

# Switch traffic to green
kubectl patch service myapp -p '{"spec":{"selector":{"version":"green"}}}'

# If problems, rollback to blue
kubectl patch service myapp -p '{"spec":{"selector":{"version":"blue"}}}'

# Delete old blue deployment
kubectl delete deployment app-blue
```

### 4. Canary Deployment

```yaml
# Main deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: stable
    spec:
      containers:
        - name: app
          image: myapp:v1
---
# Canary deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: canary
    spec:
      containers:
        - name: app
          image: myapp:v2
---
# Service (routes to both)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp  # Matches both stable and canary
  ports:
    - port: 80
```

```bash
# Start with stable only
kubectl apply -f app-stable.yaml

# Deploy canary (10%)
kubectl apply -f app-canary.yaml

# Monitor canary
kubectl logs -f deployment/app-canary

# If successful, scale up canary
kubectl scale deployment app-canary --replicas=5
kubectl scale deployment app-stable --replicas=5

# Eventually replace stable
kubectl scale deployment app-canary --replicas=10
kubectl scale deployment app-stable --replicas=0
kubectl delete deployment app-stable
```

---

## Hands-On Examples

### Example 1: Basic Deployment with Rolling Update

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.3
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
```

```bash
# Deploy
kubectl apply -f webapp.yaml

# Watch deployment
kubectl rollout status deployment/webapp

# Update image
kubectl set image deployment/webapp nginx=nginx:1.25.4

# Watch rolling update
kubectl get pods -w -l app=webapp

# Check rollout history
kubectl rollout history deployment/webapp
```

### Example 2: Deployment with HPA

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scalable-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scalable
  template:
    metadata:
      labels:
        app: scalable
    spec:
      containers:
        - name: app
          image: nginx:1.25.3
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scalable-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scalable-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

```bash
# Deploy
kubectl apply -f scalable-app.yaml

# Check HPA
kubectl get hpa

# Generate load and watch scaling
kubectl run load-gen --image=busybox:1.35 -it --rm -- /bin/sh
while true; do wget -q -O- http://scalable-app; done

# Watch pods scale
kubectl get pods -w -l app=scalable
```

### Example 3: Recreate Strategy

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  replicas: 1
  strategy:
    type: Recreate  # Kill all pods, then create new ones
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
        - name: postgres
          image: postgres:15
          env:
            - name: POSTGRES_PASSWORD
              value: password
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: data
          emptyDir: {}
```

---

## Best Practices

### 1. Always Set Resource Requests and Limits

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

### 2. Use Readiness Probes

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 3. Set Appropriate maxSurge and maxUnavailable

```yaml
# For critical services (zero downtime)
rollingUpdate:
  maxSurge: 25%
  maxUnavailable: 0

# For faster updates (some downtime acceptable)
rollingUpdate:
  maxSurge: 50%
  maxUnavailable: 25%
```

### 4. Keep Revision History

```yaml
spec:
  revisionHistoryLimit: 10  # Keep last 10 ReplicaSets
```

### 5. Use Labels Consistently

```yaml
metadata:
  labels:
    app: myapp
    version: v1.0.0
    environment: production
```

### 6. Set Progress Deadlines

```yaml
spec:
  progressDeadlineSeconds: 600  # Fail if not progressing after 10 min
```

### 7. Use HPA for Dynamic Workloads

```yaml
# Auto-scale between 2-10 pods
kubectl autoscale deployment myapp --min=2 --max=10 --cpu-percent=70
```

### 8. Test Updates in Staging First

```bash
# Deploy to staging
kubectl apply -f deployment.yaml -n staging

# Test thoroughly
# Then deploy to production
kubectl apply -f deployment.yaml -n production
```

### 9. Monitor Rollouts

```bash
# Watch rollout
kubectl rollout status deployment/myapp

# Set up alerts for failed rollouts
```

### 10. Document Deployment Strategy

```yaml
metadata:
  annotations:
    description: "Main web application"
    strategy: "Rolling update with canary testing"
    rollback-plan: "kubectl rollout undo deployment/webapp"
```

---

## Quick Reference

### Deployment Commands

```bash
# Create
kubectl create deployment app --image=nginx:1.25.3 --replicas=3
kubectl apply -f deployment.yaml

# View
kubectl get deployments
kubectl get deploy app
kubectl describe deploy app

# Update
kubectl set image deployment/app nginx=nginx:1.25.4
kubectl edit deployment app
kubectl apply -f deployment.yaml

# Scale
kubectl scale deployment app --replicas=5
kubectl autoscale deployment app --min=2 --max=10 --cpu-percent=80

# Rollout
kubectl rollout status deployment/app
kubectl rollout history deployment/app
kubectl rollout undo deployment/app
kubectl rollout restart deployment/app
kubectl rollout pause deployment/app
kubectl rollout resume deployment/app

# Delete
kubectl delete deployment app
```

### Scaling Commands

```bash
# Manual horizontal scaling
kubectl scale deployment app --replicas=10

# HPA
kubectl autoscale deployment app --min=2 --max=10 --cpu-percent=70
kubectl get hpa
kubectl delete hpa app

# Manual vertical scaling
kubectl set resources deployment app \
  --requests=cpu=200m,memory=256Mi \
  --limits=cpu=500m,memory=512Mi
```

---

## Summary

### Key Concepts

✅ **Deployments manage ReplicaSets** - You don't manage ReplicaSets directly
✅ **Rolling updates** - Zero downtime deployments
✅ **Easy rollbacks** - Undo bad deployments quickly
✅ **Horizontal scaling** - Add/remove pods (HPA)
✅ **Vertical scaling** - Adjust resources per pod (VPA)
✅ **Multiple strategies** - RollingUpdate, Recreate, Blue-Green, Canary

### When to Use What

| Scenario | Solution |
|----------|----------|
| Standard web app | Deployment with RollingUpdate |
| Need zero downtime | maxUnavailable: 0 |
| Fast updates | maxSurge: 100% |
| Variable traffic | HPA |
| Unknown resource needs | VPA |
| Database migration | Recreate strategy |
| A/B testing | Blue-Green or Canary |

---

**Master Deployments and you've mastered Kubernetes application management! 🚀**