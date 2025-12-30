# Kubernetes ConfigMap Tutorial

## What is a ConfigMap?

A **ConfigMap** stores non-sensitive configuration data as key-value pairs. It separates configuration from application code.

```
┌─────────────────────────────────────────────┐
│            ConfigMap                        │
│  ┌───────────────────────────────────────┐  │
│  │  database.host = mysql.prod.com       │  │
│  │  database.port = 3306                 │  │
│  │  app.name = MyApp                     │  │
│  │  log.level = INFO                     │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
   Environment Variables    Volume Files
   in Pod                   in Pod
```

### Why Use ConfigMaps?

 Easy to update without rebuilding images
 Separate config from code
 Reuse same config across multiple pods
 Environment-specific configurations
 **NOT for sensitive data** (use Secrets instead)

---

## Creating ConfigMaps

### Method 1: From Literal Values

```bash
# Create ConfigMap with key-value pairs
kubectl create configmap app-config \
  --from-literal=database.host=mysql \
  --from-literal=database.port=3306 \
  --from-literal=app.name=MyApp

# View it
kubectl get configmap app-config -o yaml
```

### Method 2: From File

```bash
# Create a config file
cat > app.properties <<EOF
database.host=mysql
database.port=3306
app.name=MyApp
log.level=INFO
EOF

# Create ConfigMap from file
kubectl create configmap app-config --from-file=app.properties

# Or specify custom key name
kubectl create configmap app-config --from-file=config=app.properties
```

### Method 3: From Directory

```bash
# Create multiple config files
mkdir configs
echo "server.port=8080" > configs/server.conf
echo "log.level=DEBUG" > configs/logging.conf

# Create ConfigMap from directory
kubectl create configmap app-config --from-file=configs/
```

### Method 4: From YAML

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  # Simple key-value pairs
  database.host: "mysql"
  database.port: "3306"
  app.name: "MyApp"
  
  # Multi-line values (files)
  app.properties: |
    server.port=8080
    server.host=0.0.0.0
    log.level=INFO
  
  nginx.conf: |
    server {
      listen 80;
      server_name example.com;
      location / {
        proxy_pass http://backend:8080;
      }
    }
```

```bash
# Apply
kubectl apply -f configmap.yaml
```

---

## Using ConfigMaps in Pods

### Method 1: Environment Variables (Individual Keys)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:v1
      env:
        # Single value from ConfigMap
        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database.host
        
        - name: DATABASE_PORT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database.port
```

### Method 2: All Keys as Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:v1
      envFrom:
        # All keys become environment variables
        - configMapRef:
            name: app-config
```

### Method 3: Environment Variables with Prefix

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:v1
      envFrom:
        - prefix: "CONFIG_"  # Adds prefix to all keys
          configMapRef:
            name: app-config
```

### Method 4: Mount as Volume (Files)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: nginx:1.25.3
      volumeMounts:
        # Mount entire ConfigMap as files
        - name: config-volume
          mountPath: /etc/config
          readOnly: true
  
  volumes:
    - name: config-volume
      configMap:
        name: app-config
```

### Method 5: Mount Specific Keys as Files

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
    - name: nginx
      image: nginx:1.25.3
      volumeMounts:
        - name: config-volume
          mountPath: /etc/nginx/conf.d
  
  volumes:
    - name: config-volume
      configMap:
        name: app-config
        items:
          # Only mount specific keys
          - key: nginx.conf
            path: default.conf  # Custom filename
            mode: 0644         # File permissions
```

---

## Complete Example

### Create ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
data:
  # Environment variables
  APP_ENV: "production"
  LOG_LEVEL: "info"
  DATABASE_URL: "mysql://db:3306/myapp"
  
  # Config file
  app.conf: |
    [server]
    port = 8080
    host = 0.0.0.0
    
    [database]
    max_connections = 100
    timeout = 30
  
  # Nginx config
  nginx.conf: |
    server {
      listen 80;
      location / {
        proxy_pass http://backend:8080;
      }
    }
```

### Use in Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
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
        - name: app
          image: myapp:v1
          
          # Individual env vars
          env:
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: web-config
                  key: APP_ENV
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: web-config
                  key: LOG_LEVEL
          
          # Mount config files
          volumeMounts:
            - name: config
              mountPath: /etc/app
              readOnly: true
        
        - name: nginx
          image: nginx:1.25.3
          volumeMounts:
            - name: nginx-config
              mountPath: /etc/nginx/conf.d
      
      volumes:
        # App config volume
        - name: config
          configMap:
            name: web-config
            items:
              - key: app.conf
                path: application.conf
        
        # Nginx config volume
        - name: nginx-config
          configMap:
            name: web-config
            items:
              - key: nginx.conf
                path: default.conf
```

---

## ConfigMap Operations

### View ConfigMaps

```bash
# List all
kubectl get configmaps
kubectl get cm  # Short form

# View specific ConfigMap
kubectl get configmap app-config -o yaml
kubectl describe configmap app-config

# Get specific key value
kubectl get configmap app-config -o jsonpath='{.data.database\.host}'
```

### Update ConfigMaps

```bash
# Method 1: Edit directly
kubectl edit configmap app-config

# Method 2: Replace from file
kubectl create configmap app-config --from-file=app.properties --dry-run=client -o yaml | kubectl apply -f -

# Method 3: Apply updated YAML
kubectl apply -f configmap.yaml

# Note: Pods don't auto-reload! Need to restart:
kubectl rollout restart deployment/web-app
```

### Delete ConfigMaps

```bash
# Delete specific ConfigMap
kubectl delete configmap app-config

# Delete multiple
kubectl delete configmap config1 config2 config3

# Delete all in namespace
kubectl delete configmap --all
```

---

## ConfigMap Best Practices

### 1. One ConfigMap Per Application

```bash
# ✅ Good
kubectl create configmap frontend-config --from-file=frontend.conf
kubectl create configmap backend-config --from-file=backend.conf

# ❌ Bad - mixing configs
kubectl create configmap app-config --from-file=everything/
```

### 2. Use Namespaces for Environments

```bash
# Production config
kubectl create configmap app-config --from-file=prod.conf -n production

# Development config
kubectl create configmap app-config --from-file=dev.conf -n development
```

### 3. Never Store Secrets in ConfigMaps

```yaml
# ❌ BAD - Passwords in ConfigMap
data:
  db.password: "SuperSecret123"

# ✅ GOOD - Use Secret instead
```

### 4. Use Labels

```yaml
metadata:
  name: app-config
  labels:
    app: myapp
    environment: production
    version: v1.0.0
```

### 5. Immutable ConfigMaps (K8s 1.21+)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
immutable: true  # Cannot be changed
data:
  app.name: "MyApp"
```

**Benefits:**
- Protects from accidental updates
- Better performance (no watches needed)
- Must create new ConfigMap to change

---

## Testing ConfigMap in Pods

```bash
# Create ConfigMap
kubectl create configmap test-config \
  --from-literal=key1=value1 \
  --from-literal=key2=value2

# Create test pod
kubectl run test --image=busybox:1.35 -it --rm --restart=Never \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "test",
      "image": "busybox:1.35",
      "command": ["sh"],
      "envFrom": [{"configMapRef": {"name": "test-config"}}]
    }]
  }
}' -- sh

# Inside pod, check env vars
echo $key1
echo $key2
env | grep key
```

---

## Common Use Cases

### 1. Application Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-settings
data:
  server.port: "8080"
  log.level: "INFO"
  feature.flags: "feature1,feature2,feature3"
```

### 2. Database Connection Strings

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
data:
  database.url: "postgresql://db-service:5432/mydb"
  database.max-connections: "50"
  database.timeout: "30"
```

### 3. Nginx Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    worker_processes 4;
    events {
      worker_connections 1024;
    }
    http {
      server {
        listen 80;
        location / {
          proxy_pass http://backend:8080;
        }
      }
    }
```

### 4. Environment-Specific Settings

```bash
# Production
kubectl create configmap app-config \
  --from-literal=api.url=https://api.prod.com \
  --from-literal=cache.ttl=3600 \
  -n production

# Staging
kubectl create configmap app-config \
  --from-literal=api.url=https://api.staging.com \
  --from-literal=cache.ttl=60 \
  -n staging
```

---

## Troubleshooting

### Issue 1: ConfigMap Not Found

```bash
# Error: configmap "app-config" not found

# Check if it exists
kubectl get configmap

# Check namespace
kubectl get configmap -n <namespace>

# Create it
kubectl create configmap app-config --from-literal=key=value
```

### Issue 2: Pod Not Getting ConfigMap Updates

```bash
# ConfigMaps mounted as volumes update automatically (with delay)
# Environment variables DO NOT update automatically

# Solution: Restart pods
kubectl rollout restart deployment/myapp

# Or delete pods to force recreation
kubectl delete pods -l app=myapp
```

### Issue 3: Key Not Found

```bash
# Error: key "database.host" not found in ConfigMap

# Check available keys
kubectl describe configmap app-config

# Verify key name (case-sensitive!)
kubectl get configmap app-config -o jsonpath='{.data}'
```

### Issue 4: File Permission Issues

```yaml
# Set correct permissions when mounting
volumes:
  - name: config
    configMap:
      name: app-config
      defaultMode: 0644  # Default file permissions
      items:
        - key: config.json
          path: app.json
          mode: 0600  # Specific file permissions
```

---

## Quick Reference

### Create ConfigMap

```bash
# From literals
kubectl create configmap NAME --from-literal=key=value

# From file
kubectl create configmap NAME --from-file=file.conf

# From directory
kubectl create configmap NAME --from-file=config-dir/

# From YAML
kubectl apply -f configmap.yaml
```

### View ConfigMap

```bash
kubectl get configmap
kubectl get cm NAME -o yaml
kubectl describe cm NAME
```

### Use in Pod

```yaml
# As environment variable
env:
  - name: VAR_NAME
    valueFrom:
      configMapKeyRef:
        name: CONFIG_NAME
        key: key_name

# As volume
volumes:
  - name: config-vol
    configMap:
      name: CONFIG_NAME
```

### Update ConfigMap

```bash
kubectl edit configmap NAME
kubectl apply -f configmap.yaml
kubectl rollout restart deployment/NAME  # Restart pods
```

### Delete ConfigMap

```bash
kubectl delete configmap NAME
```

---

## ConfigMap Limits

- Maximum size: **1 MB** per ConfigMap
- Etcd has size limits - don't store large files
- Use external storage for large configs

---

## Summary

### Key Points

✅ **Non-sensitive data only** - Use Secrets for passwords
✅ **Decouples config from code** - Easy updates
✅ **Multiple ways to use** - Env vars or files
✅ **Environment variables don't auto-update** - Need pod restart
✅ **Volumes update automatically** - With small delay
✅ **Size limit: 1 MB** - Keep configs small

### When to Use

| Use Case | ConfigMap | Secret |
|----------|-----------|--------|
| Database URL | ✅ | ❌ |
| Database Password | ❌ | ✅ |
| API endpoint | ✅ | ❌ |
| API key | ❌ | ✅ |
| App settings | ✅ | ❌ |
| TLS certificates | ❌ | ✅ |
| Config files | ✅ | ❌ |

---

**ConfigMaps make your apps configurable and portable! 🎛️**