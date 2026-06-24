# ERP SOLUTION SOLUTION

[![GitHub Actions](https://github.com/nyeinpyaesone-ui/ERP/actions/workflows/ci.yml/badge.svg)](https://github.com/nyeinpyaesone-ui/ERP/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![React Native](https://img.shields.io/badge/react--native-0.74+-blue.svg)](https://reactnative.dev/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)

> Enterprise-grade AI-powered ERP system with 12 modules, 268+ files, and full CI/CD pipeline.

## 🏗️ Platform Overview

| Module | Version | Files | Status | Path |
|--------|---------|-------|--------|------|
| Core System | v2.2 | 91 | ✅ | `backend/` |
| BI Dashboard | v3.2 | 20 | ✅ | `frontend/src/modules/bi-dashboard` |
| Retail POS | v2.9 | 9 | ✅ | `frontend/src/modules/pos` |
| Manufacturing/MRP | v2.7 | 10 | ✅ | `frontend/src/modules/mrp` |
| E-commerce | v3.0 | 12 | ✅ | `frontend/src/modules/ecommerce` |
| Mobile App | v2.5 | 17 | ✅ | `mobile/` |
| Kubernetes | v3.1 | 22 | ✅ | `infra/k8s/` |
| DevOps/CI/CD | — | 10 | ✅ | `.github/` |
| Knowledge System | — | 21 | ✅ | `backend/app/knowledge` |
| Integration | — | 7 | ✅ | `docs/integration` |
| Legacy v2.1 | v2.1 | 31 | ✅ | `backend-v2.1/` |
| Legacy v1.8 | v1.8 | 29 | ✅ | `backend-v1.8/` |

**Total: 268 files, 2 commits, production-ready**

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### One-Command Setup
```bash
git clone https://github.com/nyeinpyaesone-ui/ERP.git
cd ERP
./scripts/setup.sh        # Install dependencies
docker-compose up -d      # Start services
```

### Development
```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev

# Terminal 3 — Mobile
cd mobile && npx expo start
```

## 📦 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  React   │ │  Mobile  │ │  Admin   │ │ Customer │  │
│  │  Web App │ │  App     │ │  Portal  │ │  Portal  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│                      API Gateway                         │
│              FastAPI + OpenAPI + WebSocket               │
├─────────────────────────────────────────────────────────┤
│                    AI Intelligence Layer                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  RAG     │ │  Agent   │ │  LLM     │ │ Forecast │  │
│  │  Engine  │ │  Orchestr│ │  Service │ │  Engine  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│                   Core ERP Modules                       │
│  CRM │ HR │ Inventory │ Finance │ Manufacturing │ POS  │
├─────────────────────────────────────────────────────────┤
│                   Data & Infrastructure                  │
│  PostgreSQL │ Redis │ Elasticsearch │ S3/MinIO │ K8s   │
└─────────────────────────────────────────────────────────┘
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development workflow, commit conventions |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [docs/PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md) | Full production deployment guide |
| [docs/API_SUMMARY.md](docs/API_SUMMARY.md) | API endpoints and authentication |
| [docs/GITHUB_SECRETS.md](docs/GITHUB_SECRETS.md) | CI/CD secrets setup |
| [docs/integration](docs/integration) | System integration guide |

## 🛠️ Management Commands

```bash
# Repository management
./scripts/gh-manager.sh status     # Show status
./scripts/gh-manager.sh verify     # Full verification
./scripts/gh-manager.sh tag v1.1.0 # Create release

# Development
make dev        # Start dev environment
make test       # Run tests
make push       # Quick push to GitHub
make clean      # Clean build artifacts
```

## 🛡️ Security

- JWT-based authentication
- Role-based access control (RBAC)
- Row-level security (RLS) for multi-tenancy
- API rate limiting
- Input validation and sanitization
- CORS protection
- Secrets management via GitHub Actions

## 🌍 Internationalization

- English (en) — Primary
- Myanmar (my) — Burmese with Pyidaungsu font
- Extensible for additional languages

## 📊 Monitoring

- Prometheus metrics at `/metrics`
- Health checks at `/health`, `/health/db`, `/health/redis`
- Structured logging with correlation IDs
- Sentry error tracking integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with convention: `feat:`, `fix:`, `docs:`, etc.
4. Push and open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

[MIT License](LICENSE) — ERP SOLUTION Contributors

## 🆘 Support

- GitHub Issues: [github.com/nyeinpyaesone-ui/ERP/issues](https://github.com/nyeinpyaesone-ui/ERP/issues)
- API Docs: `http://localhost:8000/docs` (when running)
- Status: `./scripts/gh-manager.sh status`

---

Built with ❤️ by the ERP SOLUTION Team
