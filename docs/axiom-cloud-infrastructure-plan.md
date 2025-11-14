# Axiom Cloud Infrastructure Skill Pack - Detailed Implementation Plan

## Pack Overview

**Name:** axiom-cloud-infrastructure
**Category:** infrastructure
**Total Skills:** 12
**Philosophy:** Systematic, rigorous approach to cloud infrastructure aligned with Axiom principles (self-evident truths, foundational best practices)

**Core Principles:**
- Infrastructure as Code (immutable, versioned)
- Defense in depth (security at every layer)
- Observability first (instrument before deploy)
- Fail-safe defaults (secure by default, explicit overrides)
- Reproducibility (same input → same output)
- Progressive validation (validate early, validate often)

---

## Skill Pack Structure

```
.claude/skills/
├── axiom-cloud-infrastructure/
│   ├── PACK.md                                    # Pack overview and navigation
│   ├── containerizing-applications/
│   │   ├── SKILL.md
│   │   ├── dockerfile-patterns.md                 # Multi-stage, security patterns
│   │   └── compose-examples.yml
│   ├── orchestrating-with-kubernetes/
│   │   ├── SKILL.md
│   │   ├── deployment-patterns.md                 # Common workload patterns
│   │   └── troubleshooting-guide.md
│   ├── managing-infrastructure-as-code/
│   │   ├── SKILL.md
│   │   ├── terraform-workflows.md                 # Plan-apply-verify cycle
│   │   └── state-management.md
│   ├── deploying-to-aws/
│   │   ├── SKILL.md
│   │   └── aws-reference.md                       # IAM, VPC, EC2, EKS patterns
│   ├── deploying-to-gcp/
│   │   ├── SKILL.md
│   │   └── gcp-reference.md                       # IAM, VPC, GCE, GKE patterns
│   ├── deploying-to-azure/
│   │   ├── SKILL.md
│   │   └── azure-reference.md                     # RBAC, VNet, VM, AKS patterns
│   ├── building-deployment-pipelines/
│   │   ├── SKILL.md
│   │   ├── github-actions-patterns.yml
│   │   ├── gitlab-ci-patterns.yml
│   │   └── jenkins-patterns.groovy
│   ├── implementing-observability/
│   │   ├── SKILL.md
│   │   ├── metrics-patterns.md                    # Prometheus, CloudWatch, etc.
│   │   ├── logging-patterns.md                    # Structured logging
│   │   └── tracing-patterns.md                    # Distributed tracing
│   ├── securing-cloud-infrastructure/
│   │   ├── SKILL.md
│   │   ├── security-checklist.md                  # Pre-deployment security
│   │   └── secrets-management.md                  # Vault, KMS, etc.
│   ├── designing-for-resilience/
│   │   ├── SKILL.md
│   │   └── ha-dr-patterns.md                      # High availability, disaster recovery
│   ├── troubleshooting-infrastructure/
│   │   ├── SKILL.md
│   │   └── debugging-workflows.md                 # Systematic infrastructure debugging
│   └── optimizing-cloud-costs/
│       ├── SKILL.md
│       └── cost-analysis-patterns.md              # Right-sizing, reserved instances
```

---

## Individual Skill Specifications

### 1. containerizing-applications

**Type:** Technique
**Name:** containerizing-applications
**Description:** Use when building Docker images, writing Dockerfiles, or containerizing existing applications - provides systematic multi-stage build patterns, security hardening, and optimization techniques for production containers

**When to Use:**
- Creating new Dockerfiles
- Optimizing existing container images
- Reducing image size or attack surface
- Implementing security scanning in container builds
- Errors: "layer too large", "vulnerability CVE-", "container failed security scan"

**Core Content:**
- Multi-stage build pattern (build → test → production)
- Base image selection (distroless, alpine, scratch)
- Security hardening (non-root user, minimal packages, read-only filesystem)
- Build optimization (.dockerignore, layer caching)
- Health checks and signals
- Quick reference table of common Dockerfile commands

**Reference Files:**
- `dockerfile-patterns.md` - Comprehensive patterns for different languages/frameworks
- `compose-examples.yml` - Docker Compose multi-service patterns

**Cross-References:**
- **REQUIRED:** building-deployment-pipelines (for CI integration)
- **OPTIONAL:** securing-cloud-infrastructure (for image scanning)

**Testing Approach:**
- Application scenario: "Containerize this Python Flask app with security scanning"
- Variation: "Optimize this Dockerfile - it's 2GB"
- Gap test: Can agent find multi-stage pattern without prompting?

---

### 2. orchestrating-with-kubernetes

**Type:** Technique
**Name:** orchestrating-with-kubernetes
**Description:** Use when deploying to Kubernetes, writing manifests, or troubleshooting cluster issues - provides systematic deployment patterns, resource management, and debugging workflows for reliable K8s operations

**When to Use:**
- Creating Deployment, Service, ConfigMap, Secret manifests
- Debugging pod crashes, CrashLoopBackOff, ImagePullBackOff
- Implementing health checks, resource limits, autoscaling
- Errors: "pod pending", "insufficient resources", "readiness probe failed"

**Core Content:**
- Deployment pattern (replica sets, rolling updates, rollbacks)
- Service types (ClusterIP, NodePort, LoadBalancer, Ingress)
- ConfigMap/Secret patterns (separation of config from code)
- Resource requests/limits (CPU, memory, right-sizing)
- Health probes (liveness, readiness, startup)
- Troubleshooting workflow (logs → describe → events → exec)

**Reference Files:**
- `deployment-patterns.md` - Common workload types (stateless, stateful, batch, cron)
- `troubleshooting-guide.md` - Decision tree for debugging K8s issues

**Cross-References:**
- **REQUIRED:** containerizing-applications (containers first)
- **REQUIRED:** implementing-observability (metrics, logs)
- **OPTIONAL:** designing-for-resilience (HA patterns)

**Testing Approach:**
- Application: "Deploy this containerized app to K8s with autoscaling"
- Pressure: "The pod is CrashLoopBackOff - debug it"
- Gap test: Do they check resource limits? Set health probes?

---

### 3. managing-infrastructure-as-code

**Type:** Technique
**Name:** managing-infrastructure-as-code
**Description:** Use when provisioning cloud resources with Terraform or other IaC tools - enforces plan-apply-verify cycle, state management, and systematic change workflows to prevent infrastructure drift and accidental deletions

**When to Use:**
- Creating or modifying Terraform configurations
- Managing cloud resources (VPCs, VMs, databases, load balancers)
- Before running `terraform apply`
- Errors: "state lock", "resource already exists", "drift detected"

**Core Content:**
- **IRON LAW:** ALWAYS run `terraform plan` before `apply`. No exceptions.
- State management (remote state, locking, workspaces)
- Module patterns (reusable, composable)
- Variable management (tfvars, secrets, validation)
- Import existing resources
- Destroy safety checks
- Rationalization table: "It's a small change" → Plan shows cascading deletes

**Reference Files:**
- `terraform-workflows.md` - Step-by-step workflows for common operations
- `state-management.md` - Remote state, locking, migration patterns

**Cross-References:**
- **REQUIRED:** writing-skills (this is a discipline-enforcing skill)
- **REQUIRED:** securing-cloud-infrastructure (IAM, network security)
- **OPTIONAL:** All deploying-to-* skills (cloud-specific patterns)

**Testing Approach:**
- Discipline test: "Quick, add this S3 bucket to production"
- Pressure test: Time constraint + "just apply it"
- Look for: Do they skip plan? Do they review plan output?

**Skill Type:** Discipline-enforcing (like TDD) - uses authority + commitment principles

---

### 4. deploying-to-aws

**Type:** Reference
**Name:** deploying-to-aws
**Description:** Use when provisioning AWS resources, configuring IAM policies, or troubleshooting AWS deployments - provides AWS-specific patterns, service selection guidance, and common gotchas for reliable cloud operations

**When to Use:**
- Working with AWS services (EC2, ECS, EKS, RDS, S3, Lambda)
- IAM policy troubleshooting ("Access Denied", "Insufficient permissions")
- VPC networking (subnets, security groups, routing)
- Cost optimization on AWS

**Core Content:**
- Service selection guide (when to use EC2 vs ECS vs EKS vs Lambda)
- IAM least-privilege patterns
- VPC design patterns (public/private subnets, NAT gateways)
- Common errors and solutions
- Quick reference: AWS CLI common commands

**Reference Files:**
- `aws-reference.md` - Comprehensive AWS service patterns
  - Compute: EC2, ECS, EKS, Lambda
  - Storage: S3, EBS, EFS
  - Database: RDS, DynamoDB, Aurora
  - Networking: VPC, ALB, CloudFront
  - Security: IAM, Secrets Manager, KMS

**Cross-References:**
- **REQUIRED:** managing-infrastructure-as-code (provision with Terraform)
- **REQUIRED:** securing-cloud-infrastructure (IAM, encryption)
- **OPTIONAL:** orchestrating-with-kubernetes (EKS patterns)

**Testing Approach:**
- Retrieval: "How do I create a private EKS cluster?"
- Application: "Set up an RDS database accessible only from private subnet"
- Gap test: Are IAM patterns clear? VPC patterns complete?

---

### 5. deploying-to-gcp

**Type:** Reference
**Name:** deploying-to-gcp
**Description:** Use when provisioning GCP resources, configuring IAM bindings, or troubleshooting GCP deployments - provides GCP-specific patterns, service selection guidance, and common gotchas for reliable cloud operations

**When to Use:**
- Working with GCP services (GCE, GKE, Cloud Run, Cloud SQL)
- IAM binding troubleshooting ("Permission denied", "Required IAM permission")
- VPC networking (subnets, firewall rules, Cloud NAT)
- Cost optimization on GCP

**Core Content:**
- Service selection guide (when to use GCE vs GKE vs Cloud Run vs Cloud Functions)
- IAM role binding patterns (service accounts, workload identity)
- VPC design patterns (shared VPC, private Google access)
- Common errors and solutions
- Quick reference: gcloud CLI common commands

**Reference Files:**
- `gcp-reference.md` - Comprehensive GCP service patterns (parallel to AWS)

**Cross-References:**
- **REQUIRED:** managing-infrastructure-as-code
- **REQUIRED:** securing-cloud-infrastructure
- **OPTIONAL:** orchestrating-with-kubernetes (GKE patterns)

**Testing Approach:**
- Same as deploying-to-aws but GCP-specific

---

### 6. deploying-to-azure

**Type:** Reference
**Name:** deploying-to-azure
**Description:** Use when provisioning Azure resources, configuring RBAC, or troubleshooting Azure deployments - provides Azure-specific patterns, service selection guidance, and common gotchas for reliable cloud operations

**When to Use:**
- Working with Azure services (VMs, AKS, Azure Functions, SQL Database)
- RBAC troubleshooting ("Authorization failed", "Insufficient privileges")
- VNet networking (subnets, NSGs, Azure Firewall)
- Cost optimization on Azure

**Core Content:**
- Service selection guide (when to use VMs vs AKS vs Container Instances vs Functions)
- RBAC patterns (managed identities, service principals)
- VNet design patterns (hub-spoke, private endpoints)
- Common errors and solutions
- Quick reference: az CLI common commands

**Reference Files:**
- `azure-reference.md` - Comprehensive Azure service patterns

**Cross-References:**
- **REQUIRED:** managing-infrastructure-as-code
- **REQUIRED:** securing-cloud-infrastructure
- **OPTIONAL:** orchestrating-with-kubernetes (AKS patterns)

**Testing Approach:**
- Same as deploying-to-aws but Azure-specific

---

### 7. building-deployment-pipelines

**Type:** Technique
**Name:** building-deployment-pipelines
**Description:** Use when creating CI/CD pipelines, automating deployments, or debugging pipeline failures - provides systematic patterns for reliable, secure, and fast deployment automation across GitHub Actions, GitLab CI, and Jenkins

**When to Use:**
- Setting up automated builds and deployments
- Implementing testing in CI
- Deploying containers or infrastructure
- Debugging pipeline failures ("build failed", "test timeout", "deployment hung")

**Core Content:**
- Pipeline stages pattern (build → test → security scan → deploy)
- Secrets management in CI (never commit secrets)
- Caching strategies (dependencies, Docker layers)
- Deployment strategies (blue-green, canary, rolling)
- Rollback procedures
- Common mistakes: deploying on test failure, skipping security scans

**Reference Files:**
- `github-actions-patterns.yml` - Working GitHub Actions examples
- `gitlab-ci-patterns.yml` - Working GitLab CI examples
- `jenkins-patterns.groovy` - Working Jenkinsfile examples

**Cross-References:**
- **REQUIRED:** containerizing-applications (build containers in CI)
- **REQUIRED:** securing-cloud-infrastructure (security scanning)
- **OPTIONAL:** managing-infrastructure-as-code (deploy infra from CI)

**Testing Approach:**
- Application: "Set up CI/CD for this app with security scanning"
- Variation: "Pipeline is slow - optimize it"
- Gap test: Do they cache dependencies? Run security scans?

---

### 8. implementing-observability

**Type:** Technique
**Name:** implementing-observability
**Description:** Use when instrumenting applications, setting up monitoring, or debugging production issues - enforces observability-first approach with metrics, structured logging, and distributed tracing for reliable production operations

**When to Use:**
- Setting up monitoring and alerting
- Debugging production performance issues
- Implementing SLOs/SLIs
- Troubleshooting distributed systems
- Errors: "can't find the issue in production", "no visibility into service health"

**Core Content:**
- **IRON LAW:** Instrument BEFORE deploying to production. No exceptions.
- Three pillars: Metrics, Logs, Traces
- Metrics patterns (RED: Rate, Errors, Duration; USE: Utilization, Saturation, Errors)
- Structured logging (JSON logs with correlation IDs)
- Distributed tracing (propagate trace context)
- Alerting best practices (actionable, low false-positive)
- Quick reference: Common metrics to track by service type

**Reference Files:**
- `metrics-patterns.md` - Prometheus, CloudWatch, Datadog patterns
- `logging-patterns.md` - Structured logging examples (Python, Node.js, Go)
- `tracing-patterns.md` - OpenTelemetry, Jaeger patterns

**Cross-References:**
- **REQUIRED:** orchestrating-with-kubernetes (K8s metrics, logs)
- **REQUIRED:** troubleshooting-infrastructure (use observability for debugging)
- **OPTIONAL:** All deploying-to-* skills (cloud-specific monitoring)

**Testing Approach:**
- Discipline: "Deploy this app to production"
- Look for: Do they add metrics/logging before deploying?
- Pressure: Time constraint - do they skip instrumentation?

**Skill Type:** Discipline-enforcing

---

### 9. securing-cloud-infrastructure

**Type:** Technique
**Name:** securing-cloud-infrastructure
**Description:** Use when deploying infrastructure, configuring access controls, or reviewing security posture - enforces security-first patterns including least privilege, encryption at rest/in transit, network segmentation, and secrets management to prevent breaches and data loss

**When to Use:**
- Before deploying any infrastructure
- Reviewing IAM policies, security groups, firewall rules
- Managing secrets, API keys, credentials
- Security audit or compliance review
- Errors: "security group too permissive", "unencrypted data", "exposed secrets"

**Core Content:**
- **IRON LAW:** Security is NOT optional. All deployments MUST pass security checklist.
- Least privilege principle (IAM, RBAC)
- Defense in depth (multiple security layers)
- Encryption at rest and in transit (always)
- Network segmentation (private subnets, security groups)
- Secrets management (never commit, use KMS/Vault)
- Security scanning (containers, dependencies, infrastructure)
- Rationalization table: "It's just a test environment" → Test breaches happen

**Reference Files:**
- `security-checklist.md` - Pre-deployment security verification (checklist format)
- `secrets-management.md` - Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault

**Cross-References:**
- **REQUIRED:** All deploying-to-* skills (cloud-specific security)
- **REQUIRED:** managing-infrastructure-as-code (secure by default configs)
- **REQUIRED:** containerizing-applications (container security scanning)

**Testing Approach:**
- Discipline: "Quick, deploy this database"
- Look for: Do they create in private subnet? Enable encryption? Restrict access?
- Pressure: Production down - do they skip security for speed?

**Skill Type:** Discipline-enforcing

---

### 10. designing-for-resilience

**Type:** Pattern
**Name:** designing-for-resilience
**Description:** Use when architecting systems for high availability, designing disaster recovery, or preventing single points of failure - provides systematic patterns for resilient architectures that gracefully handle failures and recover automatically

**When to Use:**
- Designing production systems
- Implementing HA/DR requirements
- Reviewing architecture for failure scenarios
- Troubleshooting availability issues
- Requirements: "99.9% uptime", "zero downtime deployments", "disaster recovery"

**Core Content:**
- Failure modes and effects analysis (FMEA)
- Redundancy patterns (multi-AZ, multi-region)
- Health checks and auto-recovery
- Graceful degradation
- Circuit breakers and retry patterns
- Backup and restore procedures
- Testing failure scenarios (chaos engineering)
- Decision flowchart: When to use which HA pattern

**Reference Files:**
- `ha-dr-patterns.md` - High availability and disaster recovery patterns
  - Database HA (replication, failover)
  - Application HA (load balancing, autoscaling)
  - Multi-region patterns
  - RTO/RPO calculations
  - Backup strategies

**Cross-References:**
- **REQUIRED:** orchestrating-with-kubernetes (replica sets, pod disruption budgets)
- **OPTIONAL:** All deploying-to-* skills (cloud-specific HA features)
- **OPTIONAL:** implementing-observability (monitor health)

**Testing Approach:**
- Recognition: "This architecture has a single point of failure - where?"
- Application: "Design a highly available database setup"
- Counter-example: "Do we need HA for this internal tool?" (know when not to apply)

---

### 11. troubleshooting-infrastructure

**Type:** Technique
**Name:** troubleshooting-infrastructure
**Description:** Use when debugging failed deployments, investigating outages, or resolving infrastructure issues - provides systematic root-cause analysis workflows to efficiently diagnose and fix cloud infrastructure problems

**When to Use:**
- Deployment failed or degraded
- Service outage or performance degradation
- Resource exhaustion (CPU, memory, disk, network)
- Connectivity issues
- Errors: "connection timeout", "503 service unavailable", "out of memory"

**Core Content:**
- Systematic debugging workflow (symptoms → hypothesis → test → fix → verify)
- Common failure patterns and solutions
- Tool selection by problem type
- Information gathering checklist (logs, metrics, events, config)
- Escalation criteria (when to involve others)
- Decision flowchart: Network vs application vs infrastructure issue?

**Reference Files:**
- `debugging-workflows.md` - Step-by-step troubleshooting for common scenarios
  - Container won't start
  - Pod CrashLoopBackOff
  - Network connectivity issues
  - Performance degradation
  - Resource exhaustion

**Cross-References:**
- **REQUIRED:** implementing-observability (use metrics/logs for debugging)
- **OPTIONAL:** orchestrating-with-kubernetes (K8s-specific troubleshooting)
- **OPTIONAL:** All deploying-to-* skills (cloud-specific debugging tools)

**Testing Approach:**
- Application: "This deployment is failing with 'ImagePullBackOff' - fix it"
- Variation: "API is slow - find the bottleneck"
- Gap test: Do they follow systematic approach? Check logs first?

**Note:** May cross-reference superpowers:root-cause-tracing if that skill exists

---

### 12. optimizing-cloud-costs

**Type:** Technique
**Name:** optimizing-cloud-costs
**Description:** Use when cloud costs are high, budgets are tight, or implementing cost controls - provides systematic analysis and optimization patterns to reduce cloud spending without sacrificing reliability or performance

**When to Use:**
- Cloud bill is higher than expected
- Implementing cost budgets or alerts
- Right-sizing resources
- Choosing pricing models (on-demand, reserved, spot)
- Before deploying large-scale infrastructure

**Core Content:**
- Cost analysis workflow (measure → identify waste → optimize → verify savings)
- Common waste patterns (idle resources, oversized instances, inefficient storage)
- Right-sizing methodology (CPU/memory utilization → resize)
- Pricing model selection (reserved instances, savings plans, spot instances)
- Cost allocation tags
- Budget alerts and controls
- Quick reference: Cost optimization by service type

**Reference Files:**
- `cost-analysis-patterns.md` - Cloud-specific cost optimization
  - Compute optimization (instance types, autoscaling)
  - Storage optimization (lifecycle policies, tiering)
  - Network optimization (data transfer, NAT gateways)
  - Database optimization (instance sizing, read replicas)

**Cross-References:**
- **REQUIRED:** implementing-observability (use metrics for right-sizing)
- **OPTIONAL:** All deploying-to-* skills (cloud-specific cost tools)

**Testing Approach:**
- Application: "Our AWS bill jumped 50% this month - investigate"
- Variation: "Right-size these EC2 instances"
- Gap test: Do they check utilization before resizing?

---

## Pack-Level Features

### PACK.md (Navigation and Overview)

```markdown
---
name: axiom-cloud-infrastructure
description: Systematic cloud infrastructure patterns for Docker, Kubernetes, Terraform, AWS/GCP/Azure, CI/CD, monitoring, and security - emphasizes reproducibility, security-first, and observability
---

# Axiom Cloud Infrastructure

## Philosophy

Infrastructure following self-evident principles:
- **Immutable**: Infrastructure as Code, version controlled
- **Secure by default**: Security is not optional
- **Observable first**: Instrument before deploy
- **Reproducible**: Same input → same output
- **Fail-safe**: Explicit overrides for dangerous operations

## Skills by Category

### Containerization & Orchestration
- **containerizing-applications**: Docker patterns
- **orchestrating-with-kubernetes**: K8s deployment patterns

### Infrastructure as Code
- **managing-infrastructure-as-code**: Terraform workflows

### Cloud Providers
- **deploying-to-aws**: AWS-specific patterns
- **deploying-to-gcp**: GCP-specific patterns
- **deploying-to-azure**: Azure-specific patterns

### Automation & Operations
- **building-deployment-pipelines**: CI/CD patterns
- **implementing-observability**: Metrics, logs, traces
- **troubleshooting-infrastructure**: Systematic debugging

### Production Readiness
- **securing-cloud-infrastructure**: Security-first patterns
- **designing-for-resilience**: HA/DR patterns
- **optimizing-cloud-costs**: Cost optimization

## Quick Start Workflows

### Deploying a New Application
1. containerizing-applications → build Docker image
2. securing-cloud-infrastructure → security review
3. implementing-observability → add metrics/logs
4. orchestrating-with-kubernetes → deploy to K8s
5. building-deployment-pipelines → automate deployment

### Setting Up New Infrastructure
1. managing-infrastructure-as-code → write Terraform
2. securing-cloud-infrastructure → security review
3. designing-for-resilience → HA/DR design
4. deploying-to-{aws|gcp|azure} → provision resources
5. implementing-observability → set up monitoring

### Troubleshooting Production
1. implementing-observability → check metrics/logs
2. troubleshooting-infrastructure → systematic debugging
3. orchestrating-with-kubernetes → K8s-specific tools (if applicable)
```

---

## Cross-Pack Integration

### Links to Existing Skills

If these skills exist in superpowers or other packs:

1. **test-driven-development** ← Referenced by:
   - managing-infrastructure-as-code (discipline enforcement)
   - securing-cloud-infrastructure (discipline enforcement)
   - implementing-observability (discipline enforcement)

2. **root-cause-tracing** ← Referenced by:
   - troubleshooting-infrastructure (systematic debugging)

3. **systematic-debugging** ← Referenced by:
   - troubleshooting-infrastructure (debugging methodology)

4. **verification-before-completion** ← Referenced by:
   - managing-infrastructure-as-code (verify plan before apply)
   - securing-cloud-infrastructure (verify security before deploy)

### Potential Future Skills to Create

Skills that would complement this pack:
- **monitoring-slos** - SLO/SLI/SLA patterns
- **implementing-gitops** - GitOps workflows (ArgoCD, Flux)
- **managing-service-mesh** - Istio/Linkerd patterns
- **serverless-patterns** - Lambda/Cloud Functions best practices
- **database-operations** - Database-specific patterns (migrations, backups, HA)

---

## Implementation Priority

### Phase 1: Core Foundation (First 4 skills)
1. **managing-infrastructure-as-code** (most critical, discipline-enforcing)
2. **securing-cloud-infrastructure** (critical, discipline-enforcing)
3. **containerizing-applications** (foundational)
4. **implementing-observability** (discipline-enforcing)

**Rationale:** These enforce good practices and are prerequisites for others

### Phase 2: Deployment & Operations (Next 4 skills)
5. **orchestrating-with-kubernetes** (most common orchestration)
6. **building-deployment-pipelines** (automation)
7. **troubleshooting-infrastructure** (operational necessity)
8. **deploying-to-aws** (most common cloud)

**Rationale:** Enable actual deployments and operations

### Phase 3: Multi-Cloud & Optimization (Final 4 skills)
9. **deploying-to-gcp** (second cloud)
10. **deploying-to-azure** (third cloud)
11. **designing-for-resilience** (production maturity)
12. **optimizing-cloud-costs** (cost control)

**Rationale:** Expand coverage and optimize existing deployments

---

## Testing Strategy by Skill Type

### Discipline-Enforcing Skills (4)
- managing-infrastructure-as-code
- securing-cloud-infrastructure
- implementing-observability
- (partially) building-deployment-pipelines

**Testing approach:**
- Pressure scenarios: Time constraints, "quick fix", production down
- Look for rationalizations: "It's just a test", "I'll fix it later", "Small change"
- Test with authority + commitment persuasion principles
- Build rationalization tables from failures

### Technique Skills (5)
- containerizing-applications
- orchestrating-with-kubernetes
- building-deployment-pipelines
- troubleshooting-infrastructure
- optimizing-cloud-costs

**Testing approach:**
- Application scenarios: Can they apply the technique?
- Variation scenarios: Different languages, frameworks, clouds?
- Gap testing: Are instructions complete?

### Pattern Skills (1)
- designing-for-resilience

**Testing approach:**
- Recognition: Can they identify failure points?
- Application: Can they design resilient architecture?
- Counter-examples: When NOT to over-engineer?

### Reference Skills (3)
- deploying-to-aws
- deploying-to-gcp
- deploying-to-azure

**Testing approach:**
- Retrieval: Can they find the right pattern?
- Application: Can they use what they found?
- Gap testing: Are common use cases covered?

---

## Metadata Standards

All skills in this pack follow these conventions:

**Naming:**
- Gerund form (verb-ing): containerizing, orchestrating, managing, deploying, building, implementing, securing, designing, troubleshooting, optimizing
- Hyphens only, no special characters
- Technology-specific where applicable (kubernetes, terraform, aws/gcp/azure)

**Descriptions:**
- Start with "Use when..."
- Include specific error messages, symptoms, situations
- Technology-agnostic problem description + technology-specific solution
- Third person
- Under 500 characters target

**File Organization:**
- Self-contained if <500 words
- Reference files for >100 lines (API docs, comprehensive patterns)
- Reusable tool files for scripts
- One level deep (no nested references)

**Word Count Targets:**
- SKILL.md: <500 words
- Reference files: Unlimited (loaded on-demand)
- Use progressive disclosure for heavy content

---

## Success Criteria

Each skill must meet these criteria before deployment:

**RED Phase:**
✓ Baseline test shows agents fail without skill
✓ Documented exact rationalizations/failures
✓ Identified 3+ pressure scenarios (for discipline skills)

**GREEN Phase:**
✓ Name follows conventions
✓ Description is CSO-optimized (Use when...)
✓ Content addresses baseline failures
✓ Code examples are excellent (not multi-language)
✓ Agents comply when skill is present

**REFACTOR Phase:**
✓ New rationalizations identified and countered
✓ Rationalization table complete (for discipline skills)
✓ Re-tested until bulletproof

**Quality:**
✓ Quick reference table present
✓ Common mistakes section included
✓ Supporting files properly linked
✓ Cross-references use skill names only (not @ links)

---

## Next Steps

1. **Review this plan** - Is the skill breakdown appropriate? Any gaps?
2. **Prioritize skills** - Start with Phase 1 (foundation)
3. **Follow TDD process** - RED-GREEN-REFACTOR for each skill
4. **Test systematically** - Use TodoWrite for checklist tracking
5. **Deploy incrementally** - One skill at a time, tested before moving on

**IMPORTANT:** Per writing-skills guidance, do NOT batch-create all 12 skills. Create one, test it, deploy it, then move to the next. Each skill must pass TDD cycle before proceeding.
