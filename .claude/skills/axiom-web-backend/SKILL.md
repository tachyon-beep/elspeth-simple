---
name: axiom-web-backend
description: Use when building backend APIs, choosing frameworks (FastAPI/Django/Express), designing REST/GraphQL endpoints, or implementing microservices/message queues - provides systematic decision frameworks that question assumptions, prioritize security and validation upfront, and align API design with frontend needs
---

# Axiom Web Backend

## Overview

Systematic approach to production backend development. **Core principle:** Question technology choices, validate requirements first, design APIs for frontend happiness.

## When to Use

Building or designing:
- REST or GraphQL APIs
- Microservices vs monolith architecture
- Message queue / async job systems
- Authentication / authorization layers
- Framework selection (FastAPI, Django, Express, etc.)

When NOT to use:
- Frontend-only projects (use lyra-web-frontend)
- Infrastructure/DevOps tasks
- Database-only design

## Critical: Always Ask BEFORE Accepting Choices

```dot
digraph decision_framework {
    rankdir=LR;
    node [shape=box];

    start [label="User suggests\ntechnology X"];
    questions [label="Ask requirement\nquestions"];
    validate [label="Validate choice\nagainst needs"];
    decide [label="Recommend\nright-sized solution"];

    start -> questions;
    questions -> validate;
    validate -> decide;
}
```

**Never immediately accept** user's stated technology preference. Always validate with:

1. **Team reality** - "What's your team's experience with [technology]?"
2. **Actual scale** - "What's your current/expected volume?" (calculate per hour/minute)
3. **Timeline constraints** - "What's your deadline?" (consider learning curves)
4. **Client needs** - "What platforms consume this API?" (web, mobile, partners)
5. **Operational capacity** - "Who maintains this?" (2-person team vs 50-person team)

## Framework Selection Decision Framework

| Requirement | FastAPI | Django REST | Express |
|-------------|---------|-------------|---------|
| Python team, async-heavy | ✅ Best | ❌ Sync default | ❌ Node |
| Python team, batteries-included | ⚠️ Manual | ✅ Best | ❌ Node |
| Node team, existing ecosystem | ❌ Python | ❌ Python | ✅ Best |
| Rapid prototyping, small scale | ✅ Good | ✅ Good | ✅ Good |
| Large team, established patterns | ⚠️ Newer | ✅ Mature | ✅ Mature |

**Don't just accept "I heard X is fastest"** - validate against team skills and requirements.

## Architecture Decisions

### Monolith vs Microservices

```
IF team_size < 10 AND operational_expertise == "low":
    → Start with modular monolith
ELSE IF specific_scaling_pain exists:
    → Extract specific service causing pain
ELSE:
    → "Big companies use microservices" is NOT a valid reason
```

**Red flag rationalizations:**
- "Netflix uses microservices" → Netflix has 1000+ engineers
- "Better to start right" → Monolith IS starting right for small teams
- "We'll need to scale" → Premature optimization, scale when painful

**Reference:** axiom-microservices-communication (for when you actually need microservices)

### REST vs GraphQL

```
IF single_client AND known_requirements AND timeline_tight:
    → REST with query params (?fields=name,email)
ELSE IF multiple_diverse_clients AND changing_requirements:
    → Consider GraphQL
ELSE IF never_used_graphql AND time_pressure:
    → REST first, GraphQL later if needed
```

**Reference:** axiom-api-design-principles

## Security and Validation: NOT Optional

**Baseline failures showed agents suggesting "add security later"** - this is WRONG.

### Non-Negotiables for MVP

These are NOT "nice to have" or "add later":

1. ✅ **Request validation** - Pydantic/Zod/Joi schemas from day 1
2. ✅ **HTTP status codes** - Proper 400/401/403/500 responses
3. ✅ **Error handling** - Try-catch at route level minimum
4. ✅ **Rate limiting** - Even simple fixed-window is better than none
5. ✅ **Input sanitization** - SQL injection / XSS prevention

**Time cost:** 30-60 minutes upfront saves 20+ hours debugging later.

**Reference:** axiom-request-validation, axiom-rate-limiting-patterns

## Frontend-First API Design

APIs exist to serve frontends. **Always consider:**

- Will mobile apps parse this easily?
- Are error messages screen-reader friendly?
- Do field names match frontend conventions (camelCase vs snake_case)?
- Is pagination consistent across endpoints?
- Can frontend detect error types programmatically?

**Reference:** axiom-response-formatting, axiom-api-design-principles

## Technology Right-Sizing

| User Says | Volume | Right Answer |
|-----------|--------|--------------|
| "Should I use Kafka?" | 100 events/day | No. Redis Queue or SQS |
| "Need microservices" | 2 developers | No. Modular monolith |
| "GraphQL is better" | Single dashboard | Probably REST with query params |
| "FastAPI is fastest" | Team knows Django | Maybe, but consider Django DRF |

**Pattern:** Calculate actual requirements, question hype-driven choices.

## Common Rationalizations to Reject

| Rationalization | Reality |
|----------------|---------|
| "User knows what they want" | Users know pain points, not always solutions |
| "Can add validation later" | Validation IS the feature (security, data integrity) |
| "Complex validation can wait" | Basic validation takes 10 minutes, prevents hours of debugging |
| "Big companies use X" | Big companies have different problems and teams |
| "Will add security after MVP" | Security vulnerabilities block launches, add now |
| "Framework X is fastest" | Fastest for WHO? Team expertise matters more |

## Related Skills (Axiom Web Backend Suite)

**Core API Design (3 skills):**
- axiom-api-design-principles - Versioning, contracts, REST/GraphQL patterns
- axiom-request-validation - Pydantic, Zod, sanitization
- axiom-response-formatting - Errors, pagination, consistency

**Security & Control (3 skills):**
- axiom-authentication-patterns - JWT, OAuth, sessions
- axiom-authorization-patterns - RBAC, permissions
- axiom-rate-limiting-patterns - DOS prevention, throttling

**Architecture (3 skills):**
- axiom-microservices-communication - When and how to split
- axiom-message-queue-patterns - Redis, RabbitMQ, SQS, Kafka
- axiom-async-background-jobs - Celery, Bull, job queues

**Framework-Specific (3 skills):**
- axiom-fastapi-production - Async, dependency injection
- axiom-django-rest-production - DRF viewsets, serializers
- axiom-express-production - Middleware, error handling

## Quick Reference

### Before Recommending Any Technology

- [ ] Asked about team expertise?
- [ ] Calculated actual scale (events per hour/minute)?
- [ ] Considered frontend integration?
- [ ] Validated timeline against learning curve?
- [ ] Questioned user's stated preference?
- [ ] Mentioned security/validation as MVP requirement?

### Red Flags - STOP and Question Assumptions

- User says "I heard X is best"
- User wants microservices with <5 person team
- User wants to "add validation later"
- User chooses GraphQL without multiple clients
- User wants Kafka for <1000 events/day
- User accepts framework without team skill discussion

**All of these mean: Ask requirement questions, validate the choice.**
