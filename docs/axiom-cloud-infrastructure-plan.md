# Axiom Cloud Infrastructure Skill Pack - Implementation Plan

## Overview

**Pack Name:** axiom-cloud-infrastructure
**Category:** infrastructure
**Skill Count:** 12
**Philosophy:** Systematic approach to robust, production-ready cloud systems

This skill pack provides comprehensive guidance for building, deploying, and operating cloud-native Python applications with emphasis on security, reliability, and maintainability - aligned with the elspeth-simple project's values.

## Alignment with Elspeth-Simple

The axiom-cloud-infrastructure pack directly supports elspeth-simple's production deployment:

- **Security-first**: Official-sensitive data handling requirements
- **Production-ready**: Robust deployment patterns for data processing workflows
- **Plugin architecture**: Containerization and orchestration of pluggable systems
- **Observability**: Monitoring SDA pipelines in production
- **Cost tracking**: Infrastructure cost awareness matching elspeth's token cost tracking

## Skill Dependencies and Cross-References

### Internal Cross-References (within pack)

```
containerizing-python-applications
  ↓ (builds foundation for)
multi-stage-docker-builds
  ↓ (images deployed to)
kubernetes-deployment-patterns
  ↓ (requires)
health-checks-and-readiness

infrastructure-as-code-principles
  ↓ (implemented via)
terraform-state-management
  ↓ (provisions)
cloud-provider-selection
  ↓ (secures)
secure-secrets-management

ci-cd-pipeline-design
  ↓ (includes)
automated-testing-in-pipelines
  ↓ (monitors via)
observability-stack-setup
  ↓ (responds via)
incident-response-workflows
```

### External Cross-References

These skills should reference the **writing-skills** skill:
- All skills created using TDD methodology from writing-skills
- Follow CSO (Claude Search Optimization) patterns
- Use progressive disclosure for reference material

Future integration points:
- **test-driven-development** (from superpowers) - for automated-testing-in-pipelines
- **systematic-debugging** (from superpowers) - for incident-response-workflows
- **verification-before-completion** (from superpowers) - for ci-cd-pipeline-design

## Detailed Skill Specifications

---

### 1. containerizing-python-applications

**Type:** Technique
**Skill Level:** Fundamental
**Dependencies:** None (foundational skill)

**Description:**
```yaml
name: containerizing-python-applications
description: Use when deploying Python applications to production or creating reproducible environments - provides patterns for Dockerfile creation, dependency management with uv/pip, and Python 3.13+ specific considerations for secure, minimal container images
```

**What it teaches:**
- Dockerfile structure for Python apps (especially Python 3.13+)
- Base image selection (official python, distroless, alpine trade-offs)
- Dependency management with uv (elspeth-simple's package manager)
- Security scanning and non-root users
- Environment variable handling
- Volume mounts for data processing workflows

**Why it matters for elspeth:**
- elspeth-simple needs containerization for production deployment
- Data processing workflows require consistent environments
- Official-sensitive data requires secure container practices

**Key sections:**
- Overview: Core principle of reproducible Python environments
- When to Use: Deploying Python 3.13+ apps, data pipelines, batch processors
- Quick Reference: Common Dockerfile patterns table
- Implementation: Complete Dockerfile example for elspeth-simple
- Common Mistakes: Root users, bloated images, missing .dockerignore

**Supporting files:**
- `elspeth-simple.Dockerfile` - Reference Dockerfile optimized for data processing
- `dockerignore-template` - Standard .dockerignore for Python projects

**Testing approach:**
- Application scenario: "Containerize elspeth-simple for production"
- Variation scenario: "Optimize image size while keeping dependencies"
- Gap testing: "Handle Azure SDK dependencies correctly"

---

### 2. multi-stage-docker-builds

**Type:** Pattern
**Skill Level:** Intermediate
**Dependencies:** containerizing-python-applications

**Description:**
```yaml
name: multi-stage-docker-builds
description: Use when Docker images are too large, contain build tools in production, or lack separation between build and runtime - teaches multi-stage patterns to reduce image size by 60-80% and improve security by excluding build dependencies from final images
```

**What it teaches:**
- Multi-stage build pattern
- Builder vs. runtime stages
- Copying artifacts between stages
- Cache optimization strategies
- Security benefits of minimal runtime images

**Why it matters for elspeth:**
- Data processing containers should be minimal for faster deployment
- Build tools (compilers, dev dependencies) shouldn't be in production
- Faster container startup for batch processing jobs

**Key sections:**
- Overview: Separation of build and runtime concerns
- Core Pattern: Before/after comparison showing size reduction
- Quick Reference: Common stage patterns (builder, tester, runtime)
- Implementation: Multi-stage Dockerfile for Python + C extensions
- Common Mistakes: Copying entire build context, poor layer caching

**Cross-references:**
- Builds on: containerizing-python-applications
- Related to: kubernetes-deployment-patterns (smaller images = faster pulls)

**Testing approach:**
- Recognition scenario: "When should I use multi-stage vs single-stage?"
- Application scenario: "Build elspeth-simple with test stage and minimal runtime"

---

### 3. kubernetes-deployment-patterns

**Type:** Pattern
**Skill Level:** Intermediate
**Dependencies:** containerizing-python-applications

**Description:**
```yaml
name: kubernetes-deployment-patterns
description: Use when deploying containerized applications to Kubernetes or facing pod restarts, failed rollouts, or scaling issues - provides deployment strategies (rolling, blue-green, canary), resource management, and production-ready manifest patterns
```

**What it teaches:**
- Deployment vs StatefulSet vs Job vs CronJob selection
- Resource requests/limits for Python applications
- Rolling update strategies
- ConfigMap/Secret management
- Pod disruption budgets
- HPA (Horizontal Pod Autoscaling) patterns

**Why it matters for elspeth:**
- Batch data processing maps to Kubernetes Jobs/CronJobs
- SDA suite runs could be orchestrated via K8s
- Concurrent processing benefits from proper resource limits

**Key sections:**
- Overview: K8s workload types and when to use each
- When to Use: Flowchart for selecting workload type
- Quick Reference: Manifest pattern table
- Implementation: Complete Job manifest for elspeth-simple batch processing
- Common Mistakes: Missing resource limits, improper restart policies

**Supporting files:**
- `k8s-manifests/` - Reference manifests for different workload types
  - `elspeth-job.yaml` - CronJob for scheduled SDA runs
  - `elspeth-deployment.yaml` - Long-running service variant
  - `configmap-example.yaml` - Configuration injection pattern

**Cross-references:**
- Requires: containerizing-python-applications
- Works with: health-checks-and-readiness
- Deployed via: ci-cd-pipeline-design

**Testing approach:**
- Decision scenario: "Choose workload type for scheduled data processing"
- Application scenario: "Create production-ready Job manifest with proper limits"

---

### 4. health-checks-and-readiness

**Type:** Technique
**Skill Level:** Fundamental
**Dependencies:** kubernetes-deployment-patterns

**Description:**
```yaml
name: health-checks-and-readiness
description: Use when applications fail to serve traffic after deployment, pods restart unexpectedly, or load balancers route to unhealthy instances - implements liveness, readiness, and startup probes with appropriate timeouts for Python applications
```

**What it teaches:**
- Liveness vs readiness vs startup probes
- Probe types: HTTP, TCP, exec
- Timeout and threshold configuration
- Health check endpoint design for Python
- Graceful shutdown handling (SIGTERM)
- Startup time considerations for data loading

**Why it matters for elspeth:**
- Data processing jobs need proper lifecycle management
- Checkpoint loading at startup may take time (startup probes)
- Graceful shutdown preserves processing state

**Key sections:**
- Overview: Three types of probes and their purposes
- When to Use: Symptoms table (pod restarts, traffic issues)
- Quick Reference: Probe configuration patterns
- Implementation: Flask/FastAPI health endpoints + K8s probe config
- Common Mistakes: Too-short timeouts, missing startup probes

**Supporting files:**
- `health-endpoints.py` - Reference implementation for Python health checks

**Cross-references:**
- Part of: kubernetes-deployment-patterns
- Monitored by: observability-stack-setup

**Testing approach:**
- Application scenario: "Add health checks to elspeth-simple for K8s deployment"
- Failure scenario: "Configure probes for app with slow startup (checkpoint loading)"

---

### 5. infrastructure-as-code-principles

**Type:** Pattern
**Skill Level:** Fundamental
**Dependencies:** None (foundational)

**Description:**
```yaml
name: infrastructure-as-code-principles
description: Use when manually provisioning cloud resources, facing environment drift, or lacking audit trails - establishes IaC principles of idempotency, versioning, testing, and documentation for reproducible infrastructure
```

**What it teaches:**
- IaC core principles (declarative, versioned, testable)
- Idempotency and convergence
- State management philosophy
- Module/component design
- DRY vs WET trade-offs in infrastructure
- Documentation as code

**Why it matters for elspeth:**
- Reproducible deployment environments for data processing
- Audit requirements for official-sensitive systems
- Version-controlled infrastructure changes

**Key sections:**
- Overview: Infrastructure as software engineering discipline
- When to Use: Manual provisioning, compliance requirements, team collaboration
- Core Pattern: Declarative vs imperative comparison
- Quick Reference: IaC best practices table
- Implementation: High-level patterns (no tool-specific code yet)
- Common Mistakes: Hardcoded values, no state management, manual changes

**Cross-references:**
- Implemented by: terraform-state-management
- Applied to: cloud-provider-selection

**Testing approach:**
- Recognition scenario: "Identify IaC principle violations in example"
- Application scenario: "Design infrastructure module structure"

---

### 6. terraform-state-management

**Type:** Technique
**Skill Level:** Intermediate
**Dependencies:** infrastructure-as-code-principles

**Description:**
```yaml
name: terraform-state-management
description: Use when experiencing Terraform state conflicts, lost state files, or team collaboration issues - covers remote state backends (S3, Azure Blob, GCS), state locking, sensitive data handling, and state migration strategies
```

**What it teaches:**
- State file purpose and structure
- Remote backend configuration (S3, Azure Storage, GCS)
- State locking with DynamoDB/Azure/GCS
- Sensitive data in state (secrets, credentials)
- State import/migration
- Workspace strategies
- Disaster recovery (state backup/restore)

**Why it matters for elspeth:**
- Production infrastructure requires team collaboration
- State contains sensitive configuration (API keys, endpoints)
- Automated deployments need reliable state locking

**Key sections:**
- Overview: State as source of truth
- When to Use: Multi-person teams, production environments, CI/CD
- Quick Reference: Backend configuration table
- Implementation: Complete backend configs for AWS/Azure/GCP
- Common Mistakes: Local state in production, no locking, committing state files

**Supporting files:**
- `terraform-backends/` - Reference backend configurations
  - `s3-backend.tf` - AWS S3 + DynamoDB locking
  - `azure-backend.tf` - Azure Storage + blob locking
  - `gcs-backend.tf` - GCS backend

**Cross-references:**
- Implements: infrastructure-as-code-principles
- Secures: secure-secrets-management
- Used by: ci-cd-pipeline-design

**Testing approach:**
- Application scenario: "Configure remote state for multi-user team"
- Recovery scenario: "Restore from state backup after corruption"

---

### 7. cloud-provider-selection

**Type:** Pattern/Reference
**Skill Level:** Fundamental
**Dependencies:** None

**Description:**
```yaml
name: cloud-provider-selection
description: Use when choosing between AWS, Azure, or GCP for new projects or migrations - provides decision framework based on organizational constraints, service requirements, cost models, and compliance needs
```

**What it teaches:**
- Provider comparison matrix (services, pricing, regions)
- Government cloud requirements (Azure Government, AWS GovCloud)
- Compliance certifications (FedRAMP, ISO 27001)
- Service availability and maturity
- Cost models and billing
- Python SDK comparison (boto3, azure-sdk, google-cloud)
- Lock-in considerations

**Why it matters for elspeth:**
- elspeth-simple supports Azure Blob, could extend to S3/GCS
- Official-sensitive data may require government cloud
- Cost optimization for data processing workloads

**Key sections:**
- Overview: No single "best" provider - context matters
- When to Use: Flowchart for decision process
- Quick Reference: Comparison matrix (services, costs, compliance)
- Implementation: Links to detailed service comparisons
- Common Mistakes: Choosing based on hype, ignoring compliance

**Supporting files:**
- `provider-comparison.md` - Detailed service/pricing comparison
- `government-cloud-requirements.md` - Compliance and certification guide

**Cross-references:**
- Informs: terraform-state-management (backend selection)
- Related to: secure-secrets-management (provider-specific secret services)

**Testing approach:**
- Decision scenario: "Select provider for official-sensitive data processing"
- Application scenario: "Evaluate costs for 1M row/month LLM pipeline"

---

### 8. secure-secrets-management

**Type:** Technique
**Skill Level:** Intermediate
**Dependencies:** cloud-provider-selection

**Description:**
```yaml
name: secure-secrets-management
description: Use when handling API keys, database passwords, or sensitive configuration in cloud deployments - covers vault services (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager), environment injection, rotation strategies, and audit logging
```

**What it teaches:**
- Secret vs config distinction
- Cloud-native secret services (AWS/Azure/GCP)
- Kubernetes Secret management
- Secret rotation patterns
- Access control and least privilege
- Audit logging for secret access
- Local development secret handling
- Secret scanning and prevention

**Why it matters for elspeth:**
- OpenRouter/Azure OpenAI API keys are critical secrets
- Database connection strings for datasources
- HMAC signing keys for artifact security
- Compliance requirements for official-sensitive systems

**Key sections:**
- Overview: Secrets are NOT configuration
- When to Use: Any credential, key, token, or password
- Quick Reference: Secret service comparison table
- Implementation: Complete examples for AWS/Azure/GCP + Python integration
- Common Mistakes: Hardcoded secrets, env vars in logs, no rotation

**Supporting files:**
- `secret-retrieval/` - Python code examples
  - `aws-secrets.py` - boto3 Secrets Manager integration
  - `azure-keyvault.py` - Azure Key Vault with managed identity
  - `gcp-secrets.py` - GCP Secret Manager integration
- `secret-rotation.md` - Rotation strategy guide

**Cross-references:**
- Uses: cloud-provider-selection (provider-specific services)
- Integrated with: kubernetes-deployment-patterns (Secret mounting)
- Part of: ci-cd-pipeline-design (secret injection)

**Testing approach:**
- Application scenario: "Retrieve OpenRouter API key from vault in production"
- Security scenario: "Implement secret rotation for database password"

---

### 9. ci-cd-pipeline-design

**Type:** Pattern
**Skill Level:** Intermediate
**Dependencies:** containerizing-python-applications, infrastructure-as-code-principles

**Description:**
```yaml
name: ci-cd-pipeline-design
description: Use when facing slow deployments, manual release processes, or deployment failures - establishes pipeline patterns for build, test, security scanning, and deployment stages with appropriate gates and rollback strategies
```

**What it teaches:**
- Pipeline stage design (build → test → scan → deploy)
- Branching strategies (trunk-based, GitFlow)
- Artifact management and promotion
- Deployment gates and approvals
- Rollback strategies
- Security scanning integration (dependency check, container scan)
- Environment promotion (dev → staging → prod)
- GitHub Actions / Azure DevOps / GitLab CI patterns

**Why it matters for elspeth:**
- Automated deployment of data processing workflows
- Security scanning for official-sensitive environments
- Reproducible builds and deployments
- Integration with existing CI/CD infrastructure

**Key sections:**
- Overview: Automated path from commit to production
- When to Use: Team size > 1, production deployments, compliance
- Core Pattern: Reference pipeline architecture diagram
- Quick Reference: Stage pattern table
- Implementation: Complete GitHub Actions workflow for elspeth-simple
- Common Mistakes: No rollback plan, missing security gates, manual steps

**Supporting files:**
- `pipeline-examples/` - Complete pipeline definitions
  - `github-actions.yml` - GitHub Actions workflow
  - `azure-pipelines.yml` - Azure DevOps pipeline
  - `gitlab-ci.yml` - GitLab CI configuration
- `pipeline-architecture.dot` - Graphviz diagram of pipeline flow

**Cross-references:**
- Builds: containerizing-python-applications
- Tests with: automated-testing-in-pipelines
- Deploys to: kubernetes-deployment-patterns
- Uses: terraform-state-management, secure-secrets-management

**Testing approach:**
- Design scenario: "Create pipeline for elspeth-simple with security gates"
- Decision scenario: "Choose deployment strategy for zero-downtime release"

---

### 10. automated-testing-in-pipelines

**Type:** Technique
**Skill Level:** Intermediate
**Dependencies:** ci-cd-pipeline-design

**Description:**
```yaml
name: automated-testing-in-pipelines
description: Use when test suites are skipped, run manually, or fail intermittently in CI - covers test pyramid implementation, parallel execution, test data management, and fast feedback loops for Python applications
```

**What it teaches:**
- Test pyramid (unit, integration, e2e) in CI/CD
- Parallel test execution with pytest-xdist
- Test data management (fixtures, factories, mocking)
- Fast feedback strategies (fail-fast, test splitting)
- Flaky test handling
- Coverage requirements and gates
- Testing containers (Docker-in-Docker, testcontainers)
- Performance/load testing in pipelines

**Why it matters for elspeth:**
- elspeth-simple has comprehensive test suite (pytest)
- Data processing requires integration testing with real sources
- Quality gates before production deployment

**Key sections:**
- Overview: Test pyramid and fast feedback
- When to Use: Any CI/CD pipeline, quality requirements
- Quick Reference: Test type comparison table
- Implementation: pytest configuration for CI + GitHub Actions example
- Common Mistakes: Slow tests, no parallelization, skipped integration tests

**Supporting files:**
- `pytest-ci-config/` - CI-optimized pytest configurations
  - `pytest.ci.ini` - Parallel execution, coverage, markers
  - `conftest.py` - CI-specific fixtures
- `test-data-management.md` - Strategies for test data

**Cross-references:**
- Part of: ci-cd-pipeline-design
- May reference: test-driven-development (future superpowers skill)
- Tests: containerizing-python-applications, kubernetes-deployment-patterns

**Testing approach:**
- Application scenario: "Configure parallel pytest execution in GitHub Actions"
- Optimization scenario: "Reduce test suite time from 10min to 3min"

---

### 11. observability-stack-setup

**Type:** Technique
**Skill Level:** Intermediate
**Dependencies:** kubernetes-deployment-patterns

**Description:**
```yaml
name: observability-stack-setup
description: Use when production applications lack visibility, troubleshooting requires pod exec, or incidents have no historical data - implements metrics (Prometheus), logs (Loki/ELK), traces (Jaeger), and dashboards (Grafana) for Python applications
```

**What it teaches:**
- Observability pillars: metrics, logs, traces
- Prometheus metrics instrumentation (prometheus-client)
- Structured logging (JSON logs, correlation IDs)
- OpenTelemetry for distributed tracing
- Grafana dashboard design
- Alert design and notification
- Cost vs signal trade-offs
- Log retention and aggregation

**Why it matters for elspeth:**
- Production data processing needs visibility
- SDA pipeline monitoring (rows processed, errors, costs)
- Troubleshooting LLM integration issues
- Cost tracking visualization (tokens, API calls)

**Key sections:**
- Overview: Three pillars of observability
- When to Use: Production systems, troubleshooting, SLO monitoring
- Quick Reference: Instrumentation pattern table
- Implementation: Complete Python instrumentation + Prometheus/Grafana setup
- Common Mistakes: Too many metrics, unstructured logs, no correlation IDs

**Supporting files:**
- `instrumentation/` - Python code examples
  - `prometheus-metrics.py` - prometheus-client integration
  - `structured-logging.py` - JSON logging with correlation
  - `opentelemetry-tracing.py` - Distributed tracing
- `dashboards/` - Grafana dashboard JSON
  - `elspeth-pipeline.json` - SDA pipeline dashboard
  - `cost-tracking.json` - Token cost visualization
- `observability-architecture.md` - Stack component guide

**Cross-references:**
- Monitors: kubernetes-deployment-patterns, health-checks-and-readiness
- Alerts via: incident-response-workflows
- Part of: production operations

**Testing approach:**
- Application scenario: "Add Prometheus metrics to elspeth-simple"
- Design scenario: "Create dashboard for SDA pipeline monitoring"

---

### 12. incident-response-workflows

**Type:** Technique
**Skill Level:** Advanced
**Dependencies:** observability-stack-setup

**Description:**
```yaml
name: incident-response-workflows
description: Use when facing production outages, data processing failures, or lacking clear escalation paths - provides incident response framework including detection, triage, mitigation, root cause analysis, and postmortem processes
```

**What it teaches:**
- Incident severity classification
- On-call rotation and escalation
- Runbook creation and maintenance
- Common failure modes (and mitigations)
- Communication during incidents
- Root cause analysis (5 whys, fishbone)
- Postmortem writing and blameless culture
- Runbook automation

**Why it matters for elspeth:**
- Data processing failures impact downstream systems
- Official-sensitive data requires documented incident handling
- Production SDA pipelines need clear recovery procedures
- Audit requirements for incident tracking

**Key sections:**
- Overview: Structured approach to production incidents
- When to Use: Production services, SLA commitments, compliance
- Quick Reference: Incident response checklist
- Implementation: Complete runbook template + examples
- Common Mistakes: No runbooks, blame culture, missing postmortems

**Supporting files:**
- `runbooks/` - Template and examples
  - `runbook-template.md` - Standard runbook structure
  - `elspeth-job-failure.md` - SDA job failure runbook
  - `api-rate-limit.md` - LLM API rate limit runbook
- `postmortem-template.md` - Blameless postmortem guide
- `incident-severity.md` - Severity classification guide

**Cross-references:**
- Uses: observability-stack-setup (detection and diagnostics)
- May reference: systematic-debugging (future superpowers skill)
- Part of: production operations maturity

**Testing approach:**
- Application scenario: "Create runbook for elspeth checkpoint recovery"
- Process scenario: "Conduct postmortem for simulated incident"

---

## Implementation Timeline and Phases

### Phase 1: Containerization Foundation (Skills 1-2)
**Dependencies:** None
**Timeline:** Week 1
**Deliverables:**
- containerizing-python-applications skill + Dockerfile examples
- multi-stage-docker-builds skill + optimized examples
- Test both skills with elspeth-simple containerization

### Phase 2: Orchestration Patterns (Skills 3-4)
**Dependencies:** Phase 1
**Timeline:** Week 2
**Deliverables:**
- kubernetes-deployment-patterns skill + K8s manifests
- health-checks-and-readiness skill + health endpoint code
- Test with elspeth-simple Job deployment

### Phase 3: Infrastructure as Code (Skills 5-6)
**Dependencies:** None (parallel to Phases 1-2)
**Timeline:** Week 1-2
**Deliverables:**
- infrastructure-as-code-principles skill
- terraform-state-management skill + backend configs
- Test with example Terraform modules

### Phase 4: Cloud Integration (Skills 7-8)
**Dependencies:** Phase 3
**Timeline:** Week 3
**Deliverables:**
- cloud-provider-selection skill + comparison guide
- secure-secrets-management skill + retrieval code
- Test secret retrieval in all three providers

### Phase 5: CI/CD Automation (Skills 9-10)
**Dependencies:** Phases 1, 3
**Timeline:** Week 4
**Deliverables:**
- ci-cd-pipeline-design skill + pipeline examples
- automated-testing-in-pipelines skill + pytest configs
- Test complete pipeline for elspeth-simple

### Phase 6: Production Operations (Skills 11-12)
**Dependencies:** Phases 2, 5
**Timeline:** Week 5
**Deliverables:**
- observability-stack-setup skill + instrumentation code
- incident-response-workflows skill + runbooks
- Test observability integration with elspeth-simple

---

## Directory Structure

```
.claude/skills/
├── writing-skills/                    # Meta-skill (already installed)
│   ├── SKILL.md
│   ├── anthropic-best-practices.md
│   ├── graphviz-conventions.dot
│   └── persuasion-principles.md
│
└── axiom-cloud-infrastructure/        # New skill pack
    │
    ├── containerizing-python-applications/
    │   ├── SKILL.md
    │   ├── elspeth-simple.Dockerfile
    │   └── dockerignore-template
    │
    ├── multi-stage-docker-builds/
    │   └── SKILL.md
    │
    ├── kubernetes-deployment-patterns/
    │   ├── SKILL.md
    │   └── k8s-manifests/
    │       ├── elspeth-job.yaml
    │       ├── elspeth-deployment.yaml
    │       └── configmap-example.yaml
    │
    ├── health-checks-and-readiness/
    │   ├── SKILL.md
    │   └── health-endpoints.py
    │
    ├── infrastructure-as-code-principles/
    │   └── SKILL.md
    │
    ├── terraform-state-management/
    │   ├── SKILL.md
    │   └── terraform-backends/
    │       ├── s3-backend.tf
    │       ├── azure-backend.tf
    │       └── gcs-backend.tf
    │
    ├── cloud-provider-selection/
    │   ├── SKILL.md
    │   ├── provider-comparison.md
    │   └── government-cloud-requirements.md
    │
    ├── secure-secrets-management/
    │   ├── SKILL.md
    │   ├── secret-retrieval/
    │   │   ├── aws-secrets.py
    │   │   ├── azure-keyvault.py
    │   │   └── gcp-secrets.py
    │   └── secret-rotation.md
    │
    ├── ci-cd-pipeline-design/
    │   ├── SKILL.md
    │   ├── pipeline-examples/
    │   │   ├── github-actions.yml
    │   │   ├── azure-pipelines.yml
    │   │   └── gitlab-ci.yml
    │   └── pipeline-architecture.dot
    │
    ├── automated-testing-in-pipelines/
    │   ├── SKILL.md
    │   ├── pytest-ci-config/
    │   │   ├── pytest.ci.ini
    │   │   └── conftest.py
    │   └── test-data-management.md
    │
    ├── observability-stack-setup/
    │   ├── SKILL.md
    │   ├── instrumentation/
    │   │   ├── prometheus-metrics.py
    │   │   ├── structured-logging.py
    │   │   └── opentelemetry-tracing.py
    │   ├── dashboards/
    │   │   ├── elspeth-pipeline.json
    │   │   └── cost-tracking.json
    │   └── observability-architecture.md
    │
    └── incident-response-workflows/
        ├── SKILL.md
        ├── runbooks/
        │   ├── runbook-template.md
        │   ├── elspeth-job-failure.md
        │   └── api-rate-limit.md
        ├── postmortem-template.md
        └── incident-severity.md
```

---

## Integration with Writing-Skills Methodology

Each skill will be created following the writing-skills TDD approach:

### RED Phase (Baseline Testing)
- Create 3+ pressure scenarios testing each skill
- Document baseline agent behavior without the skill
- Identify common failure patterns and rationalizations

### GREEN Phase (Minimal Skill)
- Write skill addressing specific baseline failures
- Optimize for Claude Search (rich descriptions, keywords)
- Include one excellent example (not multi-language)
- Test that agents now comply with skill guidance

### REFACTOR Phase (Close Loopholes)
- Identify new rationalizations from testing
- Add explicit counters and red flags
- Build rationalization tables
- Re-test until bulletproof

### Quality Checklist
Each skill must pass:
- [ ] Description starts with "Use when..." (CSO optimized)
- [ ] Keywords for search (errors, symptoms, tools)
- [ ] Quick reference table
- [ ] Common mistakes section
- [ ] Tested with pressure scenarios
- [ ] No narrative storytelling
- [ ] Supporting files only for reusable tools/heavy reference

---

## Success Metrics

### Skill Quality
- All 12 skills pass writing-skills checklist
- Each skill tested with 3+ scenarios
- CSO descriptions enable discovery
- Token efficiency (<500 words for non-reference skills)

### Practical Utility
- Skills directly applicable to elspeth-simple deployment
- Cross-references create coherent learning path
- Examples use real project patterns (not generic templates)

### Knowledge Transfer
- New team members can deploy elspeth-simple using skills
- Skills reduce repeated questions about infrastructure
- Production incidents reference runbooks from skills

---

## Future Expansion Opportunities

### Additional Skills to Consider
- **terraform-module-design** - Reusable infrastructure modules
- **cost-optimization-strategies** - Cloud cost reduction techniques
- **disaster-recovery-planning** - Backup and recovery procedures
- **performance-tuning-python** - Optimizing data processing workloads
- **security-hardening-containers** - Advanced container security
- **service-mesh-patterns** - Istio/Linkerd for microservices

### Integration with Other Packs
- **axiom-data-engineering** - BigQuery, Snowflake, data warehousing
- **axiom-security-operations** - SIEM, threat detection, compliance
- **axiom-python-patterns** - Advanced Python techniques for elspeth

---

## Appendix: Skill Type Distribution

| Type | Count | Skills |
|------|-------|--------|
| **Technique** | 7 | containerizing, health-checks, terraform-state, secure-secrets, automated-testing, observability, incident-response |
| **Pattern** | 4 | multi-stage-builds, kubernetes-deployment, infrastructure-principles, ci-cd-pipeline |
| **Reference** | 1 | cloud-provider-selection |

**Rationale:** Heavy emphasis on techniques (how-to guides) for practical application, balanced with patterns (mental models) for decision-making.

---

## Appendix: Elspeth-Simple Integration Examples

### Example 1: Containerized Deployment
Using skills 1, 2, 3:
```bash
# Build with multi-stage pattern (skill 2)
docker build -f elspeth-simple.Dockerfile -t elspeth:latest .

# Deploy as K8s CronJob (skill 3)
kubectl apply -f k8s-manifests/elspeth-job.yaml

# Monitor with health checks (skill 4)
kubectl logs -f job/elspeth-batch
```

### Example 2: Infrastructure Provisioning
Using skills 5, 6, 7:
```bash
# Apply IaC principles (skill 5)
# Use Terraform state management (skill 6)
# Selected Azure based on requirements (skill 7)

cd terraform/azure
terraform init -backend-config=backend.tf
terraform plan
terraform apply
```

### Example 3: Full Production Pipeline
Using skills 9, 10, 11:
```yaml
# CI/CD pipeline (skill 9)
# Runs tests (skill 10)
# Deploys with observability (skill 11)

name: Deploy elspeth
on: [push]
jobs:
  test:
    - pytest --cov --parallel
  build:
    - docker build
  deploy:
    - kubectl apply
    - verify metrics endpoint
```

---

**Document Version:** 1.0
**Created:** 2025-11-14
**Status:** Planning Phase
**Next Action:** Begin Phase 1 implementation (containerizing-python-applications)
