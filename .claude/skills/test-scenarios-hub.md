# Test Scenarios for Infrastructure Hub Skill

## RED Phase: Baseline Testing (WITHOUT hub skill)

These scenarios test whether an agent can find the right infrastructure skill when facing common problems.

### Scenario 1: Deployment Failure - Too Many Options
**Pressure Type:** Time + Uncertainty
**Context:** Production deployment failing, multiple possible causes

**Prompt:**
```
Our elspeth-simple data processing job is failing in production. The pods keep restarting
and we're losing checkpoint data. I need to fix this ASAP - our SLA is at risk.

I think it might be a Docker issue, or maybe Kubernetes configuration, or possibly
health checks? We also haven't set up proper monitoring so I can't see what's happening.

What should I do first?
```

**Expected Failure (baseline):**
- Agent lists all 12 skills without prioritization
- Suggests reading multiple skills in parallel (context burn)
- Doesn't recognize symptoms map to specific skills
- May skip systematic diagnosis in favor of "trying things"

**Success Criteria (with hub):**
- Agent immediately identifies symptom pattern
- Routes to health-checks-and-readiness first
- Then suggests observability-stack-setup for visibility
- Provides clear next steps, not overwhelming list

---

### Scenario 2: Wrong Skill Selection - Technology Confusion
**Pressure Type:** Authority + Sunk Cost
**Context:** Already invested time in wrong approach

**Prompt:**
```
I spent 3 hours trying to optimize our Dockerfile but the image is still 2.5GB.
I've been reading the containerizing-python-applications skill but I'm not making progress.

My manager is asking for a status update. Should I keep working on this or try something else?
The deployment is tomorrow.
```

**Expected Failure (baseline):**
- Agent continues with wrong skill (sunk cost rationalization)
- Doesn't recognize multi-stage-docker-builds is the right solution
- May suggest generic Docker optimization without skill reference
- Misses the symptom: "still 2.5GB" → multi-stage pattern needed

**Success Criteria (with hub):**
- Agent recognizes symptom matches multi-stage-docker-builds
- Explicitly redirects from basic containerizing to multi-stage
- Provides clear "when to escalate" guidance
- Doesn't validate sunk cost ("you're on the right track, keep trying")

---

### Scenario 3: Overwhelmed Newcomer - No Starting Point
**Pressure Type:** Exhaustion + Complexity
**Context:** New to infrastructure, doesn't know where to begin

**Prompt:**
```
I'm new to DevOps and need to deploy elspeth-simple to production. I've never used
Docker or Kubernetes before.

The axiom-cloud-infrastructure pack has 12 skills and I don't know which ones I need
or what order to read them in. I've been reading documentation for 6 hours and I'm
more confused than when I started.

Can you just tell me exactly what to do?
```

**Expected Failure (baseline):**
- Agent provides generic "start with containers, then K8s" advice
- Doesn't reference specific skills in order
- May suggest reading all 12 skills (overwhelming)
- Gives abstract principles instead of concrete learning path

**Success Criteria (with hub):**
- Agent provides clear 3-step learning path with specific skills
- Explains dependencies and build-up order
- References hub skill for navigation
- Concrete, actionable next step (not abstract principles)

---

### Scenario 4: Production Incident - Need Specific Runbook
**Pressure Type:** Time + Authority + Stress
**Context:** Active production incident, need immediate guidance

**Prompt:**
```
URGENT: Our elspeth batch job hit the OpenRouter rate limit and failed halfway through
processing 100k records. The checkpoint file exists but I don't know how to resume.

My director is on a call asking for ETA to recovery. I need the runbook for this NOW.
Which skill has the recovery procedure?
```

**Expected Failure (baseline):**
- Agent tries to solve problem directly without referencing skills
- May suggest generic "read the docs" without specific skill
- Doesn't recognize incident-response-workflows has runbooks
- Misses that this is covered in the infrastructure pack

**Success Criteria (with hub):**
- Immediately routes to incident-response-workflows
- Identifies specific runbook: api-rate-limit.md
- Provides concrete path to recovery procedure
- Acknowledges urgency and gives fastest path to answer

---

### Scenario 5: Skill Discovery Failure - Can't Find Secrets Management
**Pressure Type:** Uncertainty + Compliance Risk
**Context:** Security requirement, can't find right guidance

**Prompt:**
```
Our security team is requiring us to remove hardcoded API keys from environment variables
before we can go to production with official-sensitive data.

I know there's something about secrets in the infrastructure pack, but searching for
"secrets" doesn't help me find the right skill. Is it in Kubernetes? Terraform?
Docker? I've looked at 4 different skills and none of them have what I need.
```

**Expected Failure (baseline):**
- Agent searches individual skills one by one
- Doesn't recognize secure-secrets-management is dedicated skill
- May provide generic advice without skill reference
- Wastes time exploring wrong skills

**Success Criteria (with hub):**
- Hub skill provides clear symptom-to-skill mapping
- Immediately identifies secure-secrets-management
- Explains why it's separate from K8s/Terraform/Docker skills
- Provides keywords that would have found it faster

---

## Baseline Testing Protocol

For each scenario, test with a fresh agent instance that has:
- ✅ Access to axiom-cloud-infrastructure plan document
- ❌ NO hub skill present
- ❌ NO explicit routing guidance

**Document:**
1. Agent's first response (verbatim)
2. Which skills (if any) the agent references
3. Whether agent finds the correct skill
4. Time to correct answer (message count)
5. Rationalizations used ("you're on the right track", "keep reading X")

**Failure patterns to watch for:**
- Lists all 12 skills without prioritization
- Generic advice without skill references
- Wrong skill selection with rationalization
- No clear next step
- Analysis paralysis (suggesting reading multiple skills)

---

## Success Criteria for Hub Skill

After implementing hub skill, re-run all 5 scenarios. Agent should:

1. **Route correctly**: Identify right skill from symptoms 100% of time
2. **Provide path**: Give learning path for dependencies
3. **No overwhelming**: Never suggest reading >3 skills at once
4. **Acknowledge pressure**: Address urgency/time constraints appropriately
5. **Self-reference**: Mention hub skill as navigation tool

**Measurement:**
- Correct skill identified in first response: 5/5 scenarios
- Clear next step provided: 5/5 scenarios
- No rationalization of wrong paths: 5/5 scenarios
- Learning path for dependencies: 3/5 scenarios (where applicable)
