# Project Portfolio

## 1. Federated AI — Blockchain-Secured Federated Learning Platform

**Role:** Lead Developer & Researcher  
**Duration:** 2024 – Present  
**Repository:** [github.com/mubahood/federated-ai](https://github.com/mubahood/federated-ai)  
**Status:** Active Development (~75% complete)

### Overview

A production-grade federated learning system that enables privacy-preserving collaborative training of object detection models across distributed mobile devices. Built as the core artefact for MSc research at Makerere University, applied to Foot-and-Mouth Disease early warning in Ugandan cattle farms.

### Key Achievements

- **Full Django Backend** — REST API with JWT authentication, admin dashboard, model versioning, Swagger docs
- **Flower FL Server** — Federated averaging, differential privacy enforcement, client selection, round orchestration
- **Native Android Client** — Kotlin/Jetpack Compose app with on-device training, real-time inference, offline-first design
- **PyTorch Mobile Integration** — MobileNetV3 architecture, TorchScript model export, <500ms inference latency
- **Celery Workers** — Asynchronous model training, mobile format conversion, background processing
- **Docker Deployment** — Full containerized stack (Django, PostgreSQL, Redis, MinIO, Nginx)
- **95% Test Coverage** — 54+ passing tests, unit/integration/E2E test suites
- **Blockchain Governance** — Verifiable randomness, immutable audit logs, programmable incentives

### Tech Stack

`Python` `Django` `PyTorch` `Flower` `Celery` `Redis` `PostgreSQL` `MinIO` `Docker` `Kotlin` `Jetpack Compose` `Hilt` `Room` `PyTorch Mobile` `Blockchain`

### Architecture

```
Mobile Clients (Android) ←→ Django REST API ←→ Flower FL Server
                                    ↕
                          Celery Workers + Redis
                                    ↕
                     PostgreSQL + MinIO + File Storage
```

---

## 2. ULITS Blockchain FL Early Warning System

**Role:** Research & System Design  
**Duration:** 2025  
**Status:** Research Proposal Phase

### Overview

Research design for integrating Uganda's Livestock Identification and Traceability System (ULITS) with blockchain-governed federated learning for livestock disease surveillance. Combines verifiable fairness protocols, MPC-friendly aggregation, and climate-aware personalization.

### Contributions

- Designed system architecture fusing ULITS data backbone with FL pipeline
- Synthesized literature across 4 key papers into actionable research gaps
- Formulated methodology using Design Science Research framework
- Proposed drift detection and alerting logic for district veterinarians

---

*(Add more projects here — personal projects, work experience, open-source contributions, freelance work, etc.)*
