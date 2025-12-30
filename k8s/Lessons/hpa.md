# Kubernetes HPA (Horizontal Pod Autoscaler) Tutorial

## What is HPA?

**HPA** automatically scales the number of pods based on observed metrics (CPU, memory, or custom metrics).

```
Low Traffic:
┌─────────────┐
│     HPA     │  "CPU is low, scale down"
└─────────────┘
       │
       ▼
   [Pod] [Pod]  (2 pods)


High Traffic:
┌─────────────┐
│     HPA     │  "CPU is high, scale up!"
└─────────────┘
       │
       ▼
   [Pod] [Pod] [Pod] [Pod] [Pod]  (5 pods)
```

### How HPA Works

```
1. HPA checks metrics every 15 seconds (default)
2. Compares current metric to target
3. Calculates desired replicas:
   desiredReplicas = ceil[currentReplicas * (currentMetric / targetMetric)]
4. Scales deployment up or down
5. Repeat
```

---

## Prerequisites

### 1. Metrics Server Required

```bash
# Check if metrics-server is installed
kubectl get deployment metrics-server -n kube-system

# If not installed (Minikube)
minikube addons enable metrics-server

# If not installed (regular cluster)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify metrics are available
kubectl top nodes
kubectl top pods
```

### 2. Resource Requests Required

HPA needs pods to have resource requests defined:

```yaml
resources:
  requests:
    cpu: 100m      # Required for CPU-based HPA
    memory: 128Mi  # Required for memory-based HPA
```

---

## Creating HPA

### Method 1: Imperative (Simple)

```bash
# Create HPA for deployment
kubectl autoscale deployment myapp \
  --min=2 \
  --max=10 \
  --cpu-percent=80

# Parameters:
# --min: Minimum replicas
# --max: Maximum replicas
# --cpu-percent: Target CPU utilization (%)
```

### Method 2: YAML (Basic - CPU Only)

```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Method 3: YAML (Advanced - v2)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    # CPU metric
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # Target 70% CPU
    
    # Memory metric
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80  # Target 80% memory
```

---

## Complete Example

### Step 1: Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 2  # Initial replicas (HPA will override)
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
          resources:
            requests:
              cpu: 100m      # Required!
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
```

### Step 2: Create HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
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

### Step 3: Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
```

### Deploy Everything

```bash
# Apply all resources
kubectl apply -f deployment.yaml
kubectl apply -f hpa.yaml
kubectl apply -f service.yaml

# Verify HPA
kubectl get hpa
kubectl describe hpa web-app-hpa
```

---

## Testing HPA

### Generate Load

```bash
# Method 1: Using load generator pod
kubectl run load-generator --image=busybox:1.35 -it --rm -- /bin/sh

# Inside the pod, run:
while true; do wget -q -O- http://web-app; done

# Method 2: Multiple load generators
for i in {1..5}; do
  kubectl run load-gen-$i --image=busybox:1.35 -- /bin/sh -c \
    "while true; do wget -q -O- http://web-app; done" &
done

# Method 3: Apache Bench (from local machine)
kubectl port-forward svc/web-app 8080:80 &
ab -n 100000 -c 100 http://localhost:8080/
```

### Watch HPA Scale

```bash
# Watch HPA status
kubectl get hpa web-app-hpa -w

# Watch pods being created
kubectl get pods -w -l app=web

# Watch resource usage
watch kubectl top pods -l app=web

# Check HPA events
kubectl describe hpa web-app-hpa
```

### Stop Load

```bash
# Stop load generators
kubectl delete pod load-generator

# Or delete all load-gen pods
kubectl delete pods -l run=load-gen

# Watch scale down (takes ~5 minutes)
kubectl get hpa web-app-hpa -w
```

---

## HPA Metrics Types

### 1. Resource Metrics (CPU/Memory)

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Pods Metrics (Custom Metrics)

```yaml
metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"  # 1000 RPS per pod
```

### 3. Object Metrics

```yaml
metrics:
  - type: Object
    object:
      metric:
        name: requests-per-second
      describedObject:
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        name: main-route
      target:
        type: Value
        value: "10k"
```

### 4. External Metrics

```yaml
metrics:
  - type: External
    external:
      metric:
        name: queue_messages_ready
        selector:
          matchLabels:
            queue: "worker-tasks"
      target:
        type: AverageValue
        averageValue: "30"  # 30 messages per pod
```

---

## Advanced HPA Features

### 1. Multiple Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: multi-metric-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    # Scale based on CPU
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    
    # OR scale based on memory
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    
    # OR scale based on requests per second
    - type: Pods
      pods:
        metric:
          name: http_requests
        target:
          type: AverageValue
          averageValue: "1000"
```

**Note**: HPA uses the metric that suggests the highest number of replicas.

### 2. Scaling Behavior (K8s 1.23+)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: controlled-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
  
  # Control scaling behavior
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
        - type: Percent
          value: 50            # Scale down by max 50% of current pods
          periodSeconds: 60    # Per minute
        - type: Pods
          value: 2             # Or remove max 2 pods
          periodSeconds: 60    # Per minute
      selectPolicy: Min        # Use the policy that removes fewer pods
    
    scaleUp:
      stabilizationWindowSeconds: 0   # Scale up immediately
      policies:
        - type: Percent
          value: 100           # Double the pods
          periodSeconds: 60    # Per minute
        - type: Pods
          value: 4             # Or add max 4 pods
          periodSeconds: 60    # Per minute
      selectPolicy: Max        # Use the policy that adds more pods
```

### 3. Target Different Values

```yaml
metrics:
  # Utilization (percentage)
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  
  # Absolute value
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 500Mi
  
  # Pod metric
  - type: Pods
    pods:
      metric:
        name: packets-per-second
      target:
        type: AverageValue
        averageValue: "1k"
```

---

## HPA Operations

### View HPA

```bash
# List all HPAs
kubectl get hpa
kubectl get horizontalpodautoscaler  # Long form

# View specific HPA
kubectl get hpa myapp-hpa
kubectl get hpa myapp-hpa -o yaml

# Describe HPA (shows current/desired replicas, events)
kubectl describe hpa myapp-hpa

# Watch HPA
kubectl get hpa myapp-hpa -w
```

### Edit HPA

```bash
# Edit directly
kubectl edit hpa myapp-hpa

# Update min/max replicas
kubectl patch hpa myapp-hpa -p '{"spec":{"minReplicas":3}}'
kubectl patch hpa myapp-hpa -p '{"spec":{"maxReplicas":20}}'

# Update from file
kubectl apply -f hpa.yaml
```

### Delete HPA

```bash
# Delete HPA
kubectl delete hpa myapp-hpa

# Deployment keeps current replica count
# Set replicas manually if needed
kubectl scale deployment myapp --replicas=3
```

---

## HPA Best Practices

### 1. Set Appropriate Min/Max

```yaml
# ❌ Bad - Too narrow range
minReplicas: 3
maxReplicas: 4

# ✅ Good - Allows flexibility
minReplicas: 2
maxReplicas: 10

# ✅ Better - Based on traffic patterns
minReplicas: 3   # Handle baseline traffic
maxReplicas: 20  # Handle peak traffic
```

### 2. Set Realistic Targets

```yaml
# ❌ Bad - Too aggressive
targetCPUUtilizationPercentage: 30  # Wastes resources

# ❌ Bad - Too high
targetCPUUtilizationPercentage: 95  # Pods always overloaded

# ✅ Good - Balanced
targetCPUUtilizationPercentage: 70  # Efficient with headroom
```

### 3. Always Set Resource Requests

```yaml
# ✅ Required for HPA to work
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
# HPA waits for pods to be ready
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 5. Configure Scaling Behavior

```yaml
# Prevent flapping
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300  # Wait 5 min
  scaleUp:
    stabilizationWindowSeconds: 0    # Scale up quickly
```

### 6. Monitor HPA

```bash
# Regular checks
kubectl get hpa
kubectl top pods

# Set up alerts for:
# - HPA at max replicas
# - HPA unable to get metrics
# - Frequent scaling events
```

### 7. Test Scaling

```bash
# Always test HPA before production
# - Generate load
# - Verify scaling up works
# - Verify scaling down works
# - Check timing
```

---

## Troubleshooting

### Issue 1: HPA Shows "unknown" for Metrics

```bash
# Check HPA status
kubectl describe hpa myapp-hpa

# Common causes:
# 1. Metrics server not installed
kubectl get deployment metrics-server -n kube-system

# 2. No resource requests defined
kubectl get deployment myapp -o yaml | grep -A 5 resources

# 3. Pods not ready
kubectl get pods -l app=myapp

# Solutions:
# Install metrics-server
minikube addons enable metrics-server

# Add resource requests
kubectl set resources deployment myapp \
  --requests=cpu=100m,memory=128Mi
```

### Issue 2: HPA Not Scaling

```bash
# Check current metrics
kubectl top pods -l app=myapp

# Check HPA conditions
kubectl describe hpa myapp-hpa

# Check if at max replicas
kubectl get hpa myapp-hpa

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp | grep HPA

# Verify target deployment exists
kubectl get deployment myapp
```

### Issue 3: HPA Scaling Too Slowly

```bash
# Default: Metrics checked every 15s
# Scale up: Every 3 minutes (after threshold)
# Scale down: Every 5 minutes (after threshold)

# Solution: Adjust behavior (K8s 1.23+)
kubectl patch hpa myapp-hpa -p '
{
  "spec": {
    "behavior": {
      "scaleUp": {
        "stabilizationWindowSeconds": 0
      }
    }
  }
}'
```

### Issue 4: HPA Flapping (Scaling Up/Down Rapidly)

```bash
# Cause: Target too close to current usage

# Solution 1: Increase stabilization window
behavior:
  scaleDown:
    stabilizationWindowSeconds: 600  # 10 minutes

# Solution 2: Adjust target
targetCPUUtilizationPercentage: 60  # Lower target

# Solution 3: Limit scale rate
behavior:
  scaleDown:
    policies:
      - type: Pods
        value: 1           # Max 1 pod per period
        periodSeconds: 60
```

---

## HPA Calculation Example

```
Current situation:
- Deployment: 4 pods running
- Current CPU: 200m per pod (average)
- Requested CPU: 100m per pod
- Target CPU: 50% (50m out of 100m)

Current utilization:
200m / 100m = 200% (per pod)

Desired replicas calculation:
ceil[4 * (200% / 50%)] = ceil[4 * 4] = 16 pods

Result:
HPA scales from 4 to 16 pods (if maxReplicas allows)
```

---

## Quick Reference

### Create HPA

```bash
# Simple CPU-based
kubectl autoscale deployment NAME --min=2 --max=10 --cpu-percent=80

# From YAML
kubectl apply -f hpa.yaml
```

### View HPA

```bash
kubectl get hpa
kubectl describe hpa NAME
kubectl get hpa NAME -w
```

### Edit HPA

```bash
kubectl edit hpa NAME
kubectl patch hpa NAME -p '{"spec":{"maxReplicas":20}}'
```

### Delete HPA

```bash
kubectl delete hpa NAME
```

### Test HPA

```bash
# Generate load
kubectl run load-gen --image=busybox:1.35 -it --rm -- \
  /bin/sh -c "while true; do wget -q -O- http://SERVICE; done"

# Watch scaling
kubectl get hpa -w
kubectl get pods -w
kubectl top pods
```

---

## HPA Limits

- **Minimum scale interval**: 15 seconds (metric check)
- **Scale up delay**: ~3 minutes after threshold
- **Scale down delay**: ~5 minutes after threshold
- **Maximum pods**: Set by maxReplicas
- **Minimum pods**: Set by minReplicas

