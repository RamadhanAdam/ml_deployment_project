# ML Deployment Project

A production-style MLOps project running a FastAPI prediction API on Kubernetes, with PostgreSQL for prediction logging, encrypted secrets, scheduled health checks, and a full monitoring stack.

Built locally using k3d, deployed to a 3-node cluster with Ingress, StatefulSet-backed Postgres, SOPS-encrypted secrets, and Prometheus/Grafana/Loki for observability.

---

## Stack

| Layer | Tech |
|-------|------|
| Cluster | k3d (Kubernetes in Docker), kubectl |
| API | Python, FastAPI, joblib |
| Database | PostgreSQL 15 (StatefulSet) |
| Secret management | SOPS + Age encryption |
| Monitoring | Prometheus, Grafana, Loki, Promtail |
| Package management | Helm |
| Container registry | Docker Hub |

---

## Architecture

```
External traffic (localhost:8081)
        ↓
  k3d LoadBalancer
        ↓
  Ingress — predictor namespace
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
  src/
    api.py
    model_loader.py
  models/
    model.pkl
  manifests/
    deployment.yaml
    service.yaml
    ingress.yaml
    configmap.yaml
    postgres.yaml
    postgres-secret.enc.yaml   ← encrypted, safe to commit
    cronjob.yaml
  .sops.yaml
  .gitignore
  .dockerignore
  Dockerfile
  requirements.txt
```

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
kubectl apply -f manifests/ingress.yaml
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

## Roadmap

- [ ] Prediction logging to PostgreSQL from the API
- [ ] AWS EKS deployment
- [ ] SageMaker model training pipeline
- [ ] Triton Inference Server for model serving
- [ ] Kubeflow pipelines
- [ ] Redis feature store / prediction cache in front of Triton