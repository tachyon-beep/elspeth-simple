---
name: axiom-cloud-infrastructure-hub
description: Use when deploying Python applications to production, facing infrastructure problems (container issues, Kubernetes failures, secrets management, CI/CD setup), or overwhelmed by 12 infrastructure skills - provides symptom-to-skill routing, beginner deployment path, and fastest route to solutions under time pressure
---

# Axiom Cloud Infrastructure Hub

## Overview

**This is the entry point for the axiom-cloud-infrastructure skill pack.**

The pack contains 12 skills covering Docker, Kubernetes, Terraform, CI/CD, secrets, and observability. This hub routes you to the RIGHT skill based on your symptoms, experience level, and time constraints.

**Core principle:** Symptom-based routing is faster than sequential reading or guessing.

## When to Use

**Use this hub when:**
- Facing infrastructure problems and unsure which skill applies
- New to infrastructure and need a learning path
- Under time pressure (incidents, deadlines) and need the fastest solution
- Successfully using one skill and need to know what's next

**Don't use this hub when:**
- You already know exactly which skill you need (go directly to it)
- Working on application code (not infrastructure)
- Problem is clearly documented in elspeth-simple's CLAUDE.md

## Quick Reference: Symptom → Skill Routing

| Symptom | Skill | Why |
|---------|-------|-----|
| **Docker image >1GB, slow builds** | multi-stage-docker-builds | 60-80% size reduction pattern |
| **Never containerized Python before** | containerizing-python-applications | Dockerfile basics, Python 3.13+, uv |
| **Pods restarting, CrashLoopBackOff** | health-checks-and-readiness | Liveness/readiness probes |
| **Checkpoint/state data lost on restart** | kubernetes-deployment-patterns | Persistent volumes for stateful apps |
| **Don't know Job vs Deployment** | kubernetes-deployment-patterns | Workload type selection |
| **Hardcoded API keys, secrets in env vars** | secure-secrets-management | Vault services, rotation |
| **Manual deployments, no automation** | ci-cd-pipeline-design | Build → test → deploy pipeline |
| **Tests skipped in CI, slow pipelines** | automated-testing-in-pipelines | Parallel pytest, fast feedback |
| **Can't troubleshoot production issues** | observability-stack-setup | Metrics, logs, traces, dashboards |
| **No runbooks, chaotic incidents** | incident-response-workflows | Runbooks, postmortems, on-call |
| **Manual cloud provisioning, drift** | infrastructure-as-code-principles | IaC philosophy, versioning |
| **Terraform state conflicts, lost state** | terraform-state-management | Remote state, locking, backup |
| **Choosing between AWS/Azure/GCP** | cloud-provider-selection | Decision framework, compliance |

**Multiple symptoms?** Start with the symptom causing immediate pain, then address root causes:
- **Incident + No monitoring** → Fix incident first (direct troubleshooting), then add observability-stack-setup
- **Restarts + No checkpoints** → Fix health-checks-and-readiness first, then kubernetes-deployment-patterns for persistence
- **Large images + Slow CI** → Fix multi-stage-docker-builds first (biggest impact), then automated-testing-in-pipelines

## Beginner Path: Get to Production (3 Skills, 1-2 Weeks)

**If you've never deployed to production before, start here:**

### Week 1: Containerization
**Skill:** containerizing-python-applications
**Time:** 2-3 days
**Goal:** Dockerfile for elspeth-simple, test locally
**Next step:** Can run `docker build` and `docker run` successfully

### Week 2: Orchestration
**Skill:** kubernetes-deployment-patterns
**Time:** 3-4 days
**Goal:** Deploy as Kubernetes Job, verify it runs
**Next step:** `kubectl apply` works, job completes successfully

### Week 3: Reliability
**Skill:** health-checks-and-readiness
**Time:** 1-2 days
**Goal:** Add health endpoint, configure probes
**Next step:** Pods don't restart unexpectedly

**You're now in production.** Everything else is optimization or team collaboration.

## Comprehensive Path: All 12 Skills

**For complete infrastructure maturity, see:** [axiom-cloud-infrastructure-plan.md](../../../docs/axiom-cloud-infrastructure-plan.md)

The plan document provides:
- All 12 skill specifications with detailed descriptions
- Dependency graph showing skill relationships
- 6 implementation phases with timeline
- Integration examples with elspeth-simple
- Supporting files reference (30+ Dockerfiles, manifests, configs)

**Use the plan when:**
- Building enterprise-grade infrastructure
- Need comprehensive understanding of all skills
- Planning team onboarding or training
- Establishing infrastructure standards

**Use this hub when:**
- Need fast routing to one skill
- Starting from zero (beginner path)
- Under time pressure (symptom index)

## Skill Dependencies (What to Read First)

```
Foundation (no prerequisites):
├── containerizing-python-applications
├── infrastructure-as-code-principles
└── cloud-provider-selection

Build on containerization:
├── multi-stage-docker-builds (requires: containerizing)
└── kubernetes-deployment-patterns (requires: containerizing)
    └── health-checks-and-readiness (requires: kubernetes-deployment)

Build on IaC:
├── terraform-state-management (requires: infrastructure-as-code)
└── secure-secrets-management (requires: cloud-provider-selection)

Build on both:
├── ci-cd-pipeline-design (requires: containerizing + terraform-state)
└── automated-testing-in-pipelines (requires: ci-cd-pipeline)

Production operations (build on kubernetes):
├── observability-stack-setup (requires: kubernetes-deployment)
└── incident-response-workflows (requires: observability-stack)
```

**Rule:** Read foundation skills before dependent skills. Order within same level doesn't matter.

## Time-Pressure Guidance

### Decision: Incident vs. Deadline vs. Learning

```
Is production down RIGHT NOW?
  ├─ YES → Production Incident (see below) - Direct troubleshooting
  └─ NO → Is deadline <48 hours?
      ├─ YES → Tight Deadline (see below) - Symptom index + Quick Reference
      └─ NO → Learning Mode (see below) - Beginner or comprehensive path
```

### Production Incident (RIGHT NOW)
**Don't read skills during active incidents.** Skills are for learning and prevention, not firefighting.

**Do this instead:**
1. **Immediate:** Use kubectl/docker commands to diagnose and mitigate
2. **After recovery:** Read incident-response-workflows to create runbooks
3. **Prevention:** Read observability-stack-setup to catch issues earlier

**Exception:** If incident involves unfamiliar concepts (e.g., "what's a readiness probe?"), 2-minute skim of relevant skill is OK, then back to mitigation.

### Tight Deadline (Tomorrow/This Week)
**Use symptom index above** to find the ONE skill that solves your specific problem.

- Don't read multiple skills in parallel
- Don't read comprehensively - read the Quick Reference section only
- Don't optimize - get it working first
- Do: Copy example, adapt, test, ship

**After deadline:** Come back and read properly to prevent technical debt.

### Learning Mode (No Pressure)
**Use beginner path or comprehensive path** depending on goals.

- Beginner: 3 skills in order
- Comprehensive: All 12 via plan document
- Realistic time: 1-2 weeks for beginner, 4-6 weeks for comprehensive

## Common Mistakes

| Mistake | Reality | Fix |
|---------|---------|-----|
| "I'll read all 12 skills before starting" | Overwhelming, low retention, delayed action | Use beginner path (3 skills) or symptom index (1 skill) |
| "Skills are for learning, I'll troubleshoot directly" | Ad-hoc solutions create technical debt | Skills contain production patterns tested under pressure |
| "Too many options, I'll guess which skill" | 50% chance of wrong skill, wasted time | Use symptom index - 100% accuracy, instant |
| "Time pressure means skip documentation" | Wrong approach takes longer to fix | Right skill = faster than trial-and-error |
| "I already read containerizing, that's enough" | Missing critical production patterns | Health checks and observability prevent 80% of issues |
| "This problem is unique to my situation" | 95% of infrastructure problems are common | Symptom index covers most scenarios |
| "This is a diagnostic problem, not a skill problem" | Many skills provide diagnostic workflows | Check symptom index first - might have exact solution |
| "I'll solve it directly and learn the pattern later" | Solving incorrectly wastes more time than learning | 5 min in right skill > 2 hours trial-and-error |

## Red Flags - STOP and Use This Hub

**You should have used this hub if you:**
- Spent >1 hour searching for the right skill
- Read 3+ skills without finding your answer
- Tried to solve problem directly and got stuck
- Feel overwhelmed by infrastructure complexity
- Keep finding pieces of answer across multiple skills
- Don't know which skill to read next after finishing one

**All of these mean:** Stop searching, consult symptom index above.

## When to Skip This Hub

**Go directly to a skill (don't use hub) when:**
- You know exactly which skill you need
- Following a specific tutorial that references a skill
- Continuing work on a skill you're already using
- Following the plan document's implementation phases

**The hub is for routing, not required reading.**

## Navigation Workflow

```
1. Problem occurs
   ↓
2. Check symptom index (this hub)
   ↓
3. Go to identified skill
   ↓
4. Read Quick Reference section of that skill
   ↓
5. Implement solution
   ↓
6. If dependencies needed, check dependency graph above
```

**Average time:** 5 minutes from symptom to skill to solution start.

**Compare to:** 30-60 minutes reading multiple skills hoping to find answer.

## Hub Updates

This hub will evolve as:
- New failure patterns emerge from baseline testing
- Additional skills added to the pack
- User feedback identifies missing symptom mappings

**Last updated:** 2025-11-14 (v1.0 - Initial TDD-tested version)

## Related Skills

**Meta-skills:**
- writing-skills - How this hub was created (TDD for documentation)

**Future integration:**
- test-driven-development (superpowers) - Referenced by automated-testing-in-pipelines
- systematic-debugging (superpowers) - Referenced by incident-response-workflows

---

**The Bottom Line:** This hub exists because "12 skills" is too many choices under pressure. Symptom index + beginner path + plan document = always know exactly what to read next.
