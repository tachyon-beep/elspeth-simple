# Baseline Test Results - Axiom Web Backend Router

Testing conducted WITHOUT axiom-web-backend skill present.
Model: Claude Haiku
Date: 2025-11-14

## Scenario 1: Framework Selection Under Time Pressure

### User Request
```
I need to build a REST API for our mobile app - we need user auth, profile picture
uploads, and push notifications. I heard FastAPI is really fast and easy. Can you
help me get started quickly? We need an MVP in 2 weeks.
```

### Agent Response Summary
- Immediately accepted FastAPI without questioning the choice
- Provided detailed 2-week implementation plan
- Focused on rapid delivery and practical shortcuts
- Suggested Firebase for notifications, local storage for files
- Gave week-by-week breakdown with specific tasks

### Key Rationalizations (Verbatim)
> "Great choice with FastAPI! It's perfect for rapid development and provides excellent performance."

> "Technology choices that minimize complexity (JWT over complex OAuth2, local storage before S3, Firebase for notifications)"

> "This approach maximizes their chance of shipping a functional MVP while leaving room to add production-grade features (caching, rate limiting, observability) after they have paying users."

### What Agent SKIPPED
- ❌ Questioning if FastAPI is actually right for these requirements
- ❌ Asking about team expertise with Python/async
- ❌ Considering if real-time notifications fit FastAPI architecture
- ❌ Discussing alternative frameworks (Django for batteries-included, Express for Node ecosystem)
- ❌ Asking about mobile platform (iOS/Android/both)
- ❌ Discussing frontend integration patterns

### What Agent DID WELL
- ✅ Provided actionable timeline-based plan
- ✅ Suggested managed services (Firebase) to save time
- ✅ Gave specific package versions to avoid dependency conflicts
- ✅ Mentioned deployment options early

### Analysis
Agent complied with user's stated preference without validation. Shows pattern of **accepting technology choices at face value** when user expresses confidence ("I heard FastAPI is really fast").

---

## Scenario 2: Microservices vs Monolith Decision

### User Request
```
We're starting a new SaaS product. I want to do microservices from the start because
that's what all the big companies do. We need a user service, payment service,
notification service, and analytics service. It's just me and one other developer.
Where should we start?
```

### Agent Response Summary
- **Strongly pushed back** on microservices
- Recommended modular monolith approach
- Explained operational complexity in detail
- Referenced how big companies actually evolved
- Provided clear action plan for monolith-first

### Key Rationalizations (Verbatim)
> "I appreciate the ambition, but I'm going to give you some honest advice: don't start with microservices."

> "Big companies like Netflix, Uber, and Amazon didn't start with microservices. They built monoliths, hit scaling problems, and then split into microservices when they had 100+ engineers and real operational complexity."

> "With two developers, microservices will kill your velocity."

> "The microservices trend is real and powerful, but it's a scaling solution, not a startup solution."

### What Agent DID WELL
- ✅ Questioned user's assumption based on hype
- ✅ Explained operational burden clearly
- ✅ Provided specific criteria for when to split
- ✅ Gave practical monolith structure
- ✅ Addressed time-to-market constraints
- ✅ Referenced industry reality vs. hype

### What Agent SKIPPED
- ❌ Didn't provide specific technology recommendations
- ❌ Didn't ask about domain complexity (might justify early separation)

### Analysis
**PASSED** - Agent showed strong systematic thinking and pushed back appropriately on over-engineering. This is the desired behavior.

---

## Scenario 3: REST vs GraphQL with Mixed Requirements

### User Request
```
I'm building a dashboard that shows users, their orders, products, reviews, and
analytics. I'm worried about over-fetching with REST - should I use GraphQL? I need
this done soon and I've never used GraphQL before but everyone says it's better.
```

### Agent Response Summary
- Questioned GraphQL for single-dashboard use case
- Explained REST optimization patterns (sparse fieldsets, query params)
- Considered learning curve vs. timeline
- Suggested REST first, GraphQL later if needed
- Explained N+1 query problem

### Key Rationalizations (Verbatim)
> "Given your timeline and that you've never used GraphQL before, I'd probably start with REST and optimize it properly."

> "For a single dashboard with known data requirements? Probably overkill."

> "With your timeline, you'd likely spend a week learning GraphQL when you could ship in 2-3 days with optimized REST."

> "Over-fetching is the reason people cite for GraphQL, but it's solvable in REST with basic query parameter patterns."

### What Agent DID WELL
- ✅ Questioned technology choice based on use case
- ✅ Considered learning curve vs timeline constraints
- ✅ Provided REST optimization patterns
- ✅ Explained when GraphQL actually makes sense
- ✅ Suggested incremental approach

### What Agent SKIPPED
- ❌ Didn't ask about future client diversity (mobile apps, partners)
- ❌ Didn't discuss type safety / code generation benefits

### Analysis
**PASSED** - Agent appropriately right-sized the solution and questioned the GraphQL hype. Good systematic thinking about technology tradeoffs.

---

## Scenario 4: Error Handling and Validation Under Pressure

### User Request
```
I've got my Express API routes working and data is flowing. I know I should add
validation and proper error handling but I'm behind schedule. Can I just add that
later once the core features are done? What's the minimum I need right now?
```

### Agent Response Summary
- Pushed back on skipping validation
- Provided "minimum non-negotiables" (status codes, try-catch, basic checks)
- Explained why deferring is more costly
- Gave 30-minute essential list
- Noted context mismatch (Express vs Python project) but answered anyway

### Key Rationalizations (Verbatim)
> "I get the time pressure, but here's the reality: deferring error handling is more costly than doing it now."

> "Skipping error handling doesn't save time - it trades small work now for massive work later."

> "Debugging is 10x harder without error handling - you'll spend more time chasing bugs later"

> "What You Can Defer: Complex validation schemas (use express-validator/joi later), Custom error classes and codes, Detailed logging/metrics, Graceful degradation for edge cases"

### What Agent DID WELL
- ✅ Pushed back on skipping validation
- ✅ Gave minimum viable checklist
- ✅ Explained cost of deferring

### What Agent SKIPPED
- ❌ **Security risks** - mentioned only briefly, not emphasized
- ❌ **Frontend impact** - didn't discuss how poor errors affect UX
- ❌ **Data corruption risks** - mentioned but not emphasized

### CRITICAL RATIONALIZATION
The "What You Can Defer" section **provides wiggle room**. Agent gave permission to skip "complex validation" which could rationalize skipping validation entirely.

### Analysis
**MIXED** - Agent pushed back but left loopholes. The "defer complex validation" guidance could rationalize "I'll just do basic validation and call it good."

---

## Scenario 5: Message Queue Technology Selection

### User Request
```
I need to process user-uploaded videos in the background. I've heard Kafka is what all
the big companies use for this. Should I set up Kafka? Or is there something simpler?
I'm handling maybe 100 videos a day right now but want to scale.
```

### Agent Response Summary
- Right-sized solution (suggested Redis Queue/SQS over Kafka)
- Explained operational complexity of Kafka
- Provided growth path showing when to upgrade
- Calculated actual volume (4-5 videos/hour)
- Referenced big company evolution patterns

### Key Rationalizations (Verbatim)
> "You're asking the right question—Kafka is powerful but often overkill for where you're starting."

> "At 100 videos daily, you're looking at roughly 4-5 videos per hour. This is not a scale that demands Kafka's complexity."

> "Don't do Kafka until you feel pain. You won't feel pain at 100/day."

> "Kafka is great infrastructure, but it's built for problems you don't have yet—and you don't want to carry that weight prematurely."

### What Agent DID WELL
- ✅ Calculated actual requirements (100/day = 4-5/hour)
- ✅ Right-sized the solution
- ✅ Provided clear growth thresholds
- ✅ Explained operational complexity
- ✅ Gave multiple simple options

### What Agent SKIPPED
- ❌ Didn't ask about reliability requirements
- ❌ Didn't discuss message delivery guarantees

### Analysis
**PASSED** - Agent showed excellent systematic thinking about scaling and operational complexity. Appropriately questioned the Kafka choice.

---

## Cross-Scenario Patterns

### ✅ What Agents Did Well
1. **Pushed back on over-engineering** (microservices, GraphQL, Kafka)
2. **Considered timeline constraints** in all scenarios
3. **Referenced industry reality** vs hype (Netflix/Uber evolution)
4. **Provided growth paths** showing when to upgrade technologies
5. **Calculated actual requirements** (100/day = 4-5/hour)

### ❌ What Agents Consistently Skipped
1. **Team expertise questions** - Never asked about existing skills
2. **Frontend/mobile impact** - Rarely considered client-side implications
3. **Security emphasis** - Mentioned but not prioritized
4. **Systematic decision frameworks** - No structured approach to choices
5. **Cross-pattern references** - Each answer standalone, no "see also auth patterns"
6. **Alternative framework exploration** - When user stated preference, didn't explore alternatives

### 🚨 Critical Rationalizations Found

| Rationalization | Scenario | Risk |
|----------------|----------|------|
| "Great choice with FastAPI!" | 1 | Validates user choice without questioning |
| "What You Can Defer: Complex validation" | 4 | Provides wiggle room to skip validation |
| "Technology choices that minimize complexity" | 1 | Justifies decisions without validation |
| "I'd probably start with REST" | 3 | Hedging language ("probably") instead of systematic criteria |

### Missing Systematic Elements

1. **No decision frameworks** - Agents made good judgments but didn't provide reusable criteria
2. **No cross-references** - Each scenario treated independently
3. **No "always ask" checklist** - Team size, expertise, timeline mentioned ad-hoc
4. **No frontend-first thinking** - API design rarely considered consumer needs
5. **No security-by-default** - Security mentioned as afterthought

---

## Test Scenario Success Metrics

Original expectations for baseline (WITHOUT skill):

- [ ] Agent questions user's framework assumptions - **MIXED** (2/5 scenarios)
- [ ] Agent asks about team size/expertise - **FAILED** (0/5 scenarios)
- [ ] Agent considers operational complexity - **PASSED** (4/5 scenarios)
- [ ] Agent mentions validation/security upfront - **FAILED** (1/5 scenarios)
- [ ] Agent thinks about frontend impact - **FAILED** (0/5 scenarios)
- [ ] Agent suggests right-sized solutions - **PASSED** (4/5 scenarios)
- [ ] Agent provides systematic decision framework - **FAILED** (0/5 scenarios)
- [ ] Agent cross-references related patterns - **FAILED** (0/5 scenarios)

**Overall: 2/8 metrics passed** - Room for significant improvement.

---

## Key Insights for Skill Design

### Must Address in Router Skill

1. **Systematic decision framework** for technology choices
2. **Always ask questions** checklist (team, expertise, scale, timeline)
3. **Frontend-first API design** mindset
4. **Security-by-default** emphasis (not "add later")
5. **Cross-reference structure** to sub-skills
6. **Explicit counters** for common rationalizations

### Specific Rationalizations to Counter

- "User knows what they want" → Always validate with questions
- "Can add security later" → Security is not optional or deferrable
- "Complex validation can wait" → Validation is part of MVP, not polish
- "Big companies use X" → Big companies have different problems

### Router Skill Core Jobs

1. Help choose the RIGHT framework (not just accept user's choice)
2. Provide decision criteria (not just vibes)
3. Reference appropriate sub-skills
4. Enforce systematic questioning
5. Keep frontend/UX concerns visible

---

## Next Steps

Now that baseline is documented, proceed to GREEN phase:
- Write router skill addressing these specific gaps
- Focus on systematic decision frameworks
- Add "always ask" checklists
- Include explicit rationalization counters
- Cross-reference the 11 sub-skills
