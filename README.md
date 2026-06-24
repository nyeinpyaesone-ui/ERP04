# AI-ERP v3.3 – Myanmar-First Enterprise Resource Planning

[![Version](https://img.shields.io/badge/version-3.3.0-blue.svg)](https://github.com/nyeinpyaesone-ui/AI_aGENts_muLTIverse/releases)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326CE5?logo=kubernetes)](https://kubernetes.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql)](https://www.postgresql.org)
[![AI](https://img.shields.io/badge/AI-Llama_3-FF6F00?logo=meta)](https://ollama.com)

**AI‑ERP v3.3** is a production‑ready ERP platform built for Myanmar businesses, combining full‑featured ERP modules, AI‑powered agents, and comprehensive localisation including 330+ townships, tax rates, and corrected business terminology.

---

## 🚀 Key Features

### Core Modules
- **Core ERP** (v2.5) – CRM, HR, Inventory, Finance, Projects
- **Manufacturing / MRP** (v2.7) – BOM, Work Orders, Production Planning
- **HR & Payroll** (v2.8) – Employee management, payroll, attendance
- **Retail POS** (v2.9) – Point‑of‑Sale with barcode, multi‑payment
- **E‑commerce Storefront** (v3.0) – Full B2C store with cart, checkout, orders
- **BI Dashboard** (v3.2) – Real‑time KPIs, charts, AI insights

### AI & Intelligence
- **Foundation Guard** – Enforces correct Myanmar terminology across all outputs
- **AI Agent Skills** – Deterministic delivery fee, tax calculation, terminology checks – **zero LLM token cost**
- **Local AI Agent** – Llama 3 + Qdrant for offline AI
- **RAG Pipeline** – Semantic search across ERP code, schemas, and documents

### Myanmar Domain Data (v3.3)
- **330+ Townships** with delivery zones, fees, semantic embeddings
- **6 Tax Rates** – CIT (22%), CT (5%), AIT (2%), WHT (10%), PIT (20%), SSB (2%)
- **13 Border Trade Stations** with compliance notes
- **4 Trucking Corridors** with seasonal rate variations
- **17 Corrected Business Terms** with forbidden versions
- **Full Data Lineage** – Every table linked to project version

### Infrastructure
- **Kubernetes Native** – Canary, HPA, Prometheus, Grafana
- **Local LLM** – Ollama + Qdrant for offline AI
- **Automation** – n8n workflow engine
- **Monitoring** – Prometheus + Grafana + Sentry

---

## 📦 Quick Start

```bash
# Clone and setup
git clone git@github.com:nyeinpyaesone-ui/AI_aGENts_muLTIverse.git
cd AI_aGENts_muLTIverse

# Run complete setup
./scripts/setup.sh

# Access system
# API: http://localhost:8000/docs
# Dashboard: http://localhost:3000
# Qdrant: http://localhost:6333/dashboard
# n8n: http://localhost:5678
```

---

## 🏗️ Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system architecture.

```
┌──────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                        │
│  Web Dashboard (React)  │  Mobile App (React Native)  │  Admin   │
└──────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────┐
│                         API Gateway & Security                    │
│  Auth (JWT/OAuth)  │  Rate Limiter  │  Load Balancer  │  WS      │
└───────────────────────────────┬───────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────┐
│                         Orchestration Layer                       │
│  Executive Orchestrator  │  Task Planner  │  Skill Registry      │
└───────────────────────────────┬───────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────┐
│                         Agent Pool                               │
│  CRM Agent  │  Finance Agent  │  HR Agent  │  Inventory Agent   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────┐
│                         Data Layer                                │
│  PostgreSQL  │  Qdrant (Vector)  │  Redis (Cache)  │  MinIO     │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Kubernetes (minikube or kind for local dev)
- Ollama (for local LLM)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=api --cov-report=html

# Frontend tests
cd frontend
npm test
```

---

## 📁 Project Structure

```
AI_aGENts_muLTIverse/
├── README.md                 # This file
├── docs/
│   ├── ARCHITECTURE.md       # System architecture
│   ├── DEPLOYMENT.md         # Deployment guide
│   ├── API.md                # API documentation
│   └── SECURITY.md           # Security policies
├── backend/
│   ├── api/                  # API endpoints
│   ├── models/               # Database models
│   ├── services/             # Business logic
│   ├── tests/                # Unit & integration tests
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/                  # React source code
│   ├── public/               # Static assets
│   └── package.json          # Node dependencies
├── k8s/
│   ├── base/                 # Base Kubernetes configs
│   └── overlays/             # Environment-specific configs
├── monitoring/
│   ├── prometheus.yaml       # Prometheus config
│   └── grafana/              # Grafana dashboards
├── scripts/
│   ├── setup.sh              # Setup script
│   └── seed_data.py          # Database seeding
├── data/
│   ├── townships.json        # Myanmar township data
│   ├── tax_rates.json        # Tax configuration
│   └── business_terms.json   # Terminology corrections
└── .github/
    └── workflows/            # CI/CD pipelines
```

---

## 🔒 Security

See [SECURITY.md](docs/SECURITY.md) for:
- Authentication & Authorization
- Data Encryption
- Secrets Management
- Compliance (GDPR, Myanmar Data Law)
- Threat Model

**Important**: Never commit `.env` files or secrets to version control.

---

## 📊 Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards & alerting
- **Sentry**: Error tracking
- **Health Checks**: `/health`, `/ready`, `/live`

Access Grafana: http://localhost:3001 (admin/admin)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure all tests pass and coverage >80%
5. Commit with meaningful messages (`feat: add amazing feature`)
6. Push to your branch
7. Open a Pull Request

**PR Requirements**:
- Working code (no documentation-only PRs)
- Accompanying tests
- Updated documentation
- Security review for sensitive changes
- <400 lines per PR for easy review

---

## 📄 License

Proprietary - All rights reserved.

---

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/nyeinpyaesone-ui/AI_aGENts_muLTIverse/issues
- Email: support@example.com

---

**Version**: 3.3.0  
**Last Updated**: 2024
