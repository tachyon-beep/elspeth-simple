# Axiom Web Backend Router - Baseline Test Scenarios

These scenarios test agent behavior WITHOUT the axiom-web-backend skill present.

## Scenario 1: Framework Selection Under Time Pressure

**Context:** User needs a backend API for a mobile app, wants it "quick and simple"

**Pressures:**
- Time pressure: "Need MVP in 2 weeks"
- Authority pressure: "I heard FastAPI is fastest"
- Complexity: Auth, file uploads, real-time notifications needed

**User Message:**
```
I need to build a REST API for our mobile app - we need user auth, profile picture uploads,
and push notifications. I heard FastAPI is really fast and easy. Can you help me get started
quickly? We need an MVP in 2 weeks.
```

**What to observe:**
- Does agent question framework choice or just comply?
- Does agent consider all requirements (real-time, files)?
- Does agent skip validation/error handling for speed?
- Does agent mention API design patterns?
- Does agent consider frontend (mobile) needs?

---

## Scenario 2: Microservices vs Monolith Decision

**Context:** Startup with 2 developers, wants to "do microservices right"

**Pressures:**
- Authority pressure: "I read microservices are best practice"
- Complexity: Limited team size, multiple services planned
- Sunk cost: Already thinking about service boundaries

**User Message:**
```
We're starting a new SaaS product. I want to do microservices from the start because that's
what all the big companies do. We need a user service, payment service, notification service,
and analytics service. It's just me and one other developer. Where should we start?
```

**What to observe:**
- Does agent challenge microservices for small team?
- Does agent consider operational complexity?
- Does agent suggest monolith-first approach?
- Does agent ask about actual scalability needs?
- Does agent mention DevOps/monitoring requirements?

---

## Scenario 3: REST vs GraphQL with Mixed Requirements

**Context:** Building API for web dashboard with lots of related data

**Pressures:**
- Complexity: Many entities with relationships
- Authority pressure: "GraphQL solves over-fetching"
- Time pressure: "Need to launch soon"

**User Message:**
```
I'm building a dashboard that shows users, their orders, products, reviews, and analytics.
I'm worried about over-fetching with REST - should I use GraphQL? I need this done soon
and I've never used GraphQL before but everyone says it's better.
```

**What to observe:**
- Does agent consider learning curve vs timeline?
- Does agent ask about actual over-fetching problems?
- Does agent suggest REST with proper endpoints first?
- Does agent mention GraphQL complexity (N+1, caching)?
- Does agent consider incremental approach?

---

## Scenario 4: Error Handling and Validation Under Pressure

**Context:** Already started coding, validation feels like "extra work"

**Pressures:**
- Sunk cost: Already wrote routes without validation
- Time pressure: "Just need to get it working"
- Rationalization: "Will add validation later"

**User Message:**
```
I've got my Express API routes working and data is flowing. I know I should add validation
and proper error handling but I'm behind schedule. Can I just add that later once the core
features are done? What's the minimum I need right now?
```

**What to observe:**
- Does agent push back on skipping validation?
- Does agent explain security risks?
- Does agent suggest minimal validation approach?
- Does agent rationalize "add later" approach?
- Does agent mention frontend impact of poor errors?

---

## Scenario 5: Message Queue Pattern Selection

**Context:** Need async job processing, many options available

**Pressures:**
- Complexity: Multiple queue technologies (Redis, RabbitMQ, SQS)
- Authority pressure: "Kafka is what Netflix uses"
- Over-engineering risk

**User Message:**
```
I need to process user-uploaded videos in the background. I've heard Kafka is what all the
big companies use for this. Should I set up Kafka? Or is there something simpler?
I'm handling maybe 100 videos a day right now but want to scale.
```

**What to observe:**
- Does agent right-size the solution?
- Does agent ask about actual requirements?
- Does agent suggest simpler options first?
- Does agent explain operational complexity?
- Does agent consider team expertise?

---

## Testing Protocol

For each scenario:

1. **Run with fresh subagent** (no skill loaded)
2. **Document exact response** (copy-paste verbatim)
3. **Note rationalizations** (any "it's fine because..." statements)
4. **Identify gaps** (what should they have asked/mentioned?)
5. **Record poor decisions** (framework choices, skipped steps, etc.)

## Success Metrics (Baseline - Expect These to FAIL)

- [ ] Agent questions user's framework assumptions
- [ ] Agent asks about team size/expertise
- [ ] Agent considers operational complexity
- [ ] Agent mentions validation/security upfront
- [ ] Agent thinks about frontend impact
- [ ] Agent suggests right-sized solutions
- [ ] Agent provides systematic decision framework
- [ ] Agent cross-references related patterns

## Post-Baseline Analysis

After running all scenarios, answer:

1. What did agents consistently skip?
2. What rationalizations appeared most?
3. Where did agents blindly comply vs push back?
4. What systematic thinking was missing?
5. Which frontend/UX concerns were ignored?
