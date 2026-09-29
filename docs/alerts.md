# Alert runbooks

Alerts use user-visible symptoms from `data/logs.jsonl`. Notify
`#day13-llmops-alerts`; the active on-call owner acknowledges the page and records
the incident time range and affected correlation IDs.

## Alert 1: Chat availability degraded

- **Severity / duration:** Critical; error rate above 2% for 5 minutes.
- **SLI:** Failed chat requests divided by received chat requests. The 2% guardrail
  protects the 99.5% fast-successful-request SLO from rapid budget burn.
- **User impact:** More users receive failed chat requests.
- **First checks:** Confirm the time range and request volume; group
  `request_failed` logs by `error_type`; select an affected `correlation_id` and
  inspect its trace.
- **Mitigation:** Use the deployment or ingress control to throttle traffic or
  temporarily disable the affected feature. Preserve request IDs and logs, then
  confirm the error rate falls before restoring traffic.
- **Owner:** LLM Ops on-call.

## Alert 2: Chat latency SLO breach

- **Severity / duration:** Warning; request latency P95 above 3000 ms for 10 minutes.
- **SLI:** Percentage of received requests that return successfully within 3000 ms.
- **User impact:** Responses are noticeably slower; sustained breach consumes the
  0.5% error budget.
- **First checks:** Confirm P50/P95/P99 and TTFT P95; compare latency with traffic
  and incident start time; find a slow request in logs and inspect its retrieval
  and generation spans.
- **Mitigation:** Throttle traffic at ingress and roll back a recent prompt or
  configuration change if the timing matches. Verify P95 falls below the SLO
  threshold before restoring normal traffic.
- **Owner:** LLM Ops on-call.

## Alert 3: Retrieval success degraded

- **Severity / duration:** Warning; retrieval success below 90% for 5 minutes.
- **SLI:** Successful retrieval tool calls divided by all recorded retrieval calls.
- **User impact:** Answers may lack relevant supporting documents or fail.
- **First checks:** Check retrieval success alongside chat error rate; group failed
  retrieval logs by error type; follow a failed retrieval `correlation_id` into its
  trace and inspect the retriever span.
- **Mitigation:** Roll back the latest retrieval configuration or route the
  affected feature through an approved degraded mode at ingress. Keep the mode
  visible in logs and notify the on-call owner before restoring normal traffic.
- **Owner:** Retrieval on-call.
