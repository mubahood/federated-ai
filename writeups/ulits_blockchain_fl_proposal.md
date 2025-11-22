# Design and Evaluation of a Blockchain-Governed Federated Learning Early Warning System for Ugandan Livestock

**Date:** 19 November 2025  
**Prepared by:** Federated AI Research Team, School of Computing and Informatics Technology, Makerere University

---

## 1. Introduction

Distributed sensing and data-driven decision support are now central to managing transboundary animal diseases, yet most deployments still depend on central clouds that require bulk data transfers, manual trust agreements, and months-long validation cycles. These constraints make it hard to deliver early warnings to livestock keepers operating in bandwidth-limited or regulation-heavy environments.

Foot-and-mouth disease (FMD) surveillance in Uganda offers a scientifically rich testbed because the country already gathers multi-source evidence (diagnostics, climate streams, cattle census) but still experiences sharp performance drops in predictive models once rainfall and temperature regimes shift. Rather than centering the narrative on the pathology itself, this project treats FMD as an exemplar use case to rigorously test a new class of verifiable, fairness-aware federated learning (FL) pipelines.

The proposed research will design, implement, and evaluate a blockchain-governed FL architecture that couples the Uganda Livestock Identification and Traceability System (ULITS) data backbone with privacy-preserving model aggregation, verifiable incentive mechanisms, and drift-resistant monitoring. The resulting artefact aims to advance the science of trustworthy federated analytics for any high-stakes, non-stationary domain.

## 2. Background and Motivation

### 2.1 Limitations of Centralized Analytics

- National veterinary services rely on periodic uploads to single data centers, creating single points of failure and long feedback loops.
- Kapalaga et al. (2024) showed that a Random Forest trained on Uganda’s unified FMD dataset drops from 92% to 46% accuracy once climate-induced distribution shifts occur, underscoring how static models collapse when confronted with out-of-distribution samples.
- Static pipelines seldom capture granular livestock movements, micro-climate anomalies, or farmer-submitted symptoms in near real time, so public alerts often lag behind field realities.

### 2.2 Need for Verifiable Federated Coordination

- Flower-style FL servers can orchestrate model updates across veterinary districts, but without verifiability malicious or low-effort clients can poison models or free-ride.
- Blockchain primitives (verifiable randomness, immutable audit logs, programmable incentives) can provide strong guarantees, yet existing prototypes either ignore model robustness or incur prohibitive on-chain costs.
- ULITS already tags cattle and herds, making it a natural anchor for binding cryptographic identities to data provenance.

## 3. Literature Review

### 3.1 Kapalaga et al., 2024 – Unified FMD Dataset for Uganda

- Integrated NADDEC, WOAH, UNMA, border proximity, and cattle density records across 50 districts (2011–2022).
- Demonstrated severe model brittleness under rainfall and temperature shifts (rec recall collapsed from 0.94 to 0.03 for Random Forest), thereby quantifying the magnitude of non-stationarity to be expected in real deployments.
- Provided a transparent preprocessing pipeline (imputation, z-score outlier removal, SMOTE variants) that this project can adopt for initializing ULITS features.

### 3.2 Zhang et al., 2023 – Blockchain-Based Practical FL with Verifiable Fairness

- Introduced the BPNG protocol for verifiable random client selection and GRNA for differential privacy noise with zero-knowledge proofs, implemented on Hyperledger Fabric.
- Reported average proof generation of 18.993 s and on-chain verification of 2.27 s for logistic regression, proving that verifiable fairness is feasible at moderate scale.
- The curious-but-honest threat model leaves open questions about Byzantine resilience, but the protocols supply a blueprint for certifying privacy budgets in our pipeline.

### 3.3 Teo et al., 2024 – Systematic Review of Healthcare FL

- Screened 22,693 records and analyzed 612 federated healthcare studies; only 5.2% reached real clinical deployment, citing privacy, data quality, incentive, and infrastructure gaps.
- Radiology and internal medicine dominated, showing that FL is most useful where cross-organization data locking is severe—an insight that equally applies to livestock traceability between districts.
- Highlights the empirical need to report multi-metric performance, incentive adoption, and regulatory alignment, which this proposal embeds into its evaluation plan.

### 3.4 Chen et al., 2024 – FLock MPC-Friendly Robust Aggregation

- Proposed an MPC pipeline combining signSGD binarization, Shamir secret sharing, and Hamming-distance scoring, achieving <3-minute aggregation for ResNet-20 with 100 clients and 25 aggregators over WAN.
- Demonstrated tolerance to up to 40% malicious clients while sustaining 68% accuracy on CIFAR-10—valuable evidence that robustness and privacy can co-exist with state-channel-enabled blockchain incentives.
- Offers concrete optimizations (sum-then-degree-reduction, pipelined BFT) that will guide our secure aggregation engine.

### 3.5 Synthesis Table

| Study | Technical Contribution | Key Limitation | Implication for This Work |
|-------|-----------------------|----------------|---------------------------|
| Kapalaga et al. (2024) | Unified multi-source FMD dataset; quantified distribution shift impact (92%→46% accuracy) | No adaptive learning or decentralized deployment | Use dataset schema + shift metrics to benchmark drift detectors and personalization layers. |
| Zhang et al. (2023) | BPNG + GRNA protocols for verifiable fairness and privacy on Hyperledger Fabric | Evaluated only on logistic regression; assumes curious-but-honest clients | Adapt verifiable randomness + DP proofs to higher-dimensional vision models while extending to Byzantine settings. |
| Teo et al. (2024) | Evidence base of 612 healthcare FL studies; taxonomy of architectures and barriers | Few African deployments; limited incentive design coverage | Align system reporting with clinical translation criteria (privacy, incentives, regulatory readiness). |
| Chen et al. (2024) | MPC-friendly robust aggregation with blockchain state channels (FLock) | Requires honest-majority aggregators; binarization may limit accuracy | Combine FLock-style aggregation with adaptive precision and ULITS-specific incentives. |

## 4. Research Gap

Existing work either (a) curates high-quality datasets without addressing continual, privacy-preserving model updates (Kapalaga et al.), or (b) builds blockchain-enhanced FL prototypes on synthetic data without confronting real non-IID, multi-modal livestock signals (Zhang et al., Chen et al.). None integrates a national traceability backbone such as ULITS with verifiable fairness, robust aggregation, and climate-aware personalization. Consequently, there is no end-to-end methodology for building, auditing, and deploying an FL early-warning system that remains accurate when distributions drift and stakeholders demand cryptographic accountability.

## 5. Problem Statement

*How can we architect, implement, and empirically validate a blockchain-governed federated learning pipeline that ingests ULITS-enhanced livestock data, withstands non-IID distribution shifts, and provides verifiable privacy, fairness, and incentive guarantees for early warning applications in Uganda?*

## 6. Research Objectives

### Overall Objective
 
Design and evaluate a scientifically rigorous FL architecture that fuses ULITS data, blockchain-verifiable coordination, and robust aggregation to deliver adaptive early warnings without exchanging raw livestock records.

### Specific Objectives

1. **Data Fusion:** Extend the ULITS schema with Kapalaga-style climate and risk factors, delivering a harmonized dataset with documented lineage, quality metrics, and labeling functions.
2. **Secure Coordination:** Implement verifiable randomness, differential privacy, and incentive distribution on a permissioned blockchain to govern FL participation.
3. **Robust Learning:** Develop and benchmark aggregation strategies (FLock-inspired MPC, clustering, personalization layers) that tolerate distribution shifts and Byzantine updates.
4. **Monitoring & Early Warning:** Build drift detectors and alerting logic that translate global and client-level metrics into actionable warnings for district veterinarians.
5. **Empirical Evaluation:** Conduct cross-silo experiments on historical ULITS data plus simulated online updates, reporting accuracy, AUC, convergence time, privacy budgets, incentive uptake, and system costs.

## 7. Methodology

### 7.1 Research Design

A Design Science Research (DSR) process will guide the work:

1. Diagnose limitations of current surveillance (problem awareness).
2. Specify artefact requirements (verifiability, robustness, latency).
3. Build artefacts iteratively: dataset layer, FL services, blockchain governance, monitoring dashboards.
4. Evaluate artefacts using historical replay, prospective pilots, and security analysis.
5. Communicate findings via technical reports and academic publications.

### 7.2 System Architecture Overview

1. **Edge Data Producers:** District veterinary offices, farm mobile apps, and IoT collars produce labeled samples (symptoms, movement events, sensor telemetry).
2. **ULITS Data Lake:** A privacy-preserving data fabric reconciles cattle IDs, holdings, lab tests, climate readings, and movement permits into feature stores partitioned by district.
3. **Federated Learning Layer:** Flower-based coordinators schedule training rounds; clients train MobileNetV3/Temporal Transformer hybrids for outbreak probability or risk scoring.
4. **Blockchain Governance Layer:** A Hyperledger Fabric network hosts smart contracts for BPNG-style client selection, GRNA proofs of differential privacy noise, and FLock-inspired state channels for secure aggregation incentives.
5. **Monitoring & Early Warning Layer:** A Django dashboard visualizes model metrics, drift signals, and blockchain audit trails while generating threshold-based alerts to veterinary officers.

### 7.3 Algorithmic Components

- **Verifiable Fairness & Privacy:** Integrate BPNG to derive unbiased client subsets each round; extend GRNA circuits to support convolutional gradients by chunking tensors and proving Laplace noise compliance per chunk.
- **Robust Aggregation:** Combine signSGD binarization with adaptive precision—begin with binary gradients for poisoning detection, then reintroduce higher precision for stabilized rounds. MPC protocols (ΠBootstrap, ΠHM, Πλ-Score, ΠWA) will run within state channels to minimize on-chain costs.
- **Personalization & Drift Handling:** Deploy FedBN or meta-learning layers to account for district-specific climate patterns; incorporate Kapalaga-style rainfall/temperature features as auxiliary inputs and design drift detectors using Kolmogorov-Smirnov statistics on residuals.
- **Incentive Mechanism:** Contributions measured via Hamming-distance-derived λ-scores plus utility gains on local validation sets; rewards escrowed in smart contracts and released once PMSBFT consensus finalizes aggregated updates.

### 7.4 Evaluation Strategy

- **Datasets:** Historical ULITS-enhanced dataset (2011–2024) for offline experiments; rolling 2025 pilot data for prospective validation.
- **Train/Test Splits:** Temporal splits (2011–2020 train, 2021–2022 validation, 2023–2024 test) plus district-held-out cross-validation to emulate new client onboarding.
- **Metrics:** AUC, accuracy, recall, precision, F1, ECE (calibration), convergence rounds, differential privacy ε, proof latency, blockchain transaction cost, incentive redemption rate.
- **Comparisons:** Centralized baseline, vanilla FedAvg, FedAvg + DP, blockchain-less FL, proposed blockchain-governed FL.
- **Robustness Tests:** Inject Gaussian and label-flip attacks (10–40% malicious clients) to verify poisoning tolerance; simulate bandwidth constraints and client dropouts.

### 7.5 Ethical and Regulatory Alignment

- Enforce data minimization by training solely on-device/edge nodes.
- Align with Uganda’s Data Protection and Privacy Act via ULITS consent records.
- Maintain audit-ready logs (hash pointers to raw data retained on-site) for regulators.

## 8. ULITS-Enhanced Dataset Specification

1. **Core Entities:**
   - `cattle_identity`: eartag ID, RFID tag, breed, birth date, owner ID.
   - `holding_register`: holding ID, GPS coordinates, land use, water access, veterinary district.
   - `event_log`: timestamped entries for vaccinations, clinical signs, lab submissions, movement permits, and mortality.
   - `climate_tile`: daily rainfall, maximum/minimum temperature, humidity, vegetation index aggregated to 5 km tiles (sourced from UNMA + satellite feeds).
   - `risk_context`: proximity to borders/protected areas, market density, communal grazing schedules.

2. **Label Generation:**
   - Outbreak labels derived from NADDEC confirmations; negatives defined as districts with no confirmed cases for ≥90 days.
   - Latency-adjusted labels align sensor readings with outbreak confirmation windows to prevent leakage.

3. **Feature Engineering:**
   - Rolling climate z-scores, cumulative vaccination coverage, animal movement entropy, and grazing overlap indices.
   - District-level federated summary statistics (mean residual risk per week) for personalization layers.

4. **Data Quality & Provenance:**
   - Every ingest record bound to ULITS transaction hashes, enabling forward/backward traceability.
   - Schema validation, deduplication (cattle ID + timestamp collisions), anomaly detection (e.g., improbable movements).

5. **Privacy Controls:**
   - Personally identifiable owner data remains encrypted at source; only hashed identifiers leave district nodes.
   - Dataset released internally as feature tensors plus metadata dictionaries, ensuring reproducibility without leaking raw owner info.

6. **Scale Expectations:**
   - 2.3 million registered cattle, ~180,000 event_log entries per year, 50 districts participating, climate tiles updated daily.
   - Storage footprint: ~1.5 TB raw, ~400 GB curated feature store, sharded by district for federated access.

## 9. Workflow Description for Future Diagram

1. **Data Capture:** Farmers and inspectors submit events via mobile apps or offline forms synchronized to district ULITS nodes; IoT collars stream telemetry to edge gateways.
2. **Data Harmonization:** District ETL jobs clean, validate, and join events with climate tiles and movement permits, emitting feature tensors tagged with cattle and holding IDs.
3. **Client Preparation:** District FL clients fetch the latest global model snapshot, materialize local mini-batches, and checkpoint local validation splits.
4. **Training & Proof Generation:** Clients run local epochs, add GRNA-certified differential privacy noise to gradients, and publish zk-SNARK proofs plus encrypted gradient shares to the state channel.
5. **Secure Aggregation:** Aggregator committees execute FLock-style MPC to compute robust weighted gradients, backed by verifiable random selection (BPNG) and λ-score weighting.
6. **Blockchain Commit & Incentives:** The aggregated update hash, proof metadata, and contribution scores are committed to Hyperledger Fabric; smart contracts release incentives proportional to verified contributions.
7. **Model Deployment & Monitoring:** Updated global models propagate to clients; drift monitors compare incoming telemetry distributions to historical norms and raise alerts when risk thresholds exceed configurable bounds.
8. **Early Warning Dissemination:** Alerts, explanatory drivers (e.g., rainfall anomalies, movement spikes), and audit trails are pushed to veterinary dashboards and optionally to SMS/email channels for rapid intervention.

## 10. Expected Scientific Contributions

- **Reference Architecture:** A reproducible blueprint for merging national traceability systems with blockchain-governed FL, generalizable to other commodities or public health contexts.
- **Verifiable Privacy & Fairness Toolkit:** Extended BPNG/GRNA circuits and smart contracts capable of supporting convolutional models and mixed-precision updates.
- **Robust Aggregation Insights:** Empirical evidence on how FLock-style MPC scales when fused with ULITS-sized feature spaces and incentive-compatible participation.
- **Dataset Advancement:** A rigorously documented ULITS-enhanced dataset with climate-aware features and outbreak labels suitable for benchmarking drift-aware FL algorithms.
- **Evaluation Protocol:** Multi-metric, regulator-aligned reporting that addresses the gaps highlighted by the healthcare FL review, accelerating translation to operational deployments.

## 11. References

- Kapalaga, G., et al. (2024). *A unified Foot and Mouth Disease dataset for Uganda: evaluating machine learning predictive performance degradation under varying distributions.* Frontiers in Artificial Intelligence.
- Zhang, Y., et al. (2023). *Blockchain-Based Practical and Privacy-Preserving Federated Learning with Verifiable Fairness.* Mathematics.
- Teo, Z. L., et al. (2024). *Federated machine learning in healthcare: A systematic review on clinical applications and technical architecture.* Cell Reports Medicine.
- Chen, R., et al. (2024). *FLock: Robust and Privacy-Preserving Federated Learning based on Practical Blockchain State Channels.* Preprint.
