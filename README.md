# ML Deployment Project

A production style MLOps project running a FastAPI prediction API on Kubernetes, with PostgreSQL for prediction logging, encrypted secrets, scheduled health checks, and a full monitoring stack.

Built locally using k3d, initially deployed with Ingress, then migrated to Gateway API. Also deployed to GKE via GitHub Actions CI/CD, with StatefulSet-backed Postgres, SOPS-encrypted secrets, and Prometheus/Grafana/Loki for observability.
---

## Stack

| Layer | Tech |
|-------|------|
| Cluster | k3d (local), GKE (cloud), kubectl |
| API | Python, FastAPI, joblib |
| Database | PostgreSQL 15 (StatefulSet) |
| Secret management | SOPS + Age encryption |
| Monitoring | Prometheus, Grafana, Loki, Promtail |
| Package management | Helm, Kustomize |
| CI/CD | GitHub Actions |
| Container registry | Docker Hub |

---

## Architecture

```
External traffic (localhost:8081)
        ↓
  k3d LoadBalancer
        ↓
  Gateway API — predictor namespace 
        ↓
  predictor-api-svc (ClusterIP)
        ↓
  predictor-api Pod (FastAPI)
        ↓
  postgres-svc (headless)
        ↓
  postgres-ss-0 (PostgreSQL)
        └── dedicated PVC via local-path dynamic provisioning

CronJob → /health every 5 min → logs → Promtail → Loki → Grafana
```

---

## Project Structure

```
ml_deployment_project/
├── src/
│   ├── api.py
│   ├── model_loader.py
│   ├── train_model.py
│   └── preprocessing.py
│
├── models/
│   └── model.pkl
│
├── manifests/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── gateway.yaml
│   ├── httproute.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   ├── postgres.yaml
│   ├── postgres-secret.enc.yaml   ← encrypted, safe to commit
│   └── cronjob.yaml
│
├── persistentvolumes/
│   ├── persistentvolume.yaml
│   └── persistentvolumeclaim.yaml
│
├── kustomization.yaml
├── Dockerfile
├── requirements.txt
├── .sops.yaml
└── README.md
```
*Local artifacts (mlruns, service account keys, plaintext secrets) are excluded via .gitignore.*
---

## Secret Management

Credentials are encrypted with [SOPS](https://github.com/getsops/sops) + [Age](https://github.com/FiloSottile/age) before being committed. The plaintext secret file and the Age private key never touch git.

```bash
# Encrypt
sops --encrypt manifests/postgres-secret.yaml > manifests/postgres-secret.enc.yaml

# Deploy (decrypts on the fly, never writes plaintext to disk)
export SOPS_AGE_KEY_FILE=$(pwd)/keys.txt
sops --decrypt manifests/postgres-secret.enc.yaml | kubectl apply -f -
```

`keys.txt` must be kept locally and backed up somewhere safe. Without it, secrets cannot be decrypted.

---

## Running Locally

### Requirements

```bash
brew install k3d kubectl helm sops age
```

Docker Desktop must be running.

### Cluster

```bash
k3d cluster create predictor-api --port 8081:80@loadbalancer --agents 2
kubectl config use-context k3d-predictor-api
kubectl create namespace predictor
```

### Deploy

```bash
export SOPS_AGE_KEY_FILE=$(pwd)/keys.txt
sops --decrypt manifests/postgres-secret.enc.yaml | kubectl apply -f -
kubectl apply -f manifests/configmap.yaml
kubectl apply -f manifests/postgres.yaml
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml
kubectl apply -f manifests/gateway.yaml
kubectl apply -f manifests/httproute.yaml
kubectl apply -f manifests/hpa.yaml
kubectl apply -f manifests/cronjob.yaml
```

### Verify

```bash
kubectl get pods -n predictor
curl http://localhost:8081/health
```

---

## Monitoring

```bash
# Prometheus + Grafana
kubectl create namespace prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-community/kube-prometheus-stack --generate-name --namespace prometheus

# Loki + Promtail
kubectl create namespace loki-stack
helm repo add grafana https://grafana.github.io/helm-charts
helm upgrade --install loki --namespace=loki-stack grafana/loki-stack --set loki.image.tag=2.9.3
```

### Grafana

```bash
# Get generated deployment name
kubectl get deployments -n prometheus

# Forward to browser
kubectl --namespace prometheus port-forward deployment/<grafana-deployment-name> 3000

# Get admin password
kubectl get secret --namespace prometheus -l app.kubernetes.io/component=admin-secret \
  -o jsonpath="{.items[0].data.admin-password}" | base64 --decode ; echo
```

Open `http://localhost:3000`, log in as `admin`.

To connect Loki: Connections → Data sources → Add Loki → URL: `http://loki.loki-stack:3100`

---
## Cloud Deployment (GKE)

This project is also deployed to Google Kubernetes Engine (GKE) using GitHub Actions CI/CD.

High-level steps:

1. Create a GKE cluster
2. Configure Workload Identity / service account
3. Store secrets securely
4. GitHub Actions builds and pushes the Docker image
5. GitHub Actions deploys manifests to GKE via kubectl
6. Gateway API exposes service via cloud LoadBalancer

---

| Aspect        | DBaaS (Cloud SQL) | Self-Hosted (StatefulSet) |
|---------------|-------------------|----------------------------|
| **Setup Time** | Minutes — click through console or one `gcloud` command | Hours — write StatefulSet, headless service, PVC, configure init |
| **Maintenance** | Google handles patches, minor version upgrades, failover | You handle everything — upgrades, monitoring, crash recovery |
| **Backups** | Built-in automated backups, point-in-time recovery, one-click restore | You write CronJobs, manage backup storage, test restore procedures |
| **Cost** | Higher — Cloud SQL `db-f1-micro` starts ~$9/month, scales up fast | Lower — just the compute you're already paying for |
| **Reliability** | SLA-backed, automatic failover to replica | As reliable as you make it — single StatefulSet pod is a single point of failure |
| **Scaling** | Vertical scaling with a few clicks, read replicas easily added | Manual — modify StatefulSet, handle primary/replica logic yourself |
| **Portability** | Locked to GCP — migrating requires data export/import | Runs anywhere Kubernetes runs — EKS, AKS, on-prem, local |
| **Good For** | Production systems where uptime and maintenance burden matter | Learning, portability, cost-sensitive projects, full control |

## Roadmap

- [ ] Postgres high availability setup
- [ ] Terraform infrastructure provisioning
- [ ] GitOps with ArgoCD or Flux
- [ ] Triton Inference Server for model serving
- [ ] Redis feature store / prediction cache