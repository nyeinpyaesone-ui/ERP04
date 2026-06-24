# Deployment Guide

## Prerequisites

- Kubernetes cluster (v1.28+)
- kubectl configured
- Helm v3+
- Docker registry access
- SSL certificates for production

## Quick Start (Development)

### Local Development with Minikube

```bash
# Start minikube
minikube start --cpus=4 --memory=8192

# Enable ingress
minikube addons enable ingress

# Deploy to local cluster
kubectl apply -k k8s/overlays/dev

# Check deployment
kubectl get pods -n ai-erp-dev

# Access services
minikube service ai-erp-api -n ai-erp-dev
minikube service ai-erp-frontend -n ai-erp-dev
```

### Using Docker Compose (Simplest)

```bash
cd scripts
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Production Deployment

### 1. Prepare Environment

```bash
# Set environment variables
export NAMESPACE=ai-erp-prod
export IMAGE_TAG=v3.3.0
export REGISTRY=ghcr.io/nyeinpyaesone-ui
```

### 2. Configure Secrets

```bash
# Create namespace
kubectl create namespace $NAMESPACE

# Create secrets (use actual values)
kubectl create secret generic db-credentials \
  --from-literal=POSTGRES_USER=erp_user \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=DATABASE_URL=postgresql://erp_user:$(openssl rand -base64 32)@postgres:5432/erp_db \
  -n $NAMESPACE

kubectl create secret generic app-secrets \
  --from-literal=SECRET_KEY=$(openssl rand -base64 32) \
  --from-literal=JWT_SECRET=$(openssl rand -base64 32) \
  -n $NAMESPACE
```

### 3. Deploy with Kustomize

```bash
# Apply base configuration
kubectl apply -k k8s/base

# Apply production overlays
kubectl apply -k k8s/overlays/prod

# Verify deployment
kubectl rollout status deployment/ai-erp-api -n $NAMESPACE
kubectl rollout status deployment/ai-erp-frontend -n $NAMESPACE
```

### 4. Deploy Monitoring Stack

```bash
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Import custom dashboards
kubectl apply -f monitoring/grafana/dashboards/ -n monitoring
```

## CI/CD Pipeline

### GitHub Actions Workflow

The pipeline automatically:
1. Runs tests on PR
2. Builds Docker images on merge to main
3. Deploys to staging
4. Runs integration tests
5. Deploys to production (manual approval)

```yaml
# .github/workflows/deploy.yml
name: Deploy AI-ERP

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd backend && pytest --cov=api
          cd ../frontend && npm test
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push
        run: |
          docker build -t $REGISTRY/ai-erp-api:$IMAGE_TAG ./backend
          docker push $REGISTRY/ai-erp-api:$IMAGE_TAG
  
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          kubectl apply -k k8s/overlays/staging
  
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          kubectl apply -k k8s/overlays/prod
```

## Rollback Procedure

### Automatic Rollback

Canary deployments automatically rollback if:
- Error rate > 1%
- Latency p99 > 500ms
- Health check failures > 3

### Manual Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/ai-erp-api -n $NAMESPACE

# Rollback to specific revision
kubectl rollout undo deployment/ai-erp-api -n $NAMESPACE --to-revision=2

# Check rollback status
kubectl rollout status deployment/ai-erp-api -n $NAMESPACE
```

## Scaling

### Horizontal Pod Autoscaler

```yaml
# Auto-scale based on CPU (70% target)
kubectl autoscale deployment ai-erp-api \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n $NAMESPACE
```

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment ai-erp-api --replicas=5 -n $NAMESPACE
```

## Backup & Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it postgres-0 -n $NAMESPACE -- \
  pg_dump -U erp_user erp_db > backup.sql

# Restore from backup
cat backup.sql | kubectl exec -i postgres-0 -n $NAMESPACE -- \
  psql -U erp_user erp_db
```

### Disaster Recovery

1. Restore database from latest backup
2. Redeploy application
3. Verify data integrity
4. Update DNS if needed

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n $NAMESPACE
kubectl logs <pod-name> -n $NAMESPACE
```

**Service not accessible:**
```bash
kubectl get svc -n $NAMESPACE
kubectl get ingress -n $NAMESPACE
```

**Database connection issues:**
```bash
kubectl exec -it <api-pod> -n $NAMESPACE -- env | grep DATABASE
kubectl exec -it postgres-0 -n $NAMESPACE -- pg_isready
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Liveness check
curl http://localhost:8000/live
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | Application secret key | Required |
| `JWT_SECRET` | JWT signing secret | Required |
| `REDIS_URL` | Redis connection string | redis://localhost:6379 |
| `QDRANT_URL` | Qdrant vector DB URL | http://localhost:6333 |
| `LOG_LEVEL` | Logging level | INFO |
| `ENVIRONMENT` | Environment name | development |

---

**Last Updated**: 2024  
**Version**: 3.3.0
