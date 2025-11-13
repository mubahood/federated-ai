# MASTER'S PROJECT PROPOSAL

**Title:** Privacy-Preserving Federated Learning for Distributed Object Detection on Mobile Devices

**Student:** [Your Name]  
**Student Number:** [Your Registration Number]  
**Programme:** Master of Science in Computer Science  
**School:** School of Computing and Informatics Technology  
**College:** College of Computing and Information Sciences  
**Institution:** Makerere University  
**Supervisor:** [Supervisor's Name]  
**Date:** November 2025

---

## 1. BACKGROUND AND MOTIVATION

### 1.1 Context

The proliferation of mobile devices and Internet of Things (IoT) sensors has created unprecedented opportunities for collaborative machine learning. However, traditional centralized machine learning approaches face significant challenges:

1. **Privacy Concerns:** Users are increasingly reluctant to share personal data with centralized servers due to privacy risks and regulatory requirements (GDPR, HIPAA).

2. **Data Sovereignty:** Organizations and individuals in developing regions, including Uganda, face challenges with data leaving their jurisdiction for processing.

3. **Communication Costs:** Transmitting large volumes of raw data (images, videos) from mobile devices to central servers is bandwidth-intensive and costly, particularly in regions with limited connectivity.

4. **Latency Requirements:** Real-time applications require low-latency inference, which is difficult when data must travel to remote servers.

### 1.2 Problem Statement

Current machine learning systems for object detection require users to upload their images to centralized servers for model training. This approach presents three critical problems:

**Problem 1: Privacy Violation**  
Users must surrender control of their personal images, exposing sensitive information (faces, locations, activities) to potential breaches or misuse.

**Problem 2: Resource Inefficiency**  
Uploading millions of images from mobile devices consumes significant bandwidth and server storage, creating barriers to participation, especially in low-connectivity environments like Uganda.

**Problem 3: Model Staleness**  
Centralized models cannot quickly adapt to local conditions, cultural contexts, or emerging object categories without expensive retraining cycles.

### 1.3 Proposed Solution

This research proposes a **Federated Learning (FL)** system that enables privacy-preserving collaborative training of object detection models across distributed mobile devices. The key innovation is:

> **"Your data stays on your device, but your knowledge improves everyone's AI"**

The system allows users to:
- Train machine learning models locally on their mobile devices
- Share only model updates (gradients/parameters), not raw images
- Contribute to a global model that benefits from collective learning
- Maintain full control over their private data

### 1.4 Significance

This research addresses critical challenges relevant to Uganda and East Africa:

**1. Data Privacy Protection**  
Enables AI development while respecting user privacy rights, crucial for sectors like healthcare, banking, and education.

**2. Efficient Bandwidth Utilization**  
Reduces communication costs by transmitting only small model updates (~10MB) instead of raw images (~1GB).

**3. Localized AI Models**  
Enables models that understand local contexts (Ugandan traffic patterns, local fruits, regional architecture) without exporting data abroad.

**4. Democratic AI Development**  
Empowers individuals and small organizations to participate in AI development without expensive cloud infrastructure.

---

## 2. LITERATURE REVIEW

### 2.1 Federated Learning

Federated Learning was introduced by McMahan et al. (2017) in their seminal paper "Communication-Efficient Learning of Deep Networks from Decentralized Data." The core algorithm, **Federated Averaging (FedAvg)**, enables distributed training:

**Algorithm Overview:**
1. Server initializes global model M₀
2. Server selects subset of clients (e.g., 10 out of 1000)
3. Clients download current global model
4. Each client trains locally for E epochs on local data
5. Clients upload model updates (Δw) to server
6. Server aggregates updates: M_{t+1} = M_t + Σ(n_k/n * Δw_k)
7. Repeat until convergence

**Key Advantages:**
- Reduces communication by 10-100× compared to centralized training
- Handles non-IID (non-independent, identically distributed) data
- Preserves privacy through gradient aggregation

### 2.2 Privacy-Preserving Techniques

**Differential Privacy (Dwork, 2006)**  
Adds calibrated noise to model updates to prevent reconstruction of individual data points:

ε-differential privacy: P[M(D) ∈ S] ≤ e^ε × P[M(D') ∈ S]

Where D and D' differ by one sample. Lower ε = stronger privacy.

**Secure Aggregation (Bonawitz et al., 2017)**  
Cryptographic protocol ensuring the server sees only aggregated results, not individual updates, using homomorphic encryption.

### 2.3 Mobile Object Detection

**MobileNet Architecture (Howard et al., 2017)**  
Efficient CNN architecture designed for mobile devices using depthwise separable convolutions:
- MobileNetV3: 5.4M parameters, 75.2% ImageNet accuracy
- Inference: <50ms on modern mobile CPUs
- Model size: 5.4MB (compressed)

**On-Device Training (Jeong et al., 2018)**  
Recent work demonstrates feasibility of training neural networks on mobile devices:
- Transfer learning: Fine-tune last layers only
- Quantization-aware training: Reduce precision to INT8
- Federated optimization: Local SGD with periodic averaging

### 2.4 Related Work

**1. FedML (He et al., 2020)**  
Open-source federated learning library with mobile support, but focuses on research simulations rather than production deployment.

**2. TensorFlow Federated (Google, 2019)**  
Framework for federated learning research, limited mobile device integration, primarily for research.

**3. PySyft (OpenMined, 2018)**  
Privacy-preserving ML library, but lacks optimized mobile clients and real-world deployment infrastructure.

**4. Flower Framework (Beutel et al., 2020)**  
Modern federated learning framework with strong mobile support, active development, and production-ready features. Our system builds on Flower.

### 2.5 Research Gap

While federated learning frameworks exist, there is limited research on:

1. **Production-ready FL systems** with complete mobile app + server infrastructure
2. **Object detection in FL** (most work focuses on classification)
3. **African context deployments** with low-bandwidth, intermittent connectivity
4. **User-centered design** for non-technical users participating in federated learning

This research fills these gaps by developing a complete, production-grade system tailored for East African deployment contexts.

---

## 3. RESEARCH OBJECTIVES

### 3.1 Main Objective

To design, implement, and evaluate a privacy-preserving federated learning system for distributed object detection on mobile devices that enables collaborative model training without sharing raw data.

### 3.2 Specific Objectives

1. **System Design & Architecture**
   - Design a scalable federated learning architecture for object detection
   - Develop communication protocols optimized for low-bandwidth networks
   - Implement secure model aggregation with differential privacy guarantees

2. **Mobile Client Development**
   - Develop a native Android application with on-device training capabilities
   - Implement efficient model compression and quantization techniques
   - Design intuitive user interfaces for data labeling and model training

3. **Server Infrastructure**
   - Build a robust Django-based backend for orchestrating FL rounds
   - Implement the Flower FL framework for model aggregation
   - Develop RESTful APIs for client registration and model distribution

4. **Privacy Preservation**
   - Implement differential privacy mechanisms with configurable privacy budgets
   - Develop secure aggregation protocols to prevent gradient leakage
   - Analyze privacy-utility tradeoffs under various configurations

5. **Performance Evaluation**
   - Evaluate model accuracy with non-IID data distributions
   - Measure communication efficiency (bandwidth usage, round convergence)
   - Assess system scalability (100+ concurrent clients)
   - Compare with centralized baseline approaches

6. **Real-World Deployment**
   - Deploy system with real users in Uganda
   - Collect user feedback on usability and privacy perceptions
   - Analyze practical challenges in low-connectivity environments

---

## 4. METHODOLOGY

### 4.1 Research Design

This research follows a **Design Science Research (DSR)** methodology, which involves:

1. **Problem Identification:** Privacy concerns in centralized ML
2. **Solution Design:** Federated learning system architecture
3. **Implementation:** Prototype development
4. **Evaluation:** Performance and usability testing
5. **Iteration:** Refinement based on findings

### 4.2 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CENTRAL SERVER                         │
│  ┌────────────────────────────────────────────────┐    │
│  │  Django Backend (REST API)                     │    │
│  │  - Client registration & authentication        │    │
│  │  - Model versioning & distribution             │    │
│  │  - Training coordination                       │    │
│  └────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Flower Federated Learning Server              │    │
│  │  - Round orchestration (FedAvg strategy)       │    │
│  │  - Client selection & aggregation              │    │
│  │  - Model update validation                     │    │
│  └────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Storage Layer                                  │    │
│  │  PostgreSQL | Redis | MinIO                    │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         ↕ HTTPS + gRPC
┌─────────────────────────────────────────────────────────┐
│                  MOBILE CLIENTS                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Device 1 │  │ Device 2 │  │ Device N │             │
│  │ Android  │  │ Android  │  │ Android  │             │
│  │          │  │          │  │          │             │
│  │ Local    │  │ Local    │  │ Local    │             │
│  │ Training │  │ Training │  │ Training │             │
│  │ PyTorch  │  │ PyTorch  │  │ PyTorch  │             │
│  │ Mobile   │  │ Mobile   │  │ Mobile   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Technology Stack

**Server-Side:**
- **Backend Framework:** Django 4.2 (Python 3.11+)
- **FL Framework:** Flower 1.8+ for federated orchestration
- **ML Framework:** PyTorch 2.0+ for model training
- **Database:** PostgreSQL 15 for relational data
- **Cache:** Redis 7 for session management
- **Object Storage:** MinIO for model artifacts
- **Task Queue:** Celery for asynchronous jobs
- **API:** Django REST Framework with JWT authentication

**Mobile Client:**
- **Platform:** Android (API 26+, targeting API 34)
- **Language:** Kotlin 1.9.20
- **UI:** Jetpack Compose (Material Design 3)
- **ML Framework:** PyTorch Mobile (.ptl models)
- **FL Client:** Flower Android SDK
- **Local Storage:** Room Database + DataStore
- **Networking:** Retrofit + OkHttp
- **DI:** Hilt (Dagger)

**Model Architecture:**
- **Base Model:** MobileNetV3-Small (5.4M parameters)
- **Detection Head:** Custom lightweight head for object detection
- **Optimization:** INT8 quantization, layer pruning
- **Format:** TorchScript (.ptl) for mobile deployment

### 4.4 Data Collection

**Primary Data:**
1. **Object Images:** 5,000+ images across 5 categories (Person, Car, Bicycle, Cat, Dog)
2. **Training Metrics:** Accuracy, loss, training time per round
3. **System Metrics:** Bandwidth usage, latency, battery consumption
4. **User Feedback:** Surveys and interviews with 20-30 test users

**Secondary Data:**
1. **Public Datasets:** COCO, Open Images for pre-training
2. **Research Literature:** Papers on FL, privacy, mobile ML

### 4.5 Implementation Phases

**Phase 1: Foundation (Weeks 1-4)**
- System architecture design
- Server infrastructure setup (Django + PostgreSQL + Redis)
- Basic REST APIs for object management

**Phase 2: Machine Learning (Weeks 5-8)**
- Model training pipeline implementation
- PyTorch Mobile integration
- Model conversion and optimization

**Phase 3: Federated Learning (Weeks 9-12)**
- Flower server setup
- FL strategy implementation (FedAvg)
- Client-server communication protocols
- Differential privacy integration

**Phase 4: Mobile Development (Weeks 13-16)**
- Android app development (UI/UX)
- On-device training implementation
- Flower client integration
- Camera and image labeling features

**Phase 5: Testing & Evaluation (Weeks 17-20)**
- Unit and integration testing
- Performance benchmarking
- Security audits
- User acceptance testing

**Phase 6: Deployment & Analysis (Weeks 21-24)**
- Production deployment
- Real-world testing with users
- Data analysis and visualization
- Documentation and thesis writing

### 4.6 Evaluation Metrics

**Model Performance:**
- **Accuracy:** Classification accuracy on test set (target: ≥85%)
- **F1-Score:** Harmonic mean of precision and recall
- **mAP (mean Average Precision):** Object detection metric
- **Convergence Rate:** Rounds to reach target accuracy

**System Performance:**
- **Communication Efficiency:** Bytes transferred per round
- **Training Time:** Time per local training round on mobile
- **Inference Latency:** Detection time per image (<500ms target)
- **Battery Impact:** Power consumption during training
- **Scalability:** Performance with 10, 50, 100 concurrent clients

**Privacy Analysis:**
- **Privacy Budget:** Epsilon (ε) value for differential privacy
- **Reconstruction Attack Success Rate:** Ability to infer training data
- **Information Leakage:** Gradient inversion attack resilience

**User Experience:**
- **System Usability Scale (SUS):** Standardized usability score
- **Task Completion Rate:** Success in labeling and training
- **User Satisfaction:** Likert scale surveys (1-5)
- **Privacy Perception:** Trust and privacy concern ratings

### 4.7 Experimental Setup

**Baseline Comparisons:**
1. **Centralized Training:** All data collected on server
2. **Local-Only Training:** No collaboration, each device isolated
3. **Federated Learning:** Proposed system

**Test Scenarios:**
1. **IID Data Distribution:** Data evenly distributed across clients
2. **Non-IID Distribution:** Each client has skewed label distribution
3. **Varying Client Numbers:** 10, 25, 50, 100 clients
4. **Network Conditions:** High-bandwidth, low-bandwidth (throttled)
5. **Privacy Levels:** ε = {∞, 10, 5, 1} (no privacy to strong privacy)

---

## 5. EXPECTED OUTCOMES AND CONTRIBUTIONS

### 5.1 Technical Deliverables

1. **Fully Functional System**
   - Production-ready FL server infrastructure
   - Native Android mobile application
   - Complete REST API documentation
   - Docker-based deployment setup

2. **Open-Source Software**
   - Published on GitHub with MIT license
   - Comprehensive documentation and tutorials
   - Example datasets and training scripts

3. **Performance Reports**
   - Detailed benchmarking results
   - Privacy-utility tradeoff analysis
   - Scalability test reports

### 5.2 Academic Contributions

1. **Novel System Architecture**
   - First complete FL system for object detection with production-ready mobile clients in East African context

2. **Empirical Evidence**
   - Real-world deployment data from Ugandan users
   - Privacy perception studies in developing contexts
   - Performance analysis under low-bandwidth conditions

3. **Publications**
   - Conference paper (target: ACM MobiCom, AAAI)
   - Workshop paper (FL-NeurIPS, FL-IJCAI)
   - Journal article (IEEE Access, MDPI Sensors)

### 5.3 Practical Impact

1. **Healthcare Applications**
   - Disease detection (malaria, skin conditions) without sharing patient images
   - Privacy-compliant AI for medical diagnosis

2. **Agricultural Monitoring**
   - Crop disease detection using farmer's smartphone images
   - Livestock health monitoring

3. **Smart City Infrastructure**
   - Traffic monitoring without privacy violations
   - Security systems with privacy preservation

4. **Educational Value**
   - Teaching resource for FL concepts
   - Reference implementation for students and researchers

---

## 6. RESEARCH TIMELINE

| Phase | Activities | Duration | Milestone |
|-------|-----------|----------|-----------|
| **1. Foundation** | Literature review, system design, server setup | Weeks 1-4 | Architecture document |
| **2. ML Pipeline** | Model training, PyTorch Mobile integration | Weeks 5-8 | Working object detector |
| **3. Federated Learning** | Flower integration, FL protocols | Weeks 9-12 | FL server operational |
| **4. Mobile App** | Android development, UI/UX | Weeks 13-16 | Alpha release |
| **5. Testing** | Unit tests, integration tests, benchmarks | Weeks 17-20 | Test reports |
| **6. Deployment** | Real-world testing, data collection | Weeks 21-24 | Deployed system |
| **7. Analysis** | Data analysis, visualizations | Weeks 25-26 | Results chapter |
| **8. Writing** | Thesis writing, revisions | Weeks 27-32 | Complete thesis |
| **9. Defense** | Presentation preparation, defense | Weeks 33-36 | Graduation |

**Total Duration:** 9 months (36 weeks)

---

## 7. ETHICAL CONSIDERATIONS

### 7.1 Privacy Protection

- **Informed Consent:** Users explicitly consent to participate in federated training
- **Data Minimization:** Only model updates (not raw images) leave devices
- **Right to Withdraw:** Users can opt-out anytime without penalties
- **Transparency:** Clear explanations of what data is shared and how

### 7.2 Research Ethics

- **IRB Approval:** Ethics clearance from Makerere University review board
- **Anonymization:** User identifiers removed from published results
- **Vulnerability Assessment:** Security audits to prevent exploitation
- **Bias Mitigation:** Testing across diverse demographics to ensure fairness

### 7.3 Responsible AI

- **Fairness:** Evaluate model performance across different user groups
- **Accountability:** Clear documentation of system limitations
- **Robustness:** Protection against adversarial attacks and poisoning
- **Explainability:** Users can understand why certain predictions are made

---

## 8. BUDGET AND RESOURCES

### 8.1 Infrastructure Costs

| Item | Specification | Monthly Cost | Duration | Total |
|------|--------------|--------------|----------|-------|
| Cloud Server | 4 vCPU, 16GB RAM | $80 | 9 months | $720 |
| Database | PostgreSQL (Managed) | $25 | 9 months | $225 |
| Object Storage | 100GB MinIO/S3 | $10 | 9 months | $90 |
| Domain & SSL | federated-ai.com | $15 | 1 year | $15 |
| **Subtotal** | | | | **$1,050** |

### 8.2 Development Resources

| Item | Specification | Cost |
|------|--------------|------|
| Android Test Devices | 3 devices (various specs) | $600 |
| Developer Tools | Android Studio, PyCharm Pro | $200 |
| API Services | SMS, email notifications | $50 |
| **Subtotal** | | **$850** |

### 8.3 Research Expenses

| Item | Cost |
|------|------|
| User participant incentives (30 users × $10) | $300 |
| Internet data bundles for testing | $100 |
| Conference submission fees | $150 |
| **Subtotal** | **$550** |

**Total Budget: $2,450 USD**

*(Note: Seeking departmental funding and potential industry sponsorship)*

---

## 9. RISKS AND MITIGATION STRATEGIES

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Low user adoption** | Medium | High | Gamification, incentives, clear value proposition |
| **Network connectivity issues** | High | Medium | Offline-first design, resumable uploads |
| **Model convergence failure** | Low | High | Multiple FL strategies, hyperparameter tuning |
| **Privacy attacks successful** | Low | Critical | Security audits, differential privacy, secure aggregation |
| **Device compatibility problems** | Medium | Medium | Extensive testing, minimum SDK support (API 26+) |
| **Server downtime** | Low | High | Cloud deployment with auto-scaling, backups |
| **Thesis timeline overrun** | Medium | High | Agile sprints, regular supervisor meetings, buffer time |

---

## 10. REFERENCES

1. McMahan, H. B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-efficient learning of deep networks from decentralized data. In *Proceedings of the 20th International Conference on Artificial Intelligence and Statistics (AISTATS)*.

2. Bonawitz, K., Ivanov, V., Kreuter, B., Marcedone, A., McMahan, H. B., Patel, S., ... & Seth, K. (2017). Practical secure aggregation for privacy-preserving machine learning. In *Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security*.

3. Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., ... & Adam, H. (2017). MobileNets: Efficient convolutional neural networks for mobile vision applications. *arXiv preprint arXiv:1704.04861*.

4. Beutel, D. J., Topal, T., Mathur, A., Qiu, X., Parcollet, T., & Lane, N. D. (2020). Flower: A friendly federated learning research framework. *arXiv preprint arXiv:2007.14390*.

5. Kairouz, P., McMahan, H. B., Avent, B., Bellet, A., Bennis, M., Bhagoji, A. N., ... & Zhao, S. (2021). Advances and open problems in federated learning. *Foundations and Trends in Machine Learning*, 14(1-2), 1-210.

6. He, C., Li, S., So, J., Zeng, X., Zhang, M., Wang, H., ... & Avestimehr, S. (2020). FedML: A research library and benchmark for federated machine learning. *arXiv preprint arXiv:2007.13518*.

7. Jeong, E., Oh, S., Kim, H., Park, J., Bennis, M., & Kim, S. L. (2018). Communication-efficient on-device machine learning: Federated distillation and augmentation under non-IID private data. *arXiv preprint arXiv:1811.11479*.

8. Dwork, C. (2006). Differential privacy. In *International colloquium on automata, languages, and programming* (pp. 1-12). Springer, Berlin, Heidelberg.

9. Li, T., Sahu, A. K., Zaheer, M., Sanjabi, M., Talwalkar, A., & Smith, V. (2020). Federated optimization in heterogeneous networks. *Proceedings of Machine Learning and Systems*, 2, 429-450.

10. Rieke, N., Hancox, J., Li, W., Milletari, F., Roth, H. R., Albarqouni, S., ... & Cardoso, M. J. (2020). The future of digital health with federated learning. *NPJ digital medicine*, 3(1), 1-7.

---

## 11. CONCLUSION

This research proposes a comprehensive federated learning system for privacy-preserving object detection on mobile devices. By enabling collaborative model training without sharing raw data, the system addresses critical privacy concerns while maintaining model performance. The research is particularly relevant for Uganda and East Africa, where data privacy, connectivity challenges, and localized AI models are pressing needs.

The project combines rigorous academic research with practical system development, promising both theoretical contributions and real-world impact. Through careful evaluation across multiple dimensions—model performance, system efficiency, privacy guarantees, and user experience—this research will provide valuable insights into the feasibility and challenges of deploying federated learning systems in developing contexts.

---

## APPENDICES

### Appendix A: Supervisor Approval

_[To be signed by supervisor]_

I have reviewed this proposal and approve the student to proceed with the research.

**Supervisor Name:** ___________________________  
**Signature:** ___________________________  
**Date:** ___________________________

### Appendix B: System Screenshots

_[To be added during implementation]_

### Appendix C: Preliminary Results

_[To be updated as research progresses]_

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Pending Approval
