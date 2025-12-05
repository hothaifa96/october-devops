# Kubernetes CKA Lab Exercises


### Exercise A: Multi-Container Pod with Shared Volume

**Requirements**:
- Create a namespace called `webapp-space`
- Deploy a pod named `web-logger` with two containers:
  - Container 1: `nginx` (image: `nginx:alpine`)
    - Should serve content from `/usr/share/nginx/html`
    - Expose port 80
  - Container 2: `logger` (image: `busybox`)
    - Should run command: 
    ```yaml
    volumeMounts:
        - name: *******
          mountPath: *****
        - name: *******
          mountPath: *****
    command:
        - sh
        - -c
        - |
          echo "<html><body><h1>Server Log</h1><pre>" > /usr/share/nginx/html/status.html;
          while true; do
            echo "$(date) CPU: $(top -bn1 | grep 'CPU' | awk '{print $2$3$4$5$6$7$8$9}')" >> /usr/share/nginx/html/status.html;
            echo "Requests: $(wc -l /var/log/nginx/access.log 2>/dev/null | awk '{print $1}')" >> /usr/share/nginx/html/status.html;
            echo "<br>" >> /usr/share/nginx/html/status.html;
            sleep 10;
          done
    ```
    - Mount a shared volume to `/logs` and `/usr/share/nginx/html`
- Both containers should share an `emptyDir` volume
- The nginx container should mount this volume at `/usr/share/nginx/html`
- Add appropriate resource limits: CPU: 100m, Memory: 128Mi for both containers
- Label the pod with `app=web-logger` and `tier=frontend`

**Verification**:
- Pod should be running with both containers healthy
- You should be able access the status.html and see it changes every 10 seconds

---

### Exercise B: Multi-Pod Shared Storage

**Requirements**:
- Create a StorageClass named `shared-storage` suitable for RWX access
- Create a PVC named `shared-data` with:
  - Size: 3Gi
  - AccessMode: ReadWriteMany (use ReadWriteOnce if RWX not available, and document the limitation)
  - StorageClass: `shared-storage`
- Deploy 3 pods (`writer-1`, `writer-2`, `reader-1`) that:
  - All mount the same PVC at `/shared-data`
  - Writers: Use `busybox`, write timestamps to files
  - Reader: Use `busybox`, continuously read and display files
- Implement a mechanism to prevent write conflicts
- Add node affinity rules to spread pods across nodes (if multi-node cluster)

---

### ETGAR ::: : PV Backup and Restore Strategy

**Requirements**:
- Create a namespace `backup-demo`
- Deploy a stateful application (e.g., PostgreSQL or WordPress) with:
  - PVC of 3Gi
  - Some sample data
- Create a CronJob named `backup-scheduler` that:
  - Runs every 6 hours
  - Creates point-in-time snapshots/backups
  - Stores backups in a separate PVC
  - Maintains only last 5 backups (rotation)
  - Logs backup status
- Create a restore Job that can:
  - List available backups
  - Restore from a specific backup
  - Verify data integrity after restore
- Test disaster recovery by:
  - Deleting the original PVC
  - Restoring from backup
  - Verifying application functionality

**Verification**:
- Automated backups run on schedule
- Restore process successfully recovers data
- Application functions normally after restore

---
