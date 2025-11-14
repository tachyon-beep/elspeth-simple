---
name: axiom-cloud-infrastructure
description: Systematic cloud infrastructure patterns for Docker, Kubernetes, Terraform, AWS/GCP/Azure, CI/CD, monitoring, and security - emphasizes reproducibility, security-first, and observability
---

# Axiom Cloud Infrastructure

## Philosophy

Infrastructure following self-evident principles:
- **Immutable**: Infrastructure as Code, version controlled
- **Secure by default**: Security is NOT optional
- **Observable first**: Instrument BEFORE deploy
- **Reproducible**: Same input → same output
- **Fail-safe**: Explicit overrides for dangerous operations

## IRON LAWS - No Exceptions

**These skills enforce critical practices. You MUST follow them. No shortcuts under pressure.**

1. **managing-infrastructure-as-code** - ALWAYS `terraform plan` before `apply`
2. **securing-cloud-infrastructure** - Security is NOT optional. ALL deployments MUST pass security checklist.
3. **implementing-observability** - Instrument BEFORE deploying to production

**Violating these under pressure (production down, CEO asking, time pressure) is still violation.**

Common rationalizations that are WRONG:
- ❌ "It's an emergency" → IRON LAWS exist FOR emergencies
- ❌ "It passed staging" → Staging ≠ production
- ❌ "I'll add monitoring after it's up" → Deploying blind is how outages get worse
- ❌ "Quick security skim is enough" → Security requires full checklist

---

## Skills by Category

### Containerization & Orchestration
- **containerizing-applications** [TECHNIQUE] - Docker multi-stage builds, security hardening
- **orchestrating-with-kubernetes** [TECHNIQUE] - K8s deployment patterns, troubleshooting

### Infrastructure as Code
- **managing-infrastructure-as-code** [DISCIPLINE] - Terraform plan-apply-verify cycle ⚠️ IRON LAW

### Cloud Providers
- **deploying-to-aws** [REFERENCE] - AWS service patterns, IAM, VPC
- **deploying-to-gcp** [REFERENCE] - GCP service patterns, IAM bindings
- **deploying-to-azure** [REFERENCE] - Azure service patterns, RBAC

### Automation & Operations
- **building-deployment-pipelines** [TECHNIQUE] - GitHub Actions, GitLab CI, Jenkins
- **implementing-observability** [DISCIPLINE] - Metrics, logs, traces ⚠️ IRON LAW
- **troubleshooting-infrastructure** [TECHNIQUE] - Systematic debugging workflows

### Production Readiness
- **securing-cloud-infrastructure** [DISCIPLINE] - Security-first patterns ⚠️ IRON LAW
- **designing-for-resilience** [PATTERN] - HA/DR patterns, failure analysis
- **optimizing-cloud-costs** [TECHNIQUE] - Cost analysis and optimization

### Skill Types Explained
- **[DISCIPLINE]** - MUST follow, no exceptions. Has iron laws and rationalization tables.
- **[TECHNIQUE]** - How-to guides with workflows. Apply systematically.
- **[REFERENCE]** - Look up as needed. Has quick reference tables.
- **[PATTERN]** - Mental models for thinking about problems.

---

## Quick Start Workflows

### Deploying a New Application

**Time: 4-8 hours for first production deploy**

1. **containerizing-applications** (1-2h)
   - Build optimized Docker image
   - Security scanning
   - Push to registry

2. **securing-cloud-infrastructure** (30min-1h) ⚠️ REQUIRED
   - Security checklist BEFORE deploying
   - Encryption, least privilege, network segmentation
   - NO EXCEPTIONS even under time pressure

3. **implementing-observability** (1-2h) ⚠️ REQUIRED
   - Add metrics, logs, traces BEFORE deploy
   - Health checks for K8s probes
   - Alerting setup
   - NO deploying blind

4. **orchestrating-with-kubernetes** (1-2h)
   - Deployment, Service, ConfigMap, Secret manifests
   - Resource limits, health probes, autoscaling
   - NetworkPolicy, Pod Security

5. **building-deployment-pipelines** (2-4h)
   - Automate: build → test → scan → deploy
   - Secrets management in CI
   - Rollback procedures

**Prerequisites:** Kubernetes cluster exists (use deploying-to-{aws|gcp|azure} if needed)

---

### Emergency Infrastructure Fix

**When: Production down, extreme pressure, need fix NOW**

**Time: Follow 10-minute rule - invest 10 minutes in skills to prevent 60 minutes of debugging**

1. **troubleshooting-infrastructure** (5min)
   - Systematic debugging workflow
   - Symptoms → hypothesis → test → fix → verify
   - Use observability data

2. **managing-infrastructure-as-code** (3min - EMERGENCY CHECKLIST) ⚠️ REQUIRED
   - terraform plan (ALWAYS, even in emergency)
   - State backup
   - Rollback procedure ready
   - ❌ "Too urgent to plan" → Plan prevents cascading failures

3. **securing-cloud-infrastructure** (2min - EMERGENCY CHECKLIST) ⚠️ REQUIRED
   - Quick security verify (encryption, access controls, network)
   - ❌ "I'll fix security after it's up" → Security holes under pressure cause bigger outages
   - Use emergency checklist in skill

4. **implementing-observability** (IMMEDIATELY AFTER FIX - 10min)
   - Verify monitoring shows fix worked
   - Add alerts to prevent recurrence
   - ❌ "Can add monitoring later" → You're deploying blind

5. **deploying-to-{aws|gcp|azure}** (2min)
   - Cloud-specific gotchas
   - Quick reference for service you're deploying

**TOTAL TIME INVESTMENT: 10-12 minutes to prevent common disaster scenarios**

**Post-incident (within 24h):**
- **designing-for-resilience** - Why didn't we have failover? How do we prevent this?
- **building-deployment-pipelines** - How do we automate faster response next time?

---

### Setting Up New Infrastructure

**Time: 1-2 days for production-ready infrastructure**

1. **managing-infrastructure-as-code** (4-6h) ⚠️ DISCIPLINE
   - Write Terraform configurations
   - Module structure, variable management
   - Remote state setup
   - ALWAYS plan before apply

2. **securing-cloud-infrastructure** (2-4h) ⚠️ DISCIPLINE
   - Security by default in IaC
   - Least privilege IAM/RBAC
   - Encryption at rest and in transit
   - Network segmentation
   - Security checklist MUST pass

3. **designing-for-resilience** (2-4h)
   - Multi-AZ/multi-region design
   - Health checks, auto-recovery
   - Backup/restore procedures
   - Failure mode analysis

4. **deploying-to-{aws|gcp|azure}** (4-6h)
   - Cloud-specific patterns
   - Service selection guide
   - VPC/VNet design
   - Choose ONE: aws, gcp, or azure

5. **implementing-observability** (2-4h) ⚠️ DISCIPLINE
   - Infrastructure monitoring
   - Logging aggregation
   - Alerting on infrastructure health
   - Set up BEFORE deploying workloads

**Prerequisites:** Cloud account, access credentials, network design

---

## Skill Relationships

### Prerequisites
- **orchestrating-with-kubernetes** requires **containerizing-applications**
- **building-deployment-pipelines** requires **containerizing-applications**
- All cloud deployment requires **managing-infrastructure-as-code**

### Strongly Recommended Together
- **orchestrating-with-kubernetes** + **implementing-observability** + **securing-cloud-infrastructure**
- **managing-infrastructure-as-code** + **securing-cloud-infrastructure**
- **troubleshooting-infrastructure** + **implementing-observability**

### Cloud Provider - Choose One
- **deploying-to-aws** OR **deploying-to-gcp** OR **deploying-to-azure**
- Don't read all three unless multi-cloud deployment

---

## Finding the Right Skill

### "I need to..."

**...containerize an application**
→ containerizing-applications

**...deploy to Kubernetes**
→ orchestrating-with-kubernetes (requires containerizing-applications first)

**...provision infrastructure with Terraform**
→ managing-infrastructure-as-code ⚠️

**...work with AWS/GCP/Azure resources**
→ deploying-to-{aws|gcp|azure} (choose your cloud)

**...set up CI/CD**
→ building-deployment-pipelines

**...add monitoring/logging/tracing**
→ implementing-observability ⚠️

**...secure my infrastructure**
→ securing-cloud-infrastructure ⚠️

**...debug infrastructure problems**
→ troubleshooting-infrastructure

**...design for high availability**
→ designing-for-resilience

**...reduce cloud costs**
→ optimizing-cloud-costs

### "I'm getting error..."

**..."CrashLoopBackOff", "ImagePullBackOff", "pod pending"**
→ orchestrating-with-kubernetes

**..."state lock", "drift detected", "resource already exists"**
→ managing-infrastructure-as-code

**..."Access Denied", "Insufficient permissions" (AWS)**
→ deploying-to-aws

**..."Permission denied", "Required IAM permission" (GCP)**
→ deploying-to-gcp

**..."Authorization failed", "Insufficient privileges" (Azure)**
→ deploying-to-azure

**..."connection timeout", "503 service unavailable"**
→ troubleshooting-infrastructure

**..."vulnerability CVE-", "security scan failed"**
→ securing-cloud-infrastructure

---

## Time Estimates

**Quick reference (5-10 minutes):**
- All [REFERENCE] skills have quick lookup tables
- All [DISCIPLINE] skills have emergency checklists

**Full workflow (1-4 hours):**
- [TECHNIQUE] skills
- [PATTERN] skills

**Deep dive (4-8 hours):**
- Learning cloud platform from scratch (deploying-to-*)
- Setting up comprehensive infrastructure

---

## Red Flags - STOP and Consult Skills

If you're about to:
- Run `terraform apply` without reviewing plan → managing-infrastructure-as-code
- Deploy without security review → securing-cloud-infrastructure
- Deploy without monitoring → implementing-observability
- Skip steps because "it's an emergency" → Check IRON LAWS above
- Expose database publicly "temporarily" → securing-cloud-infrastructure
- Deploy without health checks → orchestrating-with-kubernetes
- Commit secrets to git → securing-cloud-infrastructure + building-deployment-pipelines

**All of these lead to bigger problems than the one you're trying to solve.**
