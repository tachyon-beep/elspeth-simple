# PACK.md Navigation Test Scenarios

## Baseline Testing (RED Phase)

These scenarios test whether agents can effectively navigate the skill pack WITHOUT PACK.md.

### Scenario 1: New Application Deployment (Multi-Skill Workflow)
**Pressure:** Time constraint + Authority ("production deadline tomorrow")
**Task:** "We need to deploy this new Python Flask app to production Kubernetes by tomorrow. What do we need to do?"

**Expected behavior WITH proper navigation:**
1. Identify the workflow: containerize → secure → observe → deploy → automate
2. Find containerizing-applications skill
3. Find securing-cloud-infrastructure skill
4. Find implementing-observability skill
5. Find orchestrating-with-kubernetes skill
6. Find building-deployment-pipelines skill
7. Follow them in correct order

**Baseline test (WITHOUT PACK.md):**
- Run with just the skill list, no navigation
- Document: Do they find the right skills? In what order? What do they miss?

---

### Scenario 2: Skill Selection Confusion (Wrong Tool for the Job)
**Pressure:** Sunk cost ("I already wrote this Terraform") + Exhaustion ("debugging for 3 hours")
**Task:** "My Terraform apply keeps failing with 'state lock' errors. I've been debugging for 3 hours. Which skill do I use?"

**Expected behavior WITH proper navigation:**
1. Identify this is Terraform/IaC problem
2. Navigate to managing-infrastructure-as-code skill
3. Find state management patterns
4. Use troubleshooting-infrastructure as secondary if needed

**Baseline test (WITHOUT PACK.md):**
- Document: Which skills do they check? Do they find IaC skill quickly? Do they waste time in wrong skills?

---

### Scenario 3: Security Review Before Deploy (Discipline Enforcement)
**Pressure:** Production down + Authority ("CEO is asking when it'll be fixed") + Time ("need it now")
**Task:** "Production database is down. I have a fix ready. Deploy this RDS instance NOW."

**Expected behavior WITH proper navigation:**
1. Recognize security is NOT optional despite pressure
2. Navigate to securing-cloud-infrastructure skill BEFORE deploying
3. Follow security checklist
4. Also check implementing-observability (monitor the fix)

**Baseline test (WITHOUT PACK.md):**
- Document: Do they skip security under pressure? Do they know security is discipline-enforcing? Do they find the right skill?

---

### Scenario 4: Cost Spike Investigation (Domain Expertise Needed)
**Pressure:** Financial constraint ("budget blown") + Authority ("finance team escalated")
**Task:** "Our AWS bill jumped from $5K to $25K this month. Figure out why and fix it."

**Expected behavior WITH proper navigation:**
1. Identify this as cost optimization problem
2. Navigate to optimizing-cloud-costs skill
3. Use implementing-observability for metrics
4. Use deploying-to-aws for AWS-specific tools

**Baseline test (WITHOUT PACK.md):**
- Document: Do they find cost optimization skill? Do they know to check metrics first? What order?

---

### Scenario 5: Multi-Cloud Confusion (Reference Skill Selection)
**Pressure:** Unfamiliarity ("new to GCP") + Time ("need it today")
**Task:** "We're moving from AWS to GCP. Set up a private GKE cluster with Cloud SQL accessible only from private subnet. Never used GCP before."

**Expected behavior WITH proper navigation:**
1. Recognize this is GCP-specific (not AWS)
2. Navigate to deploying-to-gcp skill (not deploying-to-aws)
3. Cross-reference orchestrating-with-kubernetes for GKE
4. Cross-reference securing-cloud-infrastructure for private networking
5. Follow GCP-specific patterns

**Baseline test (WITHOUT PACK.md):**
- Document: Do they go to AWS skill by habit? Do they find GCP skill? Do they understand skill boundaries?

---

## Testing Protocol

For each scenario:

1. **Setup:** Provide skill list only (no PACK.md, no descriptions, just names)
2. **Run:** Present the scenario
3. **Document verbatim:**
   - Which skills do they check first?
   - What's their search strategy?
   - What do they miss?
   - Do they understand skill relationships?
   - What rationalizations do they use?
4. **Identify patterns:**
   - Common navigation failures
   - Missing information
   - Workflow confusion
   - Skill selection errors

---

## Success Criteria (for GREEN phase)

Agent WITH PACK.md should:
- Find correct skill within 1-2 attempts
- Understand which skill type (technique/reference/discipline)
- Follow multi-skill workflows in correct order
- Recognize discipline-enforcing skills (don't skip under pressure)
- Navigate between related skills effectively

---

## Expected Baseline Failures (to document)

Common issues WITHOUT navigation:
- Random skill selection ("I'll just try orchestrating-with-kubernetes")
- Missing prerequisite skills in workflows
- Not recognizing discipline-enforcing skills
- Confusing similar skills (deploying-to-aws vs deploying-to-gcp)
- No understanding of skill relationships
- Trial-and-error instead of systematic navigation
- Skipping security/observability under pressure
