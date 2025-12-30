# Kubernetes Secrets Tutorial

## What is a Secret?

A **Secret** stores sensitive data like passwords, API keys, and certificates. It's similar to ConfigMap but designed for confidential information.

```
┌─────────────────────────────────────────────┐
│              Secret                         │
│  ┌───────────────────────────────────────┐  │
│  │  username: YWRtaW4=  (base64)         │  │
│  │  password: cGFzc3dvcmQ=  (base64)     │  │
│  │  api-key: bXlzZWNyZXRrZXk=  (base64)  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
   Environment Variables    Volume Files
   in Pod (decoded)         in Pod (decoded)
```

### Secret vs ConfigMap

| Feature | ConfigMap | Secret |
|---------|-----------|--------|
| Purpose | Configuration | Sensitive data |
| Encoding | Plain text | Base64 encoded |
| Size limit | 1 MB | 1 MB |
| Security | Basic | Better (encrypted at rest) |
| Use for | Settings, configs | Passwords, keys, certs |

⚠️ **Important**: Secrets are **base64 encoded**, NOT encrypted by default in etcd (unless encryption at rest is enabled)

---

## Secret Types

| Type | Use Case | Keys |
|------|----------|------|
| `Opaque` | Generic secrets (default) | Any |
| `kubernetes.io/basic-auth` | Basic authentication | `username`, `password` |
| `kubernetes.io/ssh-auth` | SSH keys | `ssh-privatekey` |
| `kubernetes.io/tls` | TLS certificates | `tls.crt`, `tls.key` |
| `kubernetes.io/dockerconfigjson` | Docker registry auth | `.dockerconfigjson` |
| `kubernetes.io/service-account-token` | Service account tokens | `token`, `ca.crt` |

---

## Creating Secrets

### Method 1: From Literal Values

```bash
# Create secret with key-value pairs
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=SuperSecret123

# View it (values are base64 encoded)
kubectl get secret db-secret -o yaml
```

### Method 2: From Files

```bash
# Create files with sensitive data
echo -n "admin" > username.txt
echo -n "SuperSecret123" > password.txt

# Create secret from files
kubectl create secret generic db-secret \
  --from-file=username=username.txt \
  --from-file=password=password.txt

# Or use actual filenames as keys
kubectl create secret generic db-secret \
  --from-file=username.txt \
  --from-file=password.txt
```

### Method 3: From YAML (Manual Base64)

```bash
# Encode values to base64
echo -n "admin" | base64
# Output: YWRtaW4=

echo -n "SuperSecret123" | base64
# Output: U3VwZXJTZWNyZXQxMjM=
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: default
type: Opaque
data:
  # Base64 encoded values
  username: YWRtaW4=
  password: U3VwZXJTZWNyZXQxMjM=
```

### Method 4: From YAML (Plain Text)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:  # Use stringData for plain text (auto-encoded)
  username: admin
  password: SuperSecret123
```

```bash
# Apply
kubectl apply -f secret.yaml

# Kubernetes automatically converts stringData to base64 in data field
```

---

## Using Secrets in Pods

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
        # Single secret value
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
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
        - secretRef:
            name: db-secret
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
        - prefix: "DB_"  # Creates DB_username, DB_password
          secretRef:
            name: db-secret
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
      image: myapp:v1
      volumeMounts:
        # Mount secret as files
        - name: secret-volume
          mountPath: /etc/secrets
          readOnly: true  # Always read-only for secrets
  
  volumes:
    - name: secret-volume
      secret:
        secretName: db-secret
        defaultMode: 0400  # Read-only for owner
```

### Method 5: Mount Specific Keys as Files

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:v1
      volumeMounts:
        - name: secret-volume
          mountPath: /etc/secrets
          readOnly: true
  
  volumes:
    - name: secret-volume
      secret:
        secretName: db-secret
        items:
          # Only mount specific keys
          - key: username
            path: db-user.txt
            mode: 0400
          - key: password
            path: db-pass.txt
            mode: 0400
```

---

## Secret Types Examples

### 1. Opaque Secret (Generic)

```bash
# Most common type
kubectl create secret generic api-secret \
  --from-literal=api-key=mySecretAPIKey123 \
  --from-literal=api-token=xyz789token
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secret
type: Opaque
stringData:
  api-key: mySecretAPIKey123
  api-token: xyz789token
```

### 2. Basic Auth Secret

```bash
# Create basic auth secret
kubectl create secret generic basic-auth \
  --from-literal=username=admin \
  --from-literal=password=secretpass123 \
  --type=kubernetes.io/basic-auth
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: basic-auth
type: kubernetes.io/basic-auth
stringData:
  username: admin
  password: secretpass123
```

### 3. SSH Auth Secret

```bash
# Create SSH key secret
kubectl create secret generic ssh-key \
  --from-file=ssh-privatekey=~/.ssh/id_rsa \
  --type=kubernetes.io/ssh-auth
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ssh-key
type: kubernetes.io/ssh-auth
stringData:
  ssh-privatekey: |
    -----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEA...
    -----END RSA PRIVATE KEY-----
```

### 4. TLS Secret

```bash
# Create TLS secret from certificate files
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: LS0tLS1CRUdJTi...  # Base64 encoded cert
  tls.key: LS0tLS1CRUdJTi...  # Base64 encoded key
```

### 5. Docker Registry Secret

```bash
# Create Docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=user@example.com
```

```yaml
# Use in pod
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  containers:
    - name: app
      image: myregistry.com/private-image:v1
  imagePullSecrets:
    - name: regcred
```

---

## Complete Examples

### Example 1: Database Connection

```yaml
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_USER: dbadmin
  POSTGRES_PASSWORD: SuperSecret123
  POSTGRES_DB: myapp
---
# Deployment using secret
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          envFrom:
            - secretRef:
                name: postgres-secret
          ports:
            - containerPort: 5432
```

### Example 2: API Keys in Application

```yaml
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  stripe-api-key: sk_test_123456789
  sendgrid-api-key: SG.xyz789
  jwt-secret: myJWTSecretKey123
---
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
        - name: api
          image: backend:v1
          env:
            - name: STRIPE_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: stripe-api-key
            - name: SENDGRID_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: sendgrid-api-key
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: jwt-secret
```

### Example 3: TLS Certificate for Ingress

```yaml
# TLS Secret
apiVersion: v1
kind: Secret
metadata:
  name: tls-cert
  namespace: default
type: kubernetes.io/tls
stringData:
  tls.crt: |
    -----BEGIN CERTIFICATE-----
    MIIDXTCCAkWgAwIBAgIJAKZ...
    -----END CERTIFICATE-----
  tls.key: |
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w...
    -----END PRIVATE KEY-----
---
# Ingress using TLS secret
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  tls:
    - hosts:
        - example.com
      secretName: tls-cert
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
```

### Example 4: Mounted Secret Files

```yaml
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: config-secret
type: Opaque
stringData:
  database.conf: |
    host=db.example.com
    port=5432
    user=dbuser
    password=SecretPass123
  
  api-key.json: |
    {
      "apiKey": "xyz123",
      "apiSecret": "abc789"
    }
---
# Pod mounting secret as files
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:v1
      volumeMounts:
        - name: config
          mountPath: /etc/config
          readOnly: true
      command: ["sh", "-c"]
      args:
        - |
          cat /etc/config/database.conf
          cat /etc/config/api-key.json
          sleep 3600
  volumes:
    - name: config
      secret:
        secretName: config-secret
```

---

## Secret Operations

### View Secrets

```bash
# List all secrets
kubectl get secrets
kubectl get secret  # Singular also works

# View specific secret (encoded)
kubectl get secret db-secret -o yaml

# Decode secret values
kubectl get secret db-secret -o jsonpath='{.data.username}' | base64 -d
kubectl get secret db-secret -o jsonpath='{.data.password}' | base64 -d

# Describe secret (doesn't show values)
kubectl describe secret db-secret
```

### Edit Secrets

```bash
# Edit directly
kubectl edit secret db-secret

# Replace from new values
kubectl create secret generic db-secret \
  --from-literal=username=newuser \
  --from-literal=password=newpass \
  --dry-run=client -o yaml | kubectl apply -f -

# Patch specific key
kubectl patch secret db-secret -p '{"stringData":{"password":"newPassword123"}}'
```

### Delete Secrets

```bash
# Delete specific secret
kubectl delete secret db-secret

# Delete multiple
kubectl delete secret secret1 secret2

# Delete all secrets (careful!)
kubectl delete secrets --all
```

---

## Security Best Practices

### 1. Never Commit Secrets to Git

```bash
# ❌ BAD - Secret in Git
git add secret.yaml
git commit -m "Add secrets"

# ✅ GOOD - Use .gitignore
echo "secret.yaml" >> .gitignore
echo "*.secret.yaml" >> .gitignore
```

### 2. Use External Secret Management

```yaml
# Use tools like:
# - External Secrets Operator
# - Sealed Secrets
# - Vault
# - AWS Secrets Manager
# - Azure Key Vault
# - GCP Secret Manager
```

### 3. Enable Encryption at Rest

```bash
# Enable etcd encryption (cluster admin task)
# Secrets are only base64 encoded by default!
```

### 4. Use RBAC to Restrict Access

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["db-secret"]  # Specific secret only
    verbs: ["get", "list"]
```

### 5. Use Separate Namespaces

```bash
# Production secrets in production namespace
kubectl create secret generic prod-secret --from-literal=key=value -n production

# Development secrets in dev namespace
kubectl create secret generic dev-secret --from-literal=key=value -n development
```

### 6. Set Immutable Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: immutable-secret
type: Opaque
immutable: true  # Cannot be changed
stringData:
  api-key: myAPIKey123
```

### 7. Use Read-Only Mounts

```yaml
volumeMounts:
  - name: secret-volume
    mountPath: /etc/secrets
    readOnly: true  # Always true for secrets
```

### 8. Rotate Secrets Regularly

```bash
# Update secret
kubectl create secret generic db-secret \
  --from-literal=password=NewPassword456 \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment/myapp
```

---

## Troubleshooting

### Issue 1: Secret Not Found

```bash
# Error: secret "db-secret" not found

# Check if secret exists
kubectl get secrets

# Check namespace
kubectl get secrets -n <namespace>

# Create secret
kubectl create secret generic db-secret --from-literal=key=value
```

### Issue 2: Decoding Secret Values

```bash
# Get base64 encoded value
kubectl get secret db-secret -o jsonpath='{.data.password}'
# Output: U3VwZXJTZWNyZXQxMjM=

# Decode
kubectl get secret db-secret -o jsonpath='{.data.password}' | base64 -d
# Output: SuperSecret123

# Or use describe (doesn't show values)
kubectl describe secret db-secret
```

### Issue 3: Pod Not Getting Secret Updates

```bash
# Environment variables DON'T update automatically
# Mounted files update automatically (with delay)

# Solution: Restart pods
kubectl rollout restart deployment/myapp

# Or delete pods
kubectl delete pods -l app=myapp
```

### Issue 4: Permission Denied

```bash
# Error: secrets "db-secret" is forbidden

# Check RBAC permissions
kubectl auth can-i get secrets

# Check service account
kubectl get sa

# Grant permissions (if authorized)
kubectl create rolebinding secret-reader \
  --role=secret-reader \
  --serviceaccount=default:default
```

---

## Testing Secrets

```bash
# Create test secret
kubectl create secret generic test-secret \
  --from-literal=username=testuser \
  --from-literal=password=testpass

# Create test pod
kubectl run test --image=busybox:1.35 -it --rm --restart=Never \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "test",
      "image": "busybox:1.35",
      "command": ["sh"],
      "env": [
        {"name": "USERNAME", "valueFrom": {"secretKeyRef": {"name": "test-secret", "key": "username"}}},
        {"name": "PASSWORD", "valueFrom": {"secretKeyRef": {"name": "test-secret", "key": "password"}}}
      ]
    }]
  }
}' -- sh

# Inside pod
echo $USERNAME
echo $PASSWORD
```

---

## Quick Reference

### Create Secret

```bash
# From literals
kubectl create secret generic NAME \
  --from-literal=key1=value1 \
  --from-literal=key2=value2

# From files
kubectl create secret generic NAME \
  --from-file=key1=/path/to/file1 \
  --from-file=key2=/path/to/file2

# TLS secret
kubectl create secret tls NAME \
  --cert=/path/to/cert \
  --key=/path/to/key

# Docker registry
kubectl create secret docker-registry NAME \
  --docker-server=SERVER \
  --docker-username=USER \
  --docker-password=PASS

# From YAML
kubectl apply -f secret.yaml
```

### Use in Pod

```yaml
# Environment variable
env:
  - name: VAR_NAME
    valueFrom:
      secretKeyRef:
        name: SECRET_NAME
        key: key_name

# Volume mount
volumes:
  - name: secret-vol
    secret:
      secretName: SECRET_NAME
volumeMounts:
  - name: secret-vol
    mountPath: /etc/secrets
    readOnly: true
```

### View Secret

```bash
kubectl get secrets
kubectl get secret NAME -o yaml
kubectl describe secret NAME

# Decode value
kubectl get secret NAME -o jsonpath='{.data.KEY}' | base64 -d
```

### Delete Secret

```bash
kubectl delete secret NAME
```

---

## Common Patterns

### Pattern 1: Database Credentials

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-creds
type: Opaque
stringData:
  host: mysql.example.com
  port: "3306"
  database: myapp
  username: dbuser
  password: SecretPass123
```

### Pattern 2: Multiple Environment Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: prod-secrets
  namespace: production
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@db:5432/prod
  REDIS_URL: redis://redis:6379/0
  API_KEY: prod-api-key-xyz
  JWT_SECRET: prod-jwt-secret-123
---
apiVersion: v1
kind: Secret
metadata:
  name: dev-secrets
  namespace: development
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@db:5432/dev
  REDIS_URL: redis://redis:6379/1
  API_KEY: dev-api-key-abc
  JWT_SECRET: dev-jwt-secret-456
```

### Pattern 3: Configuration Files with Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-config
type: Opaque
stringData:
  config.json: |
    {
      "database": {
        "host": "db.example.com",
        "user": "dbuser",
        "password": "SecretPass123"
      },
      "api": {
        "key": "xyz789",
        "secret": "abc456"
      }
    }
```

---

## Summary

### Key Points

✅ **Secrets store sensitive data** - Passwords, keys, certificates
✅ **Base64 encoded, not encrypted** - Enable encryption at rest!
✅ **Similar to ConfigMap** - But for confidential information
✅ **Multiple types** - Opaque, TLS, Docker, SSH, basic-auth
✅ **Environment variables or files** - Two ways to use
✅ **Never commit to Git** - Use secret management tools
✅ **RBAC controls access** - Restrict who can read secrets
✅ **Rotate regularly** - Update secrets periodically

### Secret vs ConfigMap Decision

| Data Type | Use |
|-----------|-----|
| Database password | Secret ✅ |
| Database host | ConfigMap ✅ |
| API key | Secret ✅ |
| API endpoint | ConfigMap ✅ |
| TLS certificate | Secret ✅ |
| Nginx config | ConfigMap ✅ |
| JWT secret | Secret ✅ |
| Application name | ConfigMap ✅ |

