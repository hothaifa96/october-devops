# Kubernetes Storage Architecture: PV, PVC, StorageClass & Provisioners

## Table of Contents
1. [Storage Architecture Overview](#storage-architecture-overview)
2. [Core Components Deep Dive](#core-components-deep-dive)
3. [Storage Provisioners](#storage-provisioners)
4. [Storage Lifecycle and Binding](#storage-lifecycle-and-binding)
5. [Advanced Concepts](#advanced-concepts)
6. [Best Practices](#best-practices)

---

## Storage Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                      │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │     Pod      │      │     Pod      │      │     Pod      │   │
│  │  Container   │      │  Container   │      │  Container   │   │
│  │     ▲        │      │     ▲        │      │     ▲        │   │
│  └─────┼────────┘      └─────┼────────┘      └─────┼────────┘   │
│        │ Mount                │ Mount                │ Mount    │
│        │                      │                      │          │
│  ┌─────▼────────┐      ┌─────▼────────┐      ┌─────▼────────┐   │
│  │     PVC      │      │     PVC      │      │     PVC      │   │
│  │  (Request)   │      │  (Request)   │      │  (Request)   │   │ 
│  └─────┬────────┘      └─────┬────────┘      └─────┬────────┘   │
│        │ Bind                 │ Bind                 │ Bind     │
│        │                      │                      │          │
│  ┌─────▼────────┐      ┌─────▼────────┐      ┌─────▼────────┐   │
│  │      PV      │      │      PV      │      │      PV      │   │
│  │  (Resource)  │      │  (Resource)  │      │  (Resource)  │   │
│  └─────┬────────┘      └─────┬────────┘      └─────┬────────┘   │
│        │                      │                      │          │
│        └──────────────────────┼──────────────────────┘          │
│                               │                                 │
│                    ┌──────────▼──────────┐                      │
│                    │   StorageClass      │                      │
│                    │   (Provisioner)     │                      │
│                    └──────────┬──────────┘                      │
│                               │                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Storage Backend     │
                    │  (NFS, iSCSI, Cloud)  │
                    └───────────────────────┘
```

### Key Concepts

**Storage abstraction in Kubernetes follows a three-tier model:**

1. **StorageClass (SC)**: Template for dynamic provisioning
2. **PersistentVolume (PV)**: Actual storage resource
3. **PersistentVolumeClaim (PVC)**: Request for storage
4. **Volume**: Mounted storage in a Pod

---

## Core Components Deep Dive

### 1. PersistentVolume (PV)

**Definition**: A piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using Storage Classes.

#### PV Architecture

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-example
  labels:
    type: local
spec:
  # Storage characteristics
  capacity:
    storage: 10Gi
  
  # Access modes determine how the volume can be mounted
  accessModes:
    - ReadWriteOnce    # RWO - single node read-write
    - ReadOnlyMany     # ROX - multiple nodes read-only
    - ReadWriteMany    # RWX - multiple nodes read-write
  
  # Reclaim policy determines what happens when PVC is deleted
  persistentVolumeReclaimPolicy: Retain  # or Delete, Recycle
  
  # Storage class for dynamic provisioning
  storageClassName: fast-ssd
  
  # Volume mode
  volumeMode: Filesystem  # or Block
  
  # Node affinity (optional)
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node01
  
  # Backend storage configuration (varies by type)
  # Example: NFS
  nfs:
    path: /exports/data
    server: nfs-server.example.com
    readOnly: false
```

#### PV States

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│Available │────▶│  Bound   │────▶│ Released │────▶│  Failed  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                                   │
     └───────────────────────────────────┘
              (After Reclaim)
```

- **Available**: Not yet bound to a PVC
- **Bound**: Bound to a PVC
- **Released**: PVC deleted but resource not yet reclaimed
- **Failed**: Failed automatic reclamation

### 2. PersistentVolumeClaim (PVC)

**Definition**: A request for storage by a user. Claims can request specific size and access modes.

#### PVC Architecture

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-example
  namespace: default
spec:
  # Access modes required
  accessModes:
    - ReadWriteOnce
  
  # Volume mode
  volumeMode: Filesystem
  
  # Resources requested
  resources:
    requests:
      storage: 5Gi
    limits:
      storage: 10Gi  # Optional, for expandable volumes
  
  # Storage class for dynamic provisioning
  storageClassName: fast-ssd
  
  # Selector for static provisioning (optional)
  selector:
    matchLabels:
      environment: prod
    matchExpressions:
      - key: storage-tier
        operator: In
        values: ["gold", "platinum"]
  
  # Data source for cloning (optional)
  dataSource:
    name: existing-pvc
    kind: PersistentVolumeClaim
```

#### PVC Lifecycle

```
     Create PVC
          │
          ▼
    ┌──────────┐
    │ Pending  │──────────┐
    └──────────┘          │
          │               │
    Find matching PV      │ Dynamic Provisioning
          │               │
          ▼               ▼
    ┌──────────┐    ┌──────────┐
    │  Bound   │◀───│Provision │
    └──────────┘    │    PV    │
          │         └──────────┘
          │
          ▼
    ┌──────────┐
    │   Lost   │ (If PV deleted while bound)
    └──────────┘
```

### 3. StorageClass

**Definition**: Provides a way to describe different "classes" of storage with different quality-of-service levels, backup policies, or arbitrary policies.

#### StorageClass Architecture

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: premium-storage
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/aws-ebs  # Provisioner type
parameters:
  type: io1          # EBS volume type
  iopsPerGB: "50"    # IOPS per GB
  fsType: ext4       # File system type
  encrypted: "true"  # Encryption
  zones: us-west-2a,us-west-2b  # Availability zones

# Reclaim policy for dynamically provisioned PVs
reclaimPolicy: Delete  # or Retain

# Allow volume expansion
allowVolumeExpansion: true

# Volume binding mode
volumeBindingMode: WaitForFirstConsumer  # or Immediate

# Mount options
mountOptions:
  - debug
  - nouuid

# Allowed topologies for multi-zone clusters
allowedTopologies:
- matchLabelExpressions:
  - key: failure-domain.beta.kubernetes.io/zone
    values:
    - us-west-2a
    - us-west-2b
```

#### StorageClass Parameters by Provisioner

```
┌─────────────────────────────────────────────────────────┐
│                 StorageClass Parameters                  │
├──────────────────┬───────────────────────────────────────┤
│ Provisioner      │ Key Parameters                        │
├──────────────────┼───────────────────────────────────────┤
│ AWS EBS          │ type, iopsPerGB, fsType, encrypted   │
│ GCE PD           │ type, replication-type, zones         │
│ Azure Disk       │ storageaccounttype, kind              │
│ OpenStack Cinder │ availability, volumeType              │
│ vSphere          │ diskformat, datastore, policy         │
│ NFS              │ server, path, readOnly                │
│ Ceph RBD         │ monitors, pool, imageFormat           │
│ Local            │ path, nodeAffinity                    │
└──────────────────┴───────────────────────────────────────┘
```

---

## Storage Provisioners

### Provisioner Types

#### 1. In-Tree Provisioners (Legacy)

Built into Kubernetes core, being deprecated in favor of CSI:

```
kubernetes.io/aws-ebs        # AWS Elastic Block Store
kubernetes.io/gce-pd         # GCE Persistent Disk
kubernetes.io/azure-disk     # Azure Disk
kubernetes.io/azure-file     # Azure File
kubernetes.io/cinder         # OpenStack Cinder
kubernetes.io/vsphere-volume # vSphere
kubernetes.io/no-provisioner # Manual provisioning
```

#### 2. CSI (Container Storage Interface) Provisioners

Modern, plugin-based architecture:

```
┌────────────────────────────────────────────────────────┐
│                    CSI Architecture                     │
│                                                         │
│  ┌──────────┐     ┌──────────────┐    ┌────────────┐ │
│  │   Pod    │────▶│ kubelet      │───▶│ CSI Driver │ │
│  └──────────┘     │              │    │   (Node)   │ │
│                   └──────────────┘    └────────────┘ │
│                                              │         │
│  ┌──────────┐     ┌──────────────┐          │         │
│  │   PVC    │────▶│ CSI          │          │         │
│  └──────────┘     │ Controller   │◀─────────┘         │
│                   └──────────────┘                    │
│                          │                             │
│                   ┌──────▼───────┐                    │
│                   │   Storage    │                    │
│                   │   Backend    │                    │
│                   └──────────────┘                    │
└────────────────────────────────────────────────────────┘
```

##### Popular CSI Drivers

```yaml
# AWS EBS CSI Driver
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-csi-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:us-west-2:111122223333:key/abc-123"

---
# Azure Disk CSI Driver
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: azure-csi-premium
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
  cachingMode: ReadWrite
  networkAccessPolicy: AllowAll

---
# GCE PD CSI Driver
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gce-csi-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
  zones: us-central1-a,us-central1-b

---
# vSphere CSI Driver
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: vsphere-csi
provisioner: csi.vsphere.vmware.com
parameters:
  datastoreurl: "ds:///vmfs/volumes/vsan:123456789"
  storagepolicyname: "vSAN Default Storage Policy"
  fstype: ext4
```

#### 3. External Provisioners

Third-party storage solutions:

```yaml
# NFS CSI Driver
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.example.com
  share: /exported/path
  mountPermissions: "0777"

---
# Rook Ceph
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
  csi.storage.k8s.io/fstype: ext4

---
# Longhorn
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "2880"
  fromBackup: ""
  diskSelector: "ssd"
  nodeSelector: "storage-node"
  recurringJobSelector: '["backup-job", "snapshot-job"]'

---
# OpenEBS
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: openebs-cstor
provisioner: cstor.csi.openebs.io
parameters:
  cas-type: cstor
  cstorPoolCluster: cstor-disk-pool
  replicaCount: "3"
  compression: "lz4"
```

### Dynamic Provisioning Flow

```
┌──────────────────────────────────────────────────────┐
│             Dynamic Provisioning Workflow             │
│                                                       │
│   1. User creates PVC with StorageClass              │
│                      │                                │
│                      ▼                                │
│   2. PVC Controller watches for new PVCs             │
│                      │                                │
│                      ▼                                │
│   3. Controller checks if matching PV exists         │
│                      │                                │
│              No ─────┴───── Yes                      │
│               │                │                      │
│               ▼                ▼                      │
│   4. Call Provisioner    Bind PVC to PV              │
│               │                                       │
│               ▼                                       │
│   5. Provisioner creates storage                     │
│               │                                       │
│               ▼                                       │
│   6. Provisioner creates PV                          │
│               │                                       │
│               ▼                                       │
│   7. Bind PVC to new PV                             │
│               │                                       │
│               ▼                                       │
│   8. Mount to Pod when scheduled                     │
└──────────────────────────────────────────────────────┘
```

---

## Storage Lifecycle and Binding

### Binding Process

```yaml
# Binding Decision Matrix
┌────────────────────────────────────────────────────────┐
│                  PV/PVC Binding Logic                   │
├──────────────────┬─────────────────────────────────────┤
│ PVC Requests     │ PV Must Have                        │
├──────────────────┼─────────────────────────────────────┤
│ Storage Size     │ >= Requested size                   │
│ Access Modes     │ Superset of requested modes         │
│ Storage Class    │ Same storage class name             │
│ Volume Mode      │ Same volume mode                    │
│ Selector Labels  │ Matching labels                     │
│ Node Affinity    │ Compatible node requirements        │
└──────────────────┴─────────────────────────────────────┘
```

### Example: Complete Storage Setup

```yaml
# 1. Create StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-replicated
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: regional-pd
  zones: us-central1-a,us-central1-b
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

---
# 2. Create PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-pvc
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-replicated

---
# 3. Deploy StatefulSet with PVC
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-db
  namespace: production
spec:
  serviceName: postgres
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
        image: postgres:14
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "proddb"
        - name: POSTGRES_USER
          value: "dbadmin"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - /bin/bash
            - -c
            - pg_isready -U dbadmin
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/bash
            - -c
            - pg_isready -U dbadmin
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-replicated
      resources:
        requests:
          storage: 100Gi
```

---

## Advanced Concepts

### 1. Volume Snapshots

```yaml
# VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: pd.csi.storage.gke.io
deletionPolicy: Retain
parameters:
  snapshot-type: "incremental"

---
# Create Snapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: database-pvc

---
# Restore from Snapshot
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-database-pvc
spec:
  storageClassName: fast-replicated
  dataSource:
    name: postgres-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

### 2. Volume Cloning

```yaml
# Clone existing PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-pvc
spec:
  storageClassName: fast-replicated
  dataSource:
    name: database-pvc
    kind: PersistentVolumeClaim
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

### 3. Volume Expansion

```bash
# 1. Ensure StorageClass allows expansion
kubectl patch storageclass fast-replicated -p '{"allowVolumeExpansion": true}'

# 2. Edit PVC to request more storage
kubectl patch pvc database-pvc -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# 3. Monitor expansion
kubectl describe pvc database-pvc
```

### 4. Raw Block Volumes

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: block-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Block  # Raw block device
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi

---
apiVersion: v1
kind: Pod
metadata:
  name: block-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeDevices:  # Not volumeMounts
    - name: data
      devicePath: /dev/xvda  # Block device path
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: block-pvc
```

### 5. Topology-Aware Provisioning

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: topology-aware
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
allowedTopologies:
- matchLabelExpressions:
  - key: topology.ebs.csi.aws.com/zone
    values:
    - us-west-2a
    - us-west-2b
  - key: node.kubernetes.io/instance-type
    values:
    - m5.large
    - m5.xlarge
```

### 6. Storage Capacity Tracking

```yaml
apiVersion: storage.k8s.io/v1
kind: CSIStorageCapacity
metadata:
  name: csi-capacity
storageClassName: fast-replicated
capacity: 1Ti
nodeTopology:
  matchLabels:
    topology.gke.io/zone: us-central1-a
```

---

## Best Practices

### 1. Storage Class Design

```yaml
# Development Environment
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: dev-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-standard
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: Immediate

---
# Production Environment
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: prod-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: regional-pd
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### 2. Resource Quotas for Storage

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-quota
  namespace: production
spec:
  hard:
    requests.storage: 500Gi
    persistentvolumeclaims: "10"
    fast-replicated.storageclass.storage.k8s.io/requests.storage: 200Gi
    fast-replicated.storageclass.storage.k8s.io/persistentvolumeclaims: "5"
```

### 3. Monitoring Storage Usage

```bash
# Get PV usage
kubectl get pv --sort-by=.spec.capacity.storage

# Get PVC usage by namespace
kubectl get pvc --all-namespaces --sort-by=.spec.resources.requests.storage

# Check storage class usage
kubectl get pvc -o custom-columns='NAME:.metadata.name,SIZE:.spec.resources.requests.storage,STORAGECLASS:.spec.storageClassName' --all-namespaces

# Monitor events for storage issues
kubectl get events --field-selector reason=ProvisioningFailed
```

### 4. Backup Strategy

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: volume-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: velero/velero:latest
            command:
            - /bin/sh
            - -c
            - |
              velero backup create backup-$(date +%Y%m%d-%H%M%S) \
                --include-namespaces production \
                --include-resources pvc,pv \
                --snapshot-volumes \
                --wait
          restartPolicy: OnFailure
```

### 5. Security Considerations

```yaml
# Encrypt data at rest
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: encrypted-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:region:account-id:key/key-id"

---
# Pod Security Policy for volumes
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted-volumes
spec:
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
  forbiddenSysctls:
  - '*'
  fsGroup:
    rule: 'MustRunAs'
    ranges:
    - min: 1
      max: 65535
  readOnlyRootFilesystem: true
```

### 6. Performance Tuning

```yaml
# High-performance database storage
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: database-optimized
provisioner: ebs.csi.aws.com
parameters:
  type: io2
  iopsPerGB: "50"
  throughput: "1000"
  fsType: xfs
mountOptions:
  - noatime
  - nodiratime
  - nobarrier
  - logbufs=8
  - logbsize=256k
  - largeio
  - inode64
  - swalloc
```

---

## Troubleshooting Guide

### Common Issues and Solutions

```bash
# PVC stuck in Pending
kubectl describe pvc <pvc-name>
# Check: StorageClass exists, PV available, resource quotas

# PV not binding to PVC
kubectl get pv --show-labels
kubectl get pvc --show-labels
# Check: Access modes, storage size, storage class, selectors

# Volume mount failures
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c <container-name>
# Check: Mount permissions, filesystem type, node availability

# Expansion failures
kubectl get pvc <pvc-name> -o yaml
kubectl describe pvc <pvc-name>
# Check: StorageClass allowVolumeExpansion, filesystem resize support

# CSI driver issues
kubectl get csidrivers
kubectl get csinodes
kubectl logs -n kube-system <csi-driver-pod>
# Check: Driver installation, node plugins, permissions
```

### Debug Commands

```bash
# Check storage capacity
df -h  # On node
kubectl top nodes

# Check PV/PVC binding
kubectl get pv,pvc --all-namespaces -o wide

# Verify CSI drivers
kubectl get csidrivers
kubectl get volumeattachments

# Check storage events
kubectl get events --sort-by='.metadata.creationTimestamp' | grep -i volume

# Inspect volume plugins on node
ls /var/lib/kubelet/plugins/
ls /var/lib/kubelet/plugins_registry/

# Check kubelet logs for volume issues
journalctl -u kubelet | grep -i volume
```

---

## Migration Strategies

### 1. In-Tree to CSI Migration

```yaml
# Enable migration in kubelet config
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
featureGates:
  CSIMigration: true
  CSIMigrationAWS: true
  CSIMigrationGCE: true
  CSIMigrationAzureDisk: true

---
# Update StorageClass to use CSI
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: migrated-storage
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com  # Changed from kubernetes.io/aws-ebs
parameters:
  type: gp3
allowVolumeExpansion: true
```

### 2. Cross-Cluster Storage Migration

```bash
#!/bin/bash
# Storage migration script

# 1. Create snapshot
kubectl apply -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: migration-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: source-pvc
EOF

# 2. Export snapshot to external storage
velero backup create migration-backup \
  --include-resources volumesnapshots,volumesnapshotcontents \
  --snapshot-volumes

# 3. Import in target cluster
velero restore create --from-backup migration-backup

# 4. Create PVC from snapshot in target
kubectl apply -f restored-pvc.yaml
```

---