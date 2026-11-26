# Finding verification

A finding is a claim that something can go wrong. Before recording it as confirmed, try to prove it wrong. Most false positives come from a guard the first read missed: middleware, a database policy, a framework default, or a route that is not reachable.

Do this for every finding before it is reported as confirmed, and always for critical and high ones.

## 1. State the claim precisely

Write one sentence: who can do what, to which data, through which entry point. For example: "A signed-in customer can read another customer's invoice through `GET /api/invoices/:id`."

If you cannot name the actor, the action, and the entry point, the finding is not ready. Keep it suspected.

## 2. Look for the guard that would stop it

Check each layer the request passes through, not only the handler you read first:

- Edge and routing: middleware, route matchers, API gateways, rewrites
- The handler: ownership checks, role checks, input validation
- Shared helpers the handler calls, such as a query builder that adds a tenant filter
- The database: row-level security, policies, grants, views, triggers
- The framework's defaults for this version: CSRF protection, escaping, ORM parameter binding
- Configuration: feature flags, environment-specific settings, disabled routes

Record where you looked. If a guard exists, say whether it covers this exact path.

## 3. Check that the path is reachable

- Is the route registered and deployed, or only defined?
- Can the attacker in the claim reach it: signed in, signed out, another tenant?
- Does the input the attack needs actually reach the vulnerable code, or is it replaced, typed, or rejected earlier?

Unreachable code is not a vulnerability. Note it as hardening if the weakness would matter once the code is reachable.

## 4. Test it both ways

In a local or authorised staging environment, with synthetic accounts and data:

- **The denied case:** perform the action the claim says should be blocked. Record the command, the exit code, and what happened.
- **The allowed case:** perform the legitimate version, such as reading your own invoice. If that also fails, the test setup is wrong, and the denied result proves nothing.

Use the smallest request that shows the behaviour. Do not use exploit payloads, real customer data, or production systems.

## 5. Decide

| Result | Status | Confidence |
| --- | --- | --- |
| The denied case succeeded and the allowed case worked | open | confirmed |
| A guard blocks it on this path, shown by a test | false_positive | Say which guard |
| It could not be tested, and no guard was found | suspected | suspected |
| The code is unreachable | false_positive, or informational hardening | Say why |

A critical or high finding is confirmed only by a runtime test. A suspected critical or high finding still blocks release: the gate treats `suspected` as open.

## 6. Record the challenge

Put a short summary in the finding's `challenge` field: where you looked for a guard, whether the path is reachable, and the two test results. For example:

> No ownership check in the handler or the invoice service. No row-level security on `invoices`. Route is public behind sign-in. Own invoice: 200. Other customer's invoice: 200 with their data.

A reviewer should be able to repeat the check from this summary.

For a critical or high finding closed as `false_positive`, the challenge is required: the gate returns NO-GO without it.

## When another agent is available

If your environment can start a separate agent or reviewer, give it only the claim and the location, not your reasoning, and ask it to find the guard. A finding that survives an independent attempt to disprove it is stronger. Record that it was independently checked in `challenge`.
