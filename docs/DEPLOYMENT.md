# Deployment Guide

Comprehensive guide for deploying AI ERP v3.3 to various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

### Required Tools

- Docker & Docker Compose
- Node.js 18+ or Python 3.9+
- Git
- kubectl (for Kubernetes)
- AWS CLI or similar cloud CLI (for cloud deployment)

### System Requirements

- **CPU**: Minimum 4 cores (8+ recommended)
- **RAM**: Minimum 8GB (16GB+ recommended)
- **Disk**: Minimum 50GB SSD
- **Network**: Stable internet connection

### Environment Setup

```bash
# Clone repository
git clone https://github.com/nyeinpyaesone-ui/ERP.git
cd ERP

# Install dependencies
npm install
# or
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

## Development Deployment

### Local Setup

```bash
# Install development dependencies
npm install --save-dev

# Configure environment for development
cat > .env << EOF
NODE_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/erp_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-dev-secret-key
MYANMAR_LOCALE=true
MYANMAR_CURRENCY=MMK
MYANMAR_TIMEZONE=Asia/Yangon
EOF

# Initialize database
npm run db:migrate
npm run db:seed

# Start development server
npm run dev
```

### Running Tests

```bash
# Unit tests
npm run test:unit

# Integration tests
npm run test:integration

# All tests with coverage
npm run test:coverage
```

## Staging Deployment

### Staging Environment Setup

```bash
# Create staging branch
git checkout -b staging

# Configure staging environment
cat > .env.staging << EOF
NODE_ENV=staging
DATABASE_URL=postgresql://user:password@staging-db:5432/erp_staging
REDIS_URL=redis://staging-cache:6379
JWT_SECRET=${STAGING_JWT_SECRET}
API_URL=https://staging-api.yourdomain.com
LOG_LEVEL=info
MYANMAR_LOCALE=true
MYANMAR_CURRENCY=MMK
MYANMAR_TIMEZONE=Asia/Yangon
EOF

# Build for staging
npm run build:staging

# Deploy to staging
npm run deploy:staging
```

### Staging Deployment with Docker

```bash
# Build staging image
docker build -t erp:staging-latest -f Dockerfile.staging .

# Push to registry
docker tag erp:staging-latest registry.example.com/erp:staging-latest
docker push registry.example.com/erp:staging-latest

# Deploy
docker-compose -f docker-compose.staging.yml up -d
```

### Health Checks

```bash
# Check API health
curl https://staging-api.yourdomain.com/health

# Check database connection
npm run db:check

# View logs
docker-compose -f docker-compose.staging.yml logs -f api
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Security scan completed
- [ ] Performance testing done
- [ ] Backup of current production
- [ ] Rollback plan documented
- [ ] Load balancer configured
- [ ] SSL certificates valid
- [ ] Environment variables secured
- [ ] Monitoring configured

### Production Environment Configuration

```bash
# Create production branch
git checkout -b production

# Configure production environment (use secure method)
# Do NOT commit .env files
cat > .env.production << EOF
NODE_ENV=production
DATABASE_URL=${PROD_DATABASE_URL}
REDIS_URL=${PROD_REDIS_URL}
JWT_SECRET=${PROD_JWT_SECRET}
API_URL=https://api.yourdomain.com
LOG_LEVEL=warn
MYANMAR_LOCALE=true
MYANMAR_CURRENCY=MMK
MYANMAR_TIMEZONE=Asia/Yangon
SSL_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=15m
EOF
```

### Production Build & Deployment

```bash
# Build production image
docker build -t erp:v3.3.0 -f Dockerfile.production .

# Push to production registry
docker tag erp:v3.3.0 registry.example.com/erp:v3.3.0
docker push registry.example.com/erp:v3.3.0

# Deploy with health check
docker-compose -f docker-compose.production.yml up -d --health-cmd='curl -f http://localhost:3000/health || exit 1'
```

### Post-Deployment Verification

```bash
# Check API endpoints
curl -H "Authorization: Bearer ${TOKEN}" https://api.yourdomain.com/api/health

# Verify database
npm run db:check

# Verify caching
redis-cli ping

# Run smoke tests
npm run test:smoke:production
```

### Zero-Downtime Deployment

```bash
# Blue-Green Deployment Strategy

# 1. Deploy to green environment
docker-compose -f docker-compose.production-green.yml up -d

# 2. Run health checks on green
curl https://api-green.yourdomain.com/health

# 3. Run tests on green
npm run test:smoke:production

# 4. Switch traffic to green
# Update load balancer configuration

# 5. Keep blue environment ready for rollback
```

## Docker Deployment

### Docker Compose (Single Host)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Backup database
docker-compose exec db pg_dump -U user erp > backup.sql
```

### Docker Stack (Swarm Mode)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.production.yml erp

# View stack status
docker stack ps erp

# Update service
docker service update --image registry.example.com/erp:v3.3.1 erp_api
```

## Kubernetes Deployment

### Prerequisites

```bash
# Ensure kubectl is configured
kubectl config current-context

# Create namespace
kubectl create namespace erp
```

### Deployment Files

```bash
# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n erp
kubectl describe pod -n erp <pod-name>
```

### Scaling

```bash
# Scale API replicas
kubectl scale deployment erp-api --replicas=3 -n erp

# Auto-scaling
kubectl autoscale deployment erp-api --min=2 --max=10 -n erp
```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/erp-api erp-api=registry.example.com/erp:v3.3.1 -n erp

# Monitor rollout
kubectl rollout status deployment/erp-api -n erp

# Rollback if needed
kubectl rollout undo deployment/erp-api -n erp
```

## Monitoring & Maintenance

### Health Checks

```bash
# Application health
GET /health
GET /health/db
GET /health/cache

# Response: { status: 'healthy', timestamp: '2024-06-18T...' }
```

### Logging

```bash
# View application logs
docker-compose logs -f api

# View specific service logs
docker-compose logs -f db

# Tail last 100 lines
docker-compose logs --tail=100 api
```

### Database Maintenance

```bash
# Backup database
npm run db:backup

# Restore database
npm run db:restore <backup-file>

# Run migrations
npm run db:migrate

# Seed data
npm run db:seed
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Database query performance
npm run db:analyze

# Cache hit ratio
redis-cli info stats
```

### Troubleshooting

#### High Memory Usage

```bash
# Check memory leaks
node --inspect api/server.js

# View memory dump
npm run analyze:memory
```

#### Database Connection Issues

```bash
# Check connection pool
npm run db:pool:status

# Reset connection pool
npm run db:pool:reset
```

#### Cache Issues

```bash
# Check Redis connection
redis-cli ping

# Clear cache
redis-cli FLUSHDB

# Monitor cache performance
redis-cli info stats
```

### Backup & Recovery

```bash
# Automated daily backups
0 2 * * * /path/to/backup.sh

# Manual backup
npm run backup

# Verify backup integrity
npm run backup:verify

# Restore from backup
npm run restore <backup-id>
```

## Version Management

### Tagging Releases

```bash
# Create version tag
git tag -a v3.3.0 -m "Release version 3.3.0"

# Push tag
git push origin v3.3.0
```

### Release Notes

Create CHANGELOG.md with:
- New features
- Bug fixes
- Breaking changes
- Migration guide (if needed)

## Rollback Procedure

```bash
# If deployment fails:
docker-compose down
docker-compose up -d # with previous image

# Or with Kubernetes:
kubectl rollout undo deployment/erp-api -n erp

# Verify rollback
curl https://api.yourdomain.com/health
```

## Security Checklist

- [ ] SSL/TLS certificates installed
- [ ] Environment variables secured
- [ ] Database backups encrypted
- [ ] Access logs enabled
- [ ] Rate limiting configured
- [ ] CORS configured properly
- [ ] Security headers set
- [ ] Database credentials rotated
- [ ] API keys rotated
- [ ] Firewall rules configured

For more security details, see [SECURITY.md](./SECURITY.md)
