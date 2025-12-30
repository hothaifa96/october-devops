# Kubernetes Ingress and Ingress Controller - Complete Tutorial

## Table of Contents
1. [Introduction](#introduction)
2. [What is Ingress?](#what-is-ingress)
3. [What is an Ingress Controller?](#what-is-an-ingress-controller)
4. [Why Do We Need Ingress?](#why-do-we-need-ingress)
5. [Popular Ingress Controllers](#popular-ingress-controllers)
6. [Installation Guide](#installation-guide)
7. [Basic Ingress Configuration](#basic-ingress-configuration)
8. [Advanced Configurations](#advanced-configurations)
9. [TLS/SSL Configuration](#tlsssl-configuration)
10. [Path-Based Routing](#path-based-routing)
11. [Host-Based Routing](#host-based-routing)
12. [Annotations](#annotations)
13. [Troubleshooting](#troubleshooting)
14. [Best Practices](#best-practices)
15. [Complete Example Project](#complete-example-project)

---

## Introduction

Kubernetes Ingress is a critical component for managing external access to services in a Kubernetes cluster. This tutorial provides a comprehensive guide to understanding, installing, and configuring Ingress and Ingress Controllers.

### Prerequisites
- Kubernetes cluster (v1.19+)
- kubectl CLI tool installed
- Basic understanding of Kubernetes concepts (Pods, Services, Deployments)
- Helm (optional but recommended)

---

## What is Ingress?

**Ingress** is a Kubernetes API object that manages external access to services within a cluster, typically HTTP and HTTPS traffic. It provides:

- **HTTP/HTTPS routing** to services based on URL paths or hostnames
- **Load balancing** across multiple backend services
- **SSL/TLS termination** for secure connections
- **Name-based virtual hosting** on a single IP address

### Key Components of Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: example-service
                port:
                  number: 80
```

---

## What is an Ingress Controller?

An **Ingress Controller** is the actual implementation that fulfills the Ingress rules. While Ingress defines the routing rules, the Ingress Controller is the component that:

- Watches for Ingress resources in the cluster
- Configures the actual load balancer/proxy
- Routes traffic according to Ingress rules
- Handles SSL/TLS certificates

### How It Works

```
Internet → Ingress Controller → Ingress Rules → Service → Pods
```

The Ingress Controller acts as a reverse proxy and load balancer, interpreting the Ingress rules and routing traffic accordingly.

---

## Why Do We Need Ingress?

### Without Ingress
- Each service needs its own LoadBalancer (expensive in cloud environments)
- Multiple public IPs required
- No centralized routing logic
- Complex SSL/TLS management

### With Ingress
- Single entry point to the cluster
- One LoadBalancer/IP for multiple services
- Centralized routing and SSL management
- Cost-effective and easier to manage

---

## Popular Ingress Controllers

### 1. NGINX Ingress Controller
- Most popular and widely used
- Feature-rich with extensive configuration options
- Good performance and stability

### 2. Traefik
- Modern, cloud-native ingress controller
- Automatic SSL with Let's Encrypt
- Built-in dashboard

### 3. HAProxy Ingress
- High-performance option
- Enterprise features available
- Good for high-traffic scenarios

### 4. AWS ALB Ingress Controller
- Native AWS Application Load Balancer integration
- Best for AWS-specific deployments

### 5. Kong Ingress Controller
- API Gateway features
- Plugin ecosystem
- Good for microservices

---

## Installation Guide

### Method 1: Installing NGINX Ingress Controller with kubectl

```bash
# Apply the NGINX Ingress Controller manifest
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Verify installation
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx

# Wait for the controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### Method 2: Installing with Helm (Recommended)

```bash
# Add the ingress-nginx repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install the chart
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Check the installation
helm list -n ingress-nginx
kubectl get all -n ingress-nginx
```

### Method 3: Installing on Minikube

```bash
# Enable the NGINX Ingress controller addon
minikube addons enable ingress

# Verify that the addon is enabled
minikube addons list | grep ingress

# Check pods
kubectl get pods -n ingress-nginx
```

### Method 4: Installing on Kind (Kubernetes in Docker)

```bash
# Create a kind cluster with ingress ports mapped
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for it to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

---

## Basic Ingress Configuration

### Step 1: Deploy Sample Applications

```yaml
# app1-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
    spec:
      containers:
      - name: app1
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app1-service
spec:
  selector:
    app: app1
  ports:
    - port: 80
      targetPort: 80
---
# app2-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app2
  template:
    metadata:
      labels:
        app: app2
    spec:
      containers:
      - name: app2
        image: httpd
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app2-service
spec:
  selector:
    app: app2
  ports:
    - port: 80
      targetPort: 80
```

Apply the deployments:
```bash
kubectl apply -f app1-deployment.yaml
kubectl apply -f app2-deployment.yaml
```

### Step 2: Create Basic Ingress Resource

```yaml
# basic-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: basic-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /app1
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
      - path: /app2
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
```

Apply the ingress:
```bash
kubectl apply -f basic-ingress.yaml

# Check ingress status
kubectl get ingress
kubectl describe ingress basic-ingress
```

### Step 3: Test the Configuration

```bash
# Get the Ingress Controller's external IP
kubectl get svc -n ingress-nginx

# Test the routes (replace <EXTERNAL-IP> with actual IP)
curl http://<EXTERNAL-IP>/app1
curl http://<EXTERNAL-IP>/app2

# For minikube
minikube ip  # Get the IP
curl http://$(minikube ip)/app1
curl http://$(minikube ip)/app2
```

---

## Advanced Configurations

### Load Balancing Algorithms

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: load-balance-ingress
  annotations:
    nginx.ingress.kubernetes.io/load-balance: "least_conn"
    # Options: round_robin (default), least_conn, ip_hash
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

### Rate Limiting

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rate-limit-ingress
  annotations:
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-rpm: "100"
    nginx.ingress.kubernetes.io/limit-connections: "5"
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

### Request/Response Headers

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: header-ingress
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Custom-Header: MyValue";
      more_set_headers "X-Frame-Options: SAMEORIGIN";
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, OPTIONS"
spec:
  ingressClassName: nginx
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

---

## TLS/SSL Configuration

### Step 1: Create TLS Certificate

```bash
# Generate a self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key \
  -out tls.crt \
  -subj "/CN=example.com/O=example"

# Create Kubernetes secret
kubectl create secret tls example-tls \
  --cert=tls.crt \
  --key=tls.key
```

### Step 2: Configure Ingress with TLS

```yaml
# tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    - www.example.com
    secretName: example-tls
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
  - host: www.example.com
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

### Using cert-manager for Automatic SSL

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

```yaml
# Ingress with automatic SSL
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: auto-tls-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    secretName: example-com-tls
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

---

## Path-Based Routing

### Different Path Types

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-routing-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      # Exact match
      - path: /exact
        pathType: Exact
        backend:
          service:
            name: exact-service
            port:
              number: 80
      # Prefix match (default)
      - path: /prefix
        pathType: Prefix
        backend:
          service:
            name: prefix-service
            port:
              number: 80
      # Implementation specific (depends on IngressClass)
      - path: /impl
        pathType: ImplementationSpecific
        backend:
          service:
            name: impl-service
            port:
              number: 80
```

### Complex Path Routing Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: complex-path-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: api-v1
            port:
              number: 8080
      - path: /v2(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: api-v2
            port:
              number: 8080
      - path: /docs
        pathType: Prefix
        backend:
          service:
            name: docs-service
            port:
              number: 80
```

---

## Host-Based Routing

### Multiple Domains Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-routing-ingress
spec:
  ingressClassName: nginx
  rules:
  # Main website
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: main-website
            port:
              number: 80
  # Blog subdomain
  - host: blog.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: blog-service
            port:
              number: 80
  # API subdomain
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  # Admin panel
  - host: admin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
```

### Wildcard Host Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wildcard-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: "*.example.com"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wildcard-service
            port:
              number: 80
```

---

## Annotations

### Common NGINX Ingress Annotations

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: annotated-ingress
  annotations:
    # Rewrite and redirect
    nginx.ingress.kubernetes.io/rewrite-target: /$1
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    
    # Timeouts
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    
    # Body size
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    
    # Rate limiting
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-connections: "10"
    
    # Authentication
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"
    
    # Whitelist IPs
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,192.168.0.0/16"
    
    # Backend protocol
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    
    # Session affinity
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/affinity-mode: "persistent"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "86400"
spec:
  ingressClassName: nginx
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

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Ingress Controller Not Running

```bash
# Check if controller pods are running
kubectl get pods -n ingress-nginx

# Check logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Describe the pod for events
kubectl describe pod -n ingress-nginx <pod-name>
```

#### 2. Ingress Not Getting External IP

```bash
# Check service status
kubectl get svc -n ingress-nginx

# For cloud providers, ensure LoadBalancer is provisioned
kubectl describe svc -n ingress-nginx ingress-nginx-controller

# For local testing, use NodePort or port-forward
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
```

#### 3. 404 Not Found Errors

```bash
# Check if ingress resource exists
kubectl get ingress

# Verify ingress configuration
kubectl describe ingress <ingress-name>

# Check if backend service is running
kubectl get svc
kubectl get endpoints <service-name>

# Check ingress controller logs for errors
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=100
```

#### 4. SSL/TLS Issues

```bash
# Verify secret exists
kubectl get secrets
kubectl describe secret <tls-secret-name>

# Check certificate details
kubectl get secret <tls-secret-name> -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout

# Check cert-manager logs if using
kubectl logs -n cert-manager deploy/cert-manager
```

#### 5. Path Routing Not Working

```bash
# Test with curl and verbose output
curl -v http://<ingress-ip>/path

# Check annotations
kubectl get ingress <ingress-name> -o yaml | grep annotations -A 10

# Verify pathType is correct
kubectl get ingress <ingress-name> -o jsonpath='{.spec.rules[*].http.paths[*].pathType}'
```

### Debugging Commands

```bash
# Get all resources in ingress namespace
kubectl get all -n ingress-nginx

# Check ingress class
kubectl get ingressclass

# View nginx configuration
kubectl exec -n ingress-nginx <controller-pod> -- cat /etc/nginx/nginx.conf

# Test internal connectivity
kubectl run test-pod --image=busybox -it --rm -- sh
# Inside pod:
wget -O- http://<service-name>.<namespace>.svc.cluster.local

# Check events
kubectl get events -n ingress-nginx --sort-by='.lastTimestamp'

# Enable debug logging
kubectl edit deployment -n ingress-nginx ingress-nginx-controller
# Add to args: --v=5
```

---

## Best Practices

### 1. Resource Organization

```yaml
# Use namespaces for organization
apiVersion: v1
kind: Namespace
metadata:
  name: production
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: production-ingress
  namespace: production
  labels:
    environment: production
    team: platform
```

### 2. Security Best Practices

- Always use TLS/SSL for production
- Implement rate limiting
- Use network policies
- Enable ModSecurity/WAF
- Restrict source IPs when possible
- Use strong authentication

```yaml
# Example with security headers
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options: DENY";
      more_set_headers "X-Content-Type-Options: nosniff";
      more_set_headers "X-XSS-Protection: 1; mode=block";
      more_set_headers "Referrer-Policy: strict-origin-when-cross-origin";
```

### 3. Performance Optimization

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: optimized-ingress
  annotations:
    # Enable gzip compression
    nginx.ingress.kubernetes.io/enable-compression: "true"
    
    # Cache static content
    nginx.ingress.kubernetes.io/configuration-snippet: |
      location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
      }
    
    # Connection keep-alive
    nginx.ingress.kubernetes.io/upstream-keepalive-connections: "100"
    nginx.ingress.kubernetes.io/upstream-keepalive-timeout: "60"
```

### 4. Monitoring and Observability

```bash
# Install Prometheus and Grafana for monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Enable metrics in ingress controller
helm upgrade nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.metrics.enabled=true \
  --set controller.metrics.serviceMonitor.enabled=true
```

### 5. High Availability

```yaml
# Deploy multiple replicas of ingress controller
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-ingress-controller
  namespace: ingress-nginx
spec:
  replicas: 3
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                - ingress-nginx
            topologyKey: kubernetes.io/hostname
```

---

## Complete Example Project

### Project: Multi-Service E-Commerce Platform

#### Directory Structure
```
ecommerce-platform/
├── namespace.yaml
├── services/
│   ├── frontend.yaml
│   ├── api.yaml
│   ├── admin.yaml
│   └── payment.yaml
├── configmaps/
│   └── nginx-config.yaml
├── secrets/
│   └── tls-secret.yaml
└── ingress/
    └── main-ingress.yaml
```

#### 1. Namespace Configuration

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce
```

#### 2. Frontend Service

```yaml
# services/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ecommerce
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
      - name: frontend
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: config
          mountPath: /usr/share/nginx/html
      volumes:
      - name: config
        configMap:
          name: frontend-config
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: ecommerce
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
  namespace: ecommerce
data:
  index.html: |
    <!DOCTYPE html>
    <html>
    <head><title>E-Commerce Store</title></head>
    <body><h1>Welcome to our E-Commerce Platform</h1></body>
    </html>
```

#### 3. API Service

```yaml
# services/api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ecommerce
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: kennethreitz/httpbin
        ports:
        - containerPort: 80
        env:
        - name: DB_CONNECTION
          value: "postgres://db:5432"
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: ecommerce
spec:
  selector:
    app: api
  ports:
    - port: 8080
      targetPort: 80
```

#### 4. Admin Service

```yaml
# services/admin.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin
  namespace: ecommerce
spec:
  replicas: 2
  selector:
    matchLabels:
      app: admin
  template:
    metadata:
      labels:
        app: admin
    spec:
      containers:
      - name: admin
        image: nginx:alpine
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: admin-service
  namespace: ecommerce
spec:
  selector:
    app: admin
  ports:
    - port: 3000
      targetPort: 80
```

#### 5. Main Ingress Configuration

```yaml
# ingress/main-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options: SAMEORIGIN";
      more_set_headers "X-Content-Type-Options: nosniff";
      more_set_headers "X-XSS-Protection: 1; mode=block";
spec:
  ingressClassName: nginx
  rules:
  # Main website
  - host: shop.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  # API endpoint
  - host: api.shop.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
  # Admin panel with IP restriction
  - host: admin.shop.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
  # Path-based routing for different services
  - host: shop.example.com
    http:
      paths:
      - path: /api(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /admin(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
---
# Separate ingress for IP-restricted admin
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: admin-restricted-ingress
  namespace: ecommerce
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,192.168.1.0/24"
spec:
  ingressClassName: nginx
  rules:
  - host: secure-admin.shop.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 3000
```

#### 6. Deployment Script

```bash
#!/bin/bash
# deploy.sh

echo "Deploying E-Commerce Platform..."

# Create namespace
kubectl apply -f namespace.yaml

# Deploy services
kubectl apply -f services/

# Create secrets (if TLS enabled)
# kubectl apply -f secrets/

# Deploy ingress
kubectl apply -f ingress/

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s \
  deployment/frontend deployment/api deployment/admin \
  -n ecommerce

# Show status
echo "Deployment Status:"
kubectl get all -n ecommerce
echo ""
echo "Ingress Status:"
kubectl get ingress -n ecommerce
echo ""
echo "External IP:"
kubectl get svc -n ingress-nginx

echo "Deployment complete!"
```

#### 7. Testing the Deployment

```bash
# Test frontend
curl -H "Host: shop.example.com" http://<INGRESS-IP>/

# Test API
curl -H "Host: api.shop.example.com" http://<INGRESS-IP>/

# Test path-based routing
curl -H "Host: shop.example.com" http://<INGRESS-IP>/api/get
curl -H "Host: shop.example.com" http://<INGRESS-IP>/admin/

# Test with local /etc/hosts file
echo "<INGRESS-IP> shop.example.com api.shop.example.com admin.shop.example.com" >> /etc/hosts

# Then access directly
curl http://shop.example.com
curl http://api.shop.example.com
```

---

## Quick Reference Commands

```bash
# Ingress Controller Management
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
kubectl describe svc -n ingress-nginx ingress-nginx-controller

# Ingress Resources
kubectl get ingress --all-namespaces
kubectl describe ingress <name>
kubectl edit ingress <name>
kubectl delete ingress <name>

# Testing and Debugging
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
kubectl exec -it -n ingress-nginx <controller-pod> -- /bin/bash
curl -v -H "Host: example.com" http://localhost:8080

# Get External IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# View nginx.conf
kubectl exec -n ingress-nginx <controller-pod> -- cat /etc/nginx/nginx.conf

# Reload configuration
kubectl rollout restart deployment -n ingress-nginx ingress-nginx-controller
```

---

## Additional Resources

- [Official Kubernetes Ingress Documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [NGINX Ingress Controller Documentation](https://kubernetes.github.io/ingress-nginx/)
- [Ingress Controllers Comparison](https://docs.google.com/spreadsheets/d/1DnsHtdHbxjvHmxvlu7VhzWcWgLAn_Mc5L1WlhLDA__k/edit)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

---
