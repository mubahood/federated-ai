# Design and Evaluation of a Blockchain-Based Federated Learning System with Early Warning for Foot-and-Mouth Disease in Ugandan Cattle Farms

**Student:** Muhindo Mubaraka  
**Student Number:** 2400725633  
**Programme:** Master of Computer Science (MCSC) - 2024 Class  
**Registration Number:** 2024/HD05/25633U  
**Institution:** Makerere University  
**Date:** 19 November 2025

---

## 1. Introduction

Imagine a farmer in rural Uganda whose cattle show signs of disease. By the time lab tests confirm an outbreak, the disease has already spread to neighboring farms. Meanwhile, veterinary officers across fifty districts collect similar data, but each works in isolation. The data that could save herds sits scattered across phones, paper forms, and disconnected databases—never pooling together to reveal the bigger picture.

This is not just an agricultural problem. It's a fundamental challenge in how we build intelligent systems for the real world. Today's artificial intelligence learns best when it can see everything—every patient record, every sensor reading, every image. But what happens when privacy laws forbid data sharing? When internet connections are too slow to move gigabytes of information? When farmers rightfully refuse to send their farm data to distant servers?

Traditional machine learning demands we gather all data in one place, train a model, then send it back out. This approach breaks down in scenarios where data is sensitive, spread across many locations, and subject to strict privacy regulations. We need a fundamentally different approach—one where intelligence emerges from collaboration without compromising data ownership.

This research tackles that challenge head-on. We're designing a system where AI learns from distributed data sources without ever collecting the raw information. Farm-level data stays on local devices. Only the learned insights travel across the network. And to ensure everyone plays fair—to prevent malicious actors from poisoning the model—we use blockchain technology to create an auditable, trustworthy learning process.

The scientific contribution here isn't just about predicting disease in cattle. It's about proving that we can build reliable, privacy-preserving AI systems that work in resource-constrained environments. The livestock disease scenario serves as our testbed because it presents real challenges: unreliable connectivity, privacy concerns, multiple independent data sources, and life-or-death consequences for getting predictions right.

This proposal lays out a roadmap for building, testing, and evaluating such a system. We'll combine federated learning (where models train on distributed data) with blockchain verification (where every contribution is recorded and validated). The result will be the first open-source, production-ready framework for decentralized early warning systems—applicable far beyond agriculture to healthcare, disaster response, and any domain where data sharing is problematic but collective intelligence is essential.

---

## 2. Background

### 2.1 The Problem with Centralized Learning

For the past decade, machine learning has achieved remarkable success by following a simple recipe: gather massive amounts of data in one place, feed it to powerful algorithms, and let them discover patterns. This centralized approach powered breakthroughs in image recognition, language translation, and medical diagnosis. But it comes with serious limitations.

**Privacy Risks:** When hospitals send patient data to cloud servers for AI training, they expose sensitive information to potential breaches. When farmers upload farm records, they lose control over proprietary information. Data breaches make headlines regularly, and regulations like GDPR and Uganda's Data Protection Act now restrict how personal data can be shared and processed.

**Infrastructure Demands:** Centralized learning requires reliable, high-speed internet to move data and powerful servers to process it. In rural Uganda—and across much of Sub-Saharan Africa—these resources are scarce. Uploading thousands of animal health records from a district veterinary office might take hours or fail completely.

**Regulatory Barriers:** Many countries now require that certain types of data stay within national borders. Healthcare data, financial records, and government information often cannot legally be sent to foreign cloud providers. This "data sovereignty" concern makes cross-border collaboration difficult.

**Resource Inefficiency:** Why move raw data when you could move just the insights? Uploading gigabytes of farm images to train a disease detection model wastes bandwidth. The model parameters that result from training are typically much smaller—often just a few megabytes.

### 2.2 Enter Federated Learning

Federated learning flips the traditional approach. Instead of bringing data to the model, it brings the model to the data. Here's how it works in simple terms:

1. A central coordinator sends an initial AI model to multiple participants (farms, hospitals, phones)
2. Each participant trains the model on their local data privately
3. Only the model updates (not raw data) are sent back to the coordinator
4. The coordinator combines these updates to improve the global model
5. The improved model goes back to participants, and the cycle repeats

This approach offers compelling advantages. Data never leaves its source, addressing privacy concerns. Bandwidth requirements drop dramatically because only model updates travel across networks. And participants retain ownership of their information while still benefiting from collective learning.

Google pioneered this technique for improving smartphone keyboard predictions without reading your messages. Hospitals use it to train diagnostic models without sharing patient records. But the technology still faces a critical weakness: **trust**.

### 2.3 The Trust Problem

Federated learning assumes all participants act honestly. But what if someone doesn't? A malicious participant could send poisoned model updates designed to corrupt the global model. A lazy participant could submit random noise while benefiting from others' work. Without a way to verify contributions and enforce fair play, federated learning systems remain vulnerable.

This is where blockchain technology enters the picture. Blockchain provides a tamper-proof ledger where every contribution is recorded, verified, and permanently stored. Combined with cryptographic proofs, it can ensure that:

- Model updates come from legitimate participants
- Contributions are fairly rewarded based on their quality
- Malicious behavior is detected and penalized
- The entire training history remains auditable

### 2.4 Why This Matters for Uganda

Uganda's livestock sector exemplifies the challenges we aim to solve. Foot-and-Mouth Disease causes millions of shillings in losses annually. Early detection could save herds, but currently:

- Veterinary data sits isolated in district offices
- Farmers lack real-time risk assessments
- Lab results take days to reach affected areas
- No system learns from past outbreaks to predict future ones

Recent research by Kapalaga and colleagues (2024) created Uganda's first unified FMD dataset by merging records from multiple agencies. Their work showed that machine learning models can predict outbreaks with 92% accuracy—but only when environmental conditions remain stable. When rainfall and temperature patterns shifted (as climate change makes increasingly common), accuracy plummeted to 46%. This dramatic performance degradation highlights why static, centrally-trained models fail in dynamic real-world conditions.

Our research asks: What if we could build a system that continuously learns from new data across all districts, adapts to changing environmental conditions, protects farmer privacy, and prevents malicious interference—all while working within Uganda's infrastructure constraints?

The scientific value extends far beyond agriculture. Success here demonstrates how to build trustworthy AI for any scenario involving distributed data sources, privacy requirements, and adversarial threats. Healthcare diagnostics, financial fraud detection, disaster response systems—all could benefit from this architecture.

---

## 3. Literature Review

To understand what's been done and what gaps remain, we examined four key papers that represent the state of the art in federated learning, blockchain integration, and disease prediction systems.

### 3.1 Paper 1: A Unified FMD Dataset for Uganda (Kapalaga et al., 2024)

**What They Did:**

Kapalaga and his team at Makerere University tackled a fundamental problem: Uganda's animal disease data was scattered across multiple agencies with no common format. The National Animal Disease Diagnostic Centre (NADDEC) recorded confirmed outbreaks. The World Organization for Animal Health (WOAH) tracked regional patterns. The Uganda National Meteorological Authority (UNMA) collected climate data. But no one had combined these sources into a unified dataset suitable for machine learning.

The researchers spent months reconciling data from 2011-2022 across 50 Ugandan districts. They merged outbreak records with climate variables (daily rainfall and maximum temperature), cattle density figures from the 2008 livestock census, and geographic risk factors like proximity to international borders and wildlife protected areas. The result: the first comprehensive FMD prediction dataset for Uganda.

**What They Found:**

They tested seven different machine learning algorithms—from simple logistic regression to sophisticated random forests. When trained and tested on data from stable years (2011-2020), the models performed brilliantly. Random Forest achieved 92% accuracy, 94% recall, and an AUC of 0.97. These are excellent numbers that would justify deploying such a system in practice.

But then came the crucial experiment. They tested these same models on data from 2021-2022—years when rainfall and temperature patterns shifted due to climate change. Performance collapsed. That 92% accuracy dropped to 46%. Recall fell from 94% to just 3%, meaning the model missed 97% of actual outbreaks. The F1-score plunged from 0.92 to 0.06.

**Why It Matters:**

This dramatic failure demonstrates a critical limitation of traditional machine learning: models trained in one set of conditions struggle when conditions change. For early warning systems, this is unacceptable. Climate change ensures that environmental patterns will keep shifting. A model that can't adapt becomes useless within months.

**The Dataset Details:**

For our work, the dataset structure is crucial. Kapalaga's unified dataset includes:

- **Temporal features:** Month and year of observation
- **Location:** District identifier (50 districts)
- **Disease indicators:** Confirmed FMD cases, animals at risk, cumulative case counts
- **Climate variables:** Monthly average rainfall (mm), monthly maximum temperature (°C)
- **Environmental risk factors:** Distance to protected areas (km), distance to international borders (km)
- **Animal density:** Total cattle population per district

The target variable is binary: outbreak (1) or no outbreak (0) for each district-month combination. This creates a supervised learning problem where models predict outbreak probability given environmental and historical conditions.

**What's Missing:**

Kapalaga's work provides excellent data and insights, but it's purely centralized. All data must be collected in one place for training. There's no mechanism for privacy-preserving updates, no way for districts to collaborate without sharing raw data, and no protection against distributional shifts. Their models are static—once trained, they don't adapt to new patterns until someone manually retrains them with fresh data.

### 3.2 Paper 2: Blockchain-Based FL with Verifiable Fairness (Zhang et al., 2023)

**What They Did:**

Zhang and colleagues from Beijing Institute of Technology addressed a different problem: how to make federated learning both private and fair. In standard federated learning, a central server aggregates model updates from participants. But this creates two problems:

1. **Privacy leakage:** The server might infer sensitive information from gradients
2. **Unfairness:** Malicious participants can submit fake updates while benefiting from others' real work

Their solution combines blockchain (Hyperledger Fabric) with advanced cryptography. They introduced two protocols:

**BPNG (Blockchain-based Pseudorandom Number Generation):** Uses verifiable random functions to select participants for each training round. The blockchain generates random numbers that no one can predict or manipulate, ensuring fair selection. Participants can verify the randomness is legitimate through zero-knowledge proofs.

**GRNA (Gradient Random Noise Addition):** Implements differential privacy by adding calibrated noise to model updates. The clever part: participants prove they added the correct amount of noise using zero-knowledge proofs, without revealing the underlying gradients. This ensures privacy while preventing cheating.

**What They Found:**

The system works in practice. Proof generation takes about 19 seconds, and blockchain verification takes 2.3 seconds. These are acceptable delays for most applications. Models trained with their privacy-preserving approach converge successfully, achieving good accuracy even with noise added to gradients.

**Why It Matters:**

This paper proves that blockchain-based federated learning with cryptographic guarantees is feasible, not just theoretical. You can verify fairness and privacy without sacrificing model accuracy or making the system impossibly slow.

**What's Missing:**

The evaluation used only simple models (logistic regression) on small datasets (IRIS with 4,050 samples). Real-world applications involve complex neural networks with millions of parameters. The paper doesn't address how the system scales to larger models, handles non-IID data (where different participants have very different data distributions), or tolerates Byzantine faults (participants actively trying to sabotage the model).

### 3.3 Paper 3: FL in Healthcare - A Systematic Review (Teo et al., 2024)

**What They Did:**

Teo and colleagues from Singapore conducted a massive systematic review of federated learning in healthcare. They screened over 22,000 papers and analyzed 612 studies in detail, examining how FL is used across medical specialties, what technical architectures work, and why so few systems reach clinical deployment.

**What They Found:**

The findings are sobering. Despite years of research and hundreds of papers, only 5.2% of FL systems were real clinical applications. The remaining 94.8% were proof-of-concept studies with simulated data. Radiology dominates the field (lots of imaging data), followed by internal medicine and oncology.

Most systems use horizontal federated learning (different hospitals have different patients but the same features) with centralized aggregation. Neural networks are the most popular models (75% of studies). For privacy, differential privacy is most common (40%), followed by homomorphic encryption (25%).

**The Barriers They Identified:**

1. **Privacy concerns:** Even with FL, model updates can leak information through reconstruction attacks
2. **Data quality:** Non-IID data (different patient populations at different hospitals) hurts model performance
3. **Lack of explainability:** Doctors won't trust black-box models they can't interpret
4. **Infrastructure costs:** Setting up FL systems requires technical expertise and computational resources
5. **No incentive mechanisms:** Why should hospitals contribute data/compute if they don't see direct benefits?
6. **Regulatory uncertainty:** How do existing medical regulations apply to FL systems?

**Why It Matters:**

Healthcare faces the same challenges as livestock disease surveillance: sensitive data spread across independent organizations, privacy regulations preventing centralized collection, and critical decisions based on model predictions. The healthcare review reveals what works, what doesn't, and what gaps must be filled before FL systems see real-world adoption.

**What's Missing:**

The review synthesizes existing work but doesn't propose solutions to the identified barriers. Few studies came from Africa or addressed resource-constrained settings. Incentive mechanisms—crucial for sustaining participation—remain largely unexplored.

### 3.4 Paper 4: FLock - Robust Privacy-Preserving FL (Chen et al., 2024)

**What They Did:**

Chen and colleagues tackled robustness and efficiency simultaneously. They designed FLock, a system that resists poisoning attacks (up to 40% malicious participants) while maintaining privacy and working with practical blockchain platforms (Ethereum, Bitcoin).

Their key innovations:

**MPC-Friendly Aggregation:** Instead of complex similarity metrics to detect poisoned gradients, they use a lightweight approach based on median values and Hamming distances. Convert gradients to binary (+1/-1), take the median, compute how far each participant's update is from the median. Updates far from the median get low weights; those close to the median get high weights.

**Off-Chain State Channels:** Most blockchain FL systems put every model update on-chain, creating huge costs. FLock runs aggregation off-chain in secure multi-party computation channels. Only the final aggregated result and verification proofs go on-chain, slashing costs by orders of magnitude.

**Pipelined Consensus:** While aggregators reach consensus on round N, they simultaneously compute round N+1, doubling throughput.

**What They Found:**

The system works impressively well. With 100 clients and 25 aggregators, FLock completes secure aggregation for a ResNet-20 model (270,000 parameters) in about 2 minutes over realistic wide-area network conditions. It maintains 68% accuracy on CIFAR-10 even with 40% malicious clients trying to poison the model—compared to just 15% accuracy for standard federated averaging.

**Why It Matters:**

FLock demonstrates that you can have robustness, privacy, and blockchain verification without sacrificing performance. The system scales to real neural networks and tolerates significant adversarial behavior.

**What's Missing:**

FLock assumes an honest majority of aggregators. If more than half the aggregators collude, the system fails. The evaluation used standard computer vision benchmarks (MNIST, CIFAR-10), not real-world applications with unique data characteristics. There's no discussion of incentive mechanisms to encourage participation or how to handle time-varying data distributions (like seasonal disease patterns).

### 3.5 Synthesis: What the Literature Tells Us

These four papers together paint a clear picture:

**We can predict diseases with ML** (Kapalaga), but models fail when conditions change.

**We can make FL private and fair** (Zhang), but only at small scales with simple models.

**We know FL's barriers in practice** (Teo), but solutions remain scarce, especially for developing regions.

**We can build robust, efficient blockchain FL** (FLock), but haven't demonstrated it on real-world sequential data with non-stationary distributions.

No one has combined all these pieces. No system exists that:
- Learns from distributed disease surveillance data
- Adapts to changing environmental conditions
- Provides verifiable privacy and fairness guarantees
- Works within Uganda's infrastructure constraints
- Includes incentives to sustain participation
- Delivers actionable early warnings to stakeholders

That's the gap this research aims to fill.

---

## 4. Research Gap

The literature reveals a fundamental disconnect. On one side, we have rich disease datasets that demonstrate the need for adaptive learning systems. On the other side, we have sophisticated federated learning and blockchain protocols that solve privacy and trust problems. But these two worlds have never met in a complete, working system.

**Kapalaga's work** gives us the data and demonstrates the problem (models that can't adapt), but offers no solution architecture.

**Zhang's work** provides verifiable fairness mechanisms, but evaluates them only on trivial datasets with stable distributions.

**Teo's review** catalogs barriers to real-world deployment, but no one has addressed these barriers in a livestock disease context.

**FLock** shows robust aggregation can work at scale, but doesn't tackle domain-specific challenges like seasonal patterns, multi-modal data (clinical signs + climate + movement), or incentive design for agricultural stakeholders.

The specific gaps we identified:

1. **No End-to-End System:** Existing work addresses individual components (data collection, privacy, fairness, robustness) but never integrates them into a complete early warning system.

2. **No Real-World Validation:** Blockchain FL papers use synthetic datasets. Disease prediction papers use centralized learning. No one has validated blockchain FL on actual disease surveillance data.

3. **No Adaptation Mechanisms:** All systems assume static data distributions. None include drift detection, model adaptation, or personalization strategies for handling environmental shifts.

4. **No African Context:** Research focuses on high-resource settings. Questions of intermittent connectivity, limited compute power, and regulatory environments specific to developing countries remain unexplored.

5. **No Incentive Design:** For systems to sustain participation, stakeholders need clear incentives. Current work lacks economic analysis or incentive mechanisms tailored to agricultural contexts.

6. **No Integration with National Systems:** Uganda's ULITS (Uganda Livestock Identification and Traceability System) already tags cattle and tracks movements. No research has explored how to build FL systems on top of existing national infrastructure.

This research bridges these gaps by designing, implementing, and evaluating the first blockchain-based federated learning early warning system for livestock disease that operates on real Ugandan data, handles distribution shifts, and integrates with national traceability infrastructure.

---

## 5. Problem Statement

**How can we design a decentralized, privacy-preserving early warning system that learns from distributed livestock disease surveillance data, adapts to changing environmental conditions, and provides verifiable guarantees of fairness and robustness—all within the infrastructure and regulatory constraints of Sub-Saharan Africa?**

This problem has three dimensions:

**Technical:** Building a system that combines federated learning, blockchain verification, and adaptive algorithms into a working prototype.

**Empirical:** Demonstrating that such a system achieves acceptable accuracy, efficiency, and robustness on real disease surveillance data.

**Practical:** Showing the system can operate within Uganda's infrastructure realities (intermittent internet, limited compute resources) and regulatory requirements (data sovereignty, privacy laws).

Success means proving that advanced AI doesn't require centralized data collection or expensive cloud infrastructure—that we can build intelligent systems that respect privacy, operate in resource-constrained environments, and remain trustworthy even with adversarial participants.

---

## 6. Research Objectives

### Overall Objective

To design, implement, and evaluate a blockchain-based federated learning architecture that enables privacy-preserving, adaptive early warning for livestock disease outbreaks using Uganda's ULITS infrastructure.

### Specific Objectives

**Objective 1: Dataset Development**  
Extend Kapalaga's unified FMD dataset by integrating ULITS cattle identification data, movement records, vaccination histories, and fine-grained climate variables to create a comprehensive, federated-learning-ready dataset with clear data partitioning schemes for distributed training.

**Objective 2: System Architecture Design**  
Design a modular architecture that combines (a) federated learning protocols for distributed model training, (b) blockchain smart contracts for participant verification and incentive distribution, and (c) adaptive learning mechanisms for handling distribution shifts.

**Objective 3: Privacy and Fairness Mechanisms**  
Implement verifiable random selection of participants (inspired by BPNG protocol) and differential privacy with cryptographic proofs (inspired by GRNA) adapted to support neural networks for disease prediction.

**Objective 4: Robust Aggregation**  
Develop aggregation strategies that tolerate Byzantine attacks (inspired by FLock) while accounting for non-IID data distributions typical in cross-district disease surveillance.

**Objective 5: Adaptive Learning**  
Integrate drift detection and model adaptation techniques (such as federated continual learning or meta-learning) to maintain accuracy as environmental conditions change over time.

**Objective 6: System Implementation**  
Build an open-source prototype using Hyperledger Fabric (blockchain), PyTorch/TensorFlow (ML), and Flower framework (FL orchestration), deployed on resource-appropriate hardware similar to district veterinary offices.

**Objective 7: Empirical Evaluation**  
Evaluate the system against centralized and standard federated baselines across multiple metrics: prediction accuracy, privacy guarantees (epsilon values), fairness (Gini coefficient of contributions), robustness (accuracy under attack), latency, and bandwidth consumption.

**Objective 8: Stakeholder Validation**  
Conduct interviews and usability studies with district veterinary officers and farmers to assess practical feasibility, trust perceptions, and willingness to participate in a production deployment.

---

## 7. Research Methodology

This section explains **how** we'll achieve each objective, what methods we'll use, what data we'll work with, and how we'll measure success.

### 7.1 Dataset Development (Objective 1)

**Approach:**

We'll build on Kapalaga's unified FMD dataset by adding layers of information from ULITS and other sources:

**Data Sources:**

1. **ULITS cattle registry:** Electronic ID tags, breed, age, ownership, holding location
2. **ULITS movement permits:** Records of cattle moving between holdings, markets, or districts
3. **District vaccination records:** Dates and types of vaccines administered
4. **NADDEC lab results:** Test confirmations, clinical signs reported
5. **UNMA climate data:** Daily rainfall, min/max temperature, humidity
6. **Sentinel surveillance:** Regular health monitoring at selected farms
7. **Market activity:** Cattle market schedules, trading volumes (if available)

**Dataset Structure:**

We'll organize data into a federated structure where each district holds its own records:

- **District node:** Contains data for cattle registered in that district
- **Temporal granularity:** Daily records aggregated to weekly or monthly for prediction
- **Feature categories:**
  - Animal attributes: breed, age, vaccination status
  - Environmental: rainfall, temperature, seasonality
  - Spatial: distance to borders, protected areas, other outbreak sites
  - Behavioral: movement frequency, market participation
  - Historical: past outbreak occurrences, treatment outcomes

**Target Variable:**

Binary classification: will an outbreak occur in this district in the next 2-4 weeks? (Prediction horizon chosen based on intervention timeframe.)

**Data Partitioning:**

To simulate federated learning, we'll partition data by district (geographic horizontal partitioning). Each district's data represents a local client in the FL system. This creates naturally non-IID data since different districts have different cattle densities, climate patterns, and outbreak histories.

**Preprocessing:**

- Handle missing values (imputation for climate data, exclusion for critical features)
- Normalize continuous variables (z-score standardization district-wise)
- Create temporal features (rolling averages, seasonal indicators)
- Balance classes using SMOTE or undersampling where appropriate
- Split temporally: train on 2011-2020, validate on 2021-2022, test on 2023-2024

**Expected Outcome:**

A cleaned, documented dataset with ~50 client partitions (districts), each containing 50-500 samples (district-month observations) with 15-25 features, ready for federated training experiments.

### 7.2 System Architecture Design (Objective 2)

**Design Process:**

We'll follow a layered architecture approach:

**Layer 1: Data Layer**
- Local data stores at each district node
- Preprocessing pipelines for feature extraction
- Privacy-preserving data handling (encryption at rest)

**Layer 2: Learning Layer**
- PyTorch-based neural network models (starting with feedforward, potentially LSTM for temporal patterns)
- Local training orchestration
- Gradient computation and differential privacy noise addition

**Layer 3: Aggregation Layer**
- Flower framework for FL coordination
- Custom aggregation functions implementing robust averaging
- Model versioning and checkpointing

**Layer 4: Blockchain Layer**
- Hyperledger Fabric network with district nodes as organizations
- Smart contracts for:
  - Participant registration
  - Training round coordination
  - Contribution verification
  - Reward distribution
- Immutable logging of model updates and performance metrics

**Layer 5: Application Layer**
- Web dashboard for veterinary officers
- Alert generation and notification system
- Model performance monitoring
- Audit trail visualization

**Communication Protocols:**

- Secure channels (TLS) for model update transmission
- gRPC for Flower FL communication
- REST APIs for blockchain interaction
- Asynchronous updates to tolerate intermittent connectivity

**Expected Outcome:**

Detailed architecture diagrams, component specifications, and API definitions documented in a technical design document.

### 7.3 Privacy and Fairness Mechanisms (Objective 3)

**Differential Privacy Implementation:**

- Add Laplacian noise to gradients before transmission
- Noise scale calibrated to privacy budget (epsilon = 1-10)
- Track cumulative privacy loss across training rounds
- Implement gradient clipping to bound sensitivity

**Verifiable Randomness:**

Adapt BPNG protocol:
- Blockchain generates random seeds for client selection each round
- Participants verify randomness using VRF proofs
- Prevents coordinator from cherry-picking favorable clients

**Zero-Knowledge Proofs:**

Implement simplified GRNA:
- Clients prove they added correct noise without revealing gradients
- Use existing ZKP libraries (libsnark or zokrates)
- Trade-off: proof generation time vs. verification strength

**Evaluation Metrics:**

- Privacy budget consumption per round
- Success rate of membership inference attacks (to demonstrate privacy)
- Distribution uniformity of client selection (to demonstrate fairness)

**Expected Outcome:**

Documented privacy guarantees (epsilon-delta values), fairness metrics (variance in client selection frequency), and proof generation/verification timings.

### 7.4 Robust Aggregation (Objective 4)

**Baseline: FedAvg**

Start with standard federated averaging: weighted average of client updates proportional to data size.

**Robust Alternatives:**

1. **Median aggregation:** Use coordinate-wise median instead of mean (requires binarization or quantization)
2. **Krum aggregation:** Select updates closest to the majority
3. **FLock-inspired:** Hamming distance weighting after signSGD binarization

**Byzantine Attack Simulation:**

- Randomly select 10-40% of clients as malicious
- Malicious clients submit:
  - Gaussian noise
  - Inverted gradients
  - Scaled gradients
- Measure accuracy degradation with/without defenses

**Non-IID Handling:**

- Test with different data partitioning schemes (IID, label skew, feature skew)
- Implement FedProx (adds proximal term to local objectives)
- Evaluate personalization layers (district-specific batch normalization)

**Expected Outcome:**

Comparison table showing accuracy under different attack scenarios and data distributions for each aggregation method.

### 7.5 Adaptive Learning (Objective 5)

**Drift Detection:**

- Monitor per-district loss distributions over time
- Flag districts where validation loss increases significantly
- Use statistical tests (Kolmogorov-Smirnov) to detect feature distribution shifts

**Adaptation Strategies:**

1. **Periodic retraining:** Regularly retrain on recent data windows
2. **Elastic weight consolidation:** Preserve important parameters while adapting to new patterns
3. **Meta-learning:** Train model to quickly adapt to new districts/conditions
4. **Personalization:** Allow districts to fine-tune global model on local data

**Evaluation:**

- Test on temporally split data (train 2011-2020, test 2023-2024)
- Inject synthetic distribution shifts (alter climate variables)
- Measure accuracy recovery after adaptation vs. static models

**Expected Outcome:**

Demonstration that adaptive approaches maintain accuracy (>80%) even when environmental conditions shift, compared to static models that degrade (as Kapalaga showed).

### 7.6 System Implementation (Objective 6)

**Technology Stack:**

**ML/FL:**
- Python 3.9+
- PyTorch 2.0 or TensorFlow 2.12
- Flower 1.5+ (FL framework)
- NumPy, Pandas, Scikit-learn (data processing)

**Blockchain:**
- Hyperledger Fabric 2.5
- Node.js or Go for smart contracts
- Docker for containerized deployment

**Supporting Infrastructure:**
- PostgreSQL (metadata storage)
- Redis (caching/job queues)
- Flask/FastAPI (web services)
- Grafana (monitoring dashboards)

**Hardware:**

- Simulate district nodes on separate VMs or containers
- Use Raspberry Pi 4 (8GB) as representative edge device
- Central server: standard Ubuntu VM (8 cores, 32GB RAM)

**Development Process:**

1. Implement core FL training loop with Flower
2. Add blockchain layer incrementally
3. Integrate privacy mechanisms
4. Deploy on testbed with 5-10 simulated districts
5. Scale to full 50-district deployment
6. Conduct stress testing and optimization

**Code Quality:**

- Version control (Git/GitHub)
- Unit tests for critical components
- Integration tests for end-to-end workflows
- Documentation (Sphinx/MkDocs)
- Docker images for reproducibility

**Expected Outcome:**

Fully functional prototype with public GitHub repository, installation guide, API documentation, and demo notebooks showing how to train models and query predictions.

### 7.7 Empirical Evaluation (Objective 7)

**Experimental Design:**

We'll compare our system against baselines:

1. **Centralized learning:** Train on pooled data (all districts combined)
2. **Local learning:** Each district trains independently
3. **Standard FedAvg:** Federated learning without blockchain/privacy
4. **FedAvg + DP:** FedAvg with differential privacy
5. **Proposed system:** Full blockchain-based FL with robustness

**Metrics:**

**Accuracy Metrics:**
- Classification accuracy
- Precision, recall, F1-score
- AUC-ROC
- Calibration error (to assess prediction confidence)

**Efficiency Metrics:**
- Communication rounds to convergence
- Total data transmitted per client
- Training time per round
- End-to-end latency for alert generation

**Privacy Metrics:**
- Epsilon (differential privacy budget)
- Success rate of membership inference attacks
- Reconstruction error from gradient inversion attacks

**Fairness Metrics:**
- Gini coefficient of client contributions
- Standard deviation of client selection frequency
- Performance equity (accuracy variance across districts)

**Robustness Metrics:**
- Accuracy under Byzantine attacks (10%, 20%, 30%, 40% malicious)
- Recovery time after attack
- False positive rate for malicious detection

**Scalability Metrics:**
- Performance with varying client counts (10, 25, 50 districts)
- Blockchain transaction throughput
- Smart contract gas costs (if applicable)

**Test Scenarios:**

1. **Baseline performance:** IID data, no attacks, stable conditions
2. **Non-IID data:** Realistic district partitioning with skewed distributions
3. **Byzantine attacks:** Various attack types and fractions
4. **Distribution shift:** Test on 2023-2024 data with climate changes
5. **Connectivity stress:** Simulate intermittent connections, dropouts
6. **Scaling:** Add clients progressively, measure degradation

**Statistical Analysis:**

- Run each experiment 5-10 times with different random seeds
- Report mean and confidence intervals
- Use paired t-tests or Wilcoxon tests for comparing methods
- Apply Bonferroni correction for multiple comparisons

**Expected Outcome:**

Comprehensive results tables and plots showing:
- Our system achieves accuracy within 5% of centralized baseline
- Privacy budget epsilon < 10 with < 2% accuracy loss
- Tolerates up to 30% malicious clients with < 10% accuracy drop
- Maintains >75% accuracy under distribution shifts (vs. <50% for static models)
- Communication costs 10-50× lower than centralized approaches
- Fairness metrics within acceptable ranges (Gini < 0.3)

### 7.8 Stakeholder Validation (Objective 8)

**Qualitative Methods:**

1. **Semi-structured interviews** with 10-15 district veterinary officers
   - Questions about current workflows, pain points, data practices
   - Reactions to system demo (usability, trust, perceived value)
   - Concerns about privacy, fairness, blockchain complexity
   - Willingness to adopt in practice

2. **Focus groups** with 2-3 farmer cooperatives
   - Understanding of system benefits/risks
   - Trust in automated predictions vs. expert opinions
   - Incentive preferences (financial vs. information access)

3. **Usability testing**
   - Task-based evaluation: viewing alerts, understanding predictions, accessing audit logs
   - System Usability Scale (SUS) questionnaire
   - Time to complete tasks, error rates

**Quantitative Surveys:**

- Trust in AI systems (5-point Likert scale)
- Privacy concern levels
- Technology acceptance model questions
- Willingness to participate (hypothetical scenarios)

**Ethics:**

- Obtain IRB approval from Makerere University
- Informed consent from all participants
- Anonymize responses in publications
- Compensate participants for their time

**Expected Outcome:**

Qualitative themes (concerns, adoption barriers, suggestions) and quantitative metrics (SUS scores, trust levels) demonstrating practical feasibility and identifying areas for refinement before production deployment.

---

## 8. Process Workflow Diagram (Description)

This section provides a detailed textual description of the system's workflow, which will be converted into a visual diagram.

### Phase 1: System Initialization

1. **Blockchain Network Setup**
   - Deploy Hyperledger Fabric network with 50 district nodes as organizations
   - Install smart contracts for participant management and reward distribution
   - Initialize global model parameters on blockchain

2. **Participant Registration**
   - District veterinary offices register as FL clients with blockchain identities
   - Provide public keys for secure communication
   - Specify compute capabilities and connectivity profiles
   - Receive initial global model

### Phase 2: Local Data Collection (Continuous)

3. **Farm-Level Data Entry**
   - Farmers report cattle health observations via mobile app or SMS
   - District officers record lab test results, vaccination events
   - ULITS system captures movement permits, market activities
   - Climate stations push daily weather data

4. **Local Data Processing**
   - District node preprocesses incoming data (validation, cleaning)
   - Extracts features according to global schema
   - Updates local training dataset (stored encrypted on local storage)
   - Never sends raw data outside district boundaries

### Phase 3: Federated Training Round

5. **Client Selection**
   - Blockchain smart contract generates verifiable random seed
   - Random selection algorithm picks 20-30 districts for this round
   - Selected clients receive notification and download latest global model

6. **Local Training**
   - Each selected client trains model on local data for E epochs
   - Computes gradients or parameter updates
   - Adds differential privacy noise to gradients (calibrated to epsilon budget)
   - Generates zero-knowledge proof that noise was added correctly

7. **Update Transmission**
   - Client uploads encrypted model update to aggregation server
   - Submits ZK proof to blockchain for verification
   - Records update hash on blockchain (immutable audit trail)
   - Awaits aggregation result

8. **Secure Aggregation**
   - Aggregation server (or committee of aggregators) collects updates
   - Verifies ZK proofs via blockchain smart contract
   - Applies robust aggregation (e.g., weighted median or FLock-style)
   - Detects and filters outlier updates (potential attacks)

9. **Global Model Update**
   - Aggregate new global model from verified client updates
   - Store model checkpoint on blockchain (hash pointer)
   - Broadcast updated model to all clients (not just participants)
   - Update blockchain state with round statistics

### Phase 4: Early Warning Generation

10. **Continuous Prediction**
    - Each district runs latest global model on recent local data
    - Generates outbreak probability for next 2-4 weeks
    - Computes confidence intervals and explanatory features

11. **Risk Assessment**
    - Central dashboard aggregates predictions from all districts
    - Identifies high-risk regions (probability > threshold, e.g., 0.7)
    - Considers spatial clustering (multiple neighboring districts at risk)

12. **Alert Dissemination**
    - Generate alert messages for high-risk districts
    - Deliver via multiple channels: SMS, email, web dashboard, mobile app
    - Include: risk level, confidence, contributing factors (rainfall spike, nearby outbreak)
    - Provide recommended actions (enhanced surveillance, movement restrictions)

### Phase 5: Monitoring and Adaptation

13. **Performance Monitoring**
    - Track prediction accuracy as ground truth emerges
    - Monitor model calibration (are predicted probabilities accurate?)
    - Detect performance degradation by district or globally

14. **Drift Detection**
    - Analyze feature distributions over time
    - Flag significant deviations from training distribution
    - Trigger adaptation mechanisms when drift exceeds threshold

15. **Model Adaptation**
    - Initiate retraining on recent data windows
    - Apply meta-learning for quick adaptation
    - Allow districts to personalize model (fine-tune on local data)
    - Update global model more frequently during drift periods

### Phase 6: Incentive Distribution

16. **Contribution Scoring**
    - Smart contract evaluates each participant's contribution quality
    - Metrics: data quantity, model improvement, prediction accuracy on validation set
    - Compute normalized contribution scores

17. **Reward Allocation**
    - Distribute tokens or credits proportional to contribution scores
    - Record transactions on blockchain (transparent, auditable)
    - Allow participants to redeem rewards (data access, priority support, financial)

### Phase 7: Audit and Governance

18. **Audit Trail**
    - All training rounds, model updates, alerts logged immutably
    - Regulators or stakeholders can verify system behavior
    - Detect anomalies, investigate failures, ensure compliance

19. **Governance**
    - Stakeholders vote on system parameters (privacy budget, reward rates)
    - Upgrade smart contracts through consensus
    - Add/remove participants based on reputation scores

---

## 9. Expected Contributions

This research will deliver contributions across multiple dimensions:

### 9.1 Scientific Contributions

**Novel System Architecture:**  
The first complete reference architecture combining federated learning, blockchain verification, and adaptive mechanisms for disease early warning. This architectural pattern applies beyond agriculture to any domain requiring privacy-preserving, distributed learning with accountability.

**Empirical Evidence on Robustness:**  
Quantitative demonstration of how blockchain-based verification improves resistance to Byzantine attacks in real-world FL scenarios with non-IID data, filling a gap in current literature.

**Adaptation to Distribution Shifts:**  
Systematic comparison of drift detection and model adaptation techniques in the context of federated learning, showing which strategies maintain accuracy under environmental changes.

**Privacy-Utility Trade-offs:**  
Detailed analysis of how differential privacy levels (epsilon values) affect model accuracy, convergence speed, and practical usability in resource-constrained settings.

### 9.2 Technical Contributions

**Open-Source Prototype:**  
A production-ready, documented, extensible codebase that researchers and practitioners can use as a foundation for their own blockchain FL systems. Includes:
- Modular components (easy to swap aggregation methods, models, blockchain platforms)
- Docker containers for easy deployment
- Example datasets and training scripts
- Comprehensive API documentation

**ULITS-Enhanced FMD Dataset:**  
The first publicly available (subject to privacy clearances) federated learning dataset for livestock disease that includes movement records, vaccination histories, and fine-grained environmental data. This benchmark enables future research in adaptive FL.

**Performance Benchmarks:**  
Baseline performance numbers for blockchain FL on realistic disease surveillance tasks, helping future researchers assess whether their innovations represent genuine improvements.

### 9.3 Practical Contributions

**Stakeholder Insights:**  
Understanding of trust perceptions, privacy concerns, and adoption barriers among Ugandan veterinary professionals and farmers. These qualitative insights guide system refinement for real deployment.

**Deployment Blueprint:**  
Step-by-step guide for deploying blockchain FL systems in developing-country contexts, including infrastructure requirements, regulatory considerations, training needs, and cost estimates.

**Policy Recommendations:**  
Evidence-based recommendations for policymakers on data governance, privacy regulations, and incentive structures to enable collaborative AI while protecting stakeholders.

### 9.4 Broader Impact

**Demonstrating Viable Alternatives to Centralization:**  
Proving that sophisticated AI doesn't require centralized data collection empower organizations and individuals to participate in machine learning without sacrificing privacy or autonomy.

**Capacity Building:**  
Training Ugandan students and professionals in cutting-edge FL and blockchain technologies, building local expertise for future digital agriculture initiatives.

**Foundation for Future Work:**  
Establishing infrastructure and methods that can extend to other diseases (African swine fever, peste des petits ruminants), other countries in East Africa, and other sectors (healthcare, finance, smart cities).

---

## 10. Timeline and Milestones

**Month 1-3: Literature Review and Dataset Development**
- Complete in-depth review of FL, blockchain, and disease prediction literature
- Obtain ethics approval and data access agreements
- Clean and integrate ULITS data with Kapalaga's dataset
- Create federated data partitions

**Month 4-6: System Design and Implementation**
- Finalize architecture design
- Implement core FL training loop with Flower
- Set up Hyperledger Fabric network
- Integrate blockchain with FL system

**Month 7-9: Privacy and Robustness Implementation**
- Add differential privacy mechanisms
- Implement verifiable randomness and ZK proofs
- Develop robust aggregation methods
- Conduct security testing

**Month 10-12: Adaptive Learning and Dashboard**
- Implement drift detection and adaptation strategies
- Build early warning dashboard
- Integrate all system components
- Conduct end-to-end testing

**Month 13-15: Empirical Evaluation**
- Run baseline and comparison experiments
- Collect performance metrics across scenarios
- Analyze results and identify system improvements
- Iterate on weak points

**Month 16-18: Stakeholder Validation**
- Conduct interviews and focus groups
- Perform usability testing
- Analyze qualitative feedback
- Refine system based on stakeholder input

**Month 19-21: Thesis Writing and Publication**
- Draft thesis chapters
- Prepare conference/journal papers
- Create demonstration videos and documentation
- Finalize open-source code release

**Month 22-24: Defense and Dissemination**
- Present at conferences
- Defend thesis
- Publish datasets and code
- Train potential users

---

## 11. Budget and Resources

**Computing Resources:**
- Cloud VMs for development and testing (AWS, Azure, or local HPC cluster)
- 50+ containerized nodes for federated simulation
- GPU access for model training (can use Google Colab or university resources)

**Software:**
- All open-source tools (Flower, Hyperledger Fabric, PyTorch, etc.)
- No licensing costs

**Data Collection:**
- Travel to district offices for interviews (budgeted separately)
- Participant compensation for usability studies
- Mobile data costs for field testing

**Supervision and Collaboration:**
- Regular meetings with university supervisors
- Potential collaboration with NADDEC, ULITS administrators
- Peer review and feedback from FL/blockchain research communities

---

## 12. Ethical Considerations

**Data Privacy:**
- All personally identifiable information (farmer names, specific locations) will be anonymized
- Raw data never leaves district boundaries
- Aggregated insights only shared with explicit consent

**Informed Consent:**
- All research participants (interview subjects, pilot users) will receive clear explanations of the system and provide written consent
- Participation is voluntary with right to withdraw

**Responsible AI:**
- Model predictions are decision-support tools, not autonomous decisions
- Veterinary officers retain authority and judgment
- System designed to be transparent and explainable

**Benefit Sharing:**
- Results published open-access
- Software released under permissive license
- Training provided to local stakeholders
- System designed to benefit all districts, not extract value

**Environmental Impact:**
- Federated learning reduces data center energy consumption
- Blockchain energy usage minimized by using Hyperledger (not proof-of-work)

---

## 13. Conclusion

This research addresses a fundamental challenge in modern artificial intelligence: how to build intelligent systems that learn from distributed data without compromising privacy, security, or fairness. By combining federated learning with blockchain verification, we create a trustworthy foundation for collaborative machine learning in high-stakes domains.

The livestock disease use case provides a rigorous testbed with real challenges—privacy concerns, infrastructure constraints, adversarial threats, and non-stationary data distributions. Success here demonstrates principles applicable far beyond agriculture.

We're not just building a disease prediction system. We're pioneering a new paradigm for decentralized AI—one where data ownership remains with those who generated it, where contributions are verifiably fair, where systems adapt to changing conditions, and where trust is earned through transparency rather than assumed through authority.

The outcome will be open-source tools, empirical evidence, and practical insights that advance the science of privacy-preserving machine learning while delivering tangible benefits to Ugandan livestock keepers. It's research with both theoretical rigor and real-world impact.

---

## 14. References

1. Kapalaga, G., Kivunike, F.N., Kerfua, S., Jjingo, D., Biryomumaisho, S., Rutaisire, J., Ssajjakambwe, P., Mugerwa, S., & Kiwala, Y. (2024). A unified Foot and Mouth Disease dataset for Uganda: evaluating machine learning predictive performance degradation under varying distributions. *Frontiers in Artificial Intelligence*, 7, 1446368. DOI: 10.3389/frai.2024.1446368

2. Zhang, Y., Tang, Y., Zhang, Z., Li, M., Li, Z., Khan, S., Chen, H., & Cheng, G. (2023). Blockchain-Based Practical and Privacy-Preserving Federated Learning with Verifiable Fairness. *Mathematics*, 11(5), 1091. DOI: 10.3390/math11051091

3. Teo, Z.L., Jin, L., Li, S., Miao, D., Zhang, X., Ng, W.Y., Tan, T.F., Lee, D.M., Chua, K.J., Heng, J., Liu, Y., Goh, R.S.M., & Ting, D.S.W. (2024). Federated machine learning in healthcare: A systematic review on clinical applications and technical architecture. *Cell Reports Medicine*, 5(2), 101419. DOI: 10.1016/j.xcrm.2024.101419

4. Chen, R., Dong, Y., Liu, Y., Fan, T., Li, D., Guan, Z., Liu, J., & Zhou, J. (2024). FLock: Robust and Privacy-Preserving Federated Learning based on Practical Blockchain State Channels. *Cryptology ePrint Archive*, Paper 2024/1797.

5. McMahan, B., Moore, E., Ramage, D., Hampson, S., & Arcas, B.A. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data. *Proceedings of the 20th International Conference on Artificial Intelligence and Statistics (AISTATS)*.

6. Bonawitz, K., Ivanov, V., Kreuter, B., Marcedone, A., McMahan, H.B., Patel, S., Ramage, D., Segal, A., & Seth, K. (2017). Practical Secure Aggregation for Privacy-Preserving Machine Learning. *Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security*.

7. Li, T., Sahu, A.K., Zaheer, M., Sanjabi, M., Talwalkar, A., & Smith, V. (2020). Federated Optimization in Heterogeneous Networks. *Proceedings of Machine Learning and Systems (MLSys)*.

8. Kairouz, P., McMahan, H.B., Avent, B., et al. (2021). Advances and Open Problems in Federated Learning. *Foundations and Trends in Machine Learning*, 14(1-2), 1-210.

---

**End of Proposal**
