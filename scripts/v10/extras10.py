SRC = "Dhanush N, 'Forward Deployed Engineer: The Ultimate Roadmap'"
TRACK = dict(id="backend", name="Backend & Software Foundations", icon="backend",
  role="The software craft every AI role stands on: Python and TypeScript, data structures, Git and Linux, debugging, API styles, PostgreSQL and document stores, identity (OAuth2, OIDC, SAML, RBAC/ABAC), caching and queues, webhooks, API design and resilience. Day to day: build and harden the services, integrations and data paths that agents call.")
LEVELS = [("b-l1", "L1 Foundations", ["b-python", "b-dsa", "b-cli", "b-debug"]),
          ("b-l2", "L2 Practitioner", ["b-apis", "b-postgres", "b-docstore"]),
          ("b-l3", "L3 Advanced", ["b-auth", "b-async", "b-webhooks"]),
          ("b-l4", "L4 Expert", ["b-apidesign", "b-resilience"])]
ARCH_PLACEMENT = {"a-l2": ["a-discovery"], "a-l3": ["a-pilot", "a-entint"], "a-l4": ["a-adoption", "a-roi"]}
ROLE_ADD = {
 "fde": ["b-python", "b-cli", "b-debug", "b-apis", "b-postgres", "b-auth", "b-webhooks", "b-resilience", "a-discovery", "a-pilot", "a-entint", "a-adoption", "a-roi"],
 "ai-engineer": ["b-python", "b-dsa", "b-cli", "b-debug", "b-apis", "b-postgres", "b-auth", "b-async", "b-webhooks", "b-apidesign", "b-resilience"],
 "data-eng": ["b-python", "b-dsa", "b-cli", "b-postgres", "b-docstore", "b-async", "b-webhooks"],
 "solutions-architect": ["a-discovery", "a-pilot", "a-entint", "a-roi"],
 "product": ["a-discovery", "a-adoption", "a-roi"],
}
FDE_CAPSTONE_TEXT = "Ship an AI support assistant into an existing product: SSO, a ticketing integration, evals and an ROI report (see the Backend & Software Foundations capstone)."
UNIVERSAL_INSERT = [  # inserted after the shared-core steps
 ["backend", "b-python", "Python and TypeScript for AI engineers"], ["backend", "b-dsa", "Data structures and algorithms that matter"],
 ["backend", "b-cli", "Git, Linux and the command line"], ["backend", "b-debug", "Debugging systematically"],
 ["backend", "b-apis", "REST vs GraphQL vs gRPC"], ["backend", "b-postgres", "PostgreSQL, indexing, transactions and pgvector"],
 ["backend", "b-docstore", "MongoDB and document stores"], ["backend", "b-auth", "OAuth2, OIDC, SAML SSO, RBAC and ABAC"],
 ["backend", "b-async", "Caching, queues and background jobs"], ["backend", "b-webhooks", "Webhooks and event-driven integration"],
 ["backend", "b-apidesign", "API design and versioning"], ["backend", "b-resilience", "Rate limits, retries, timeouts and idempotency"]]
UNIVERSAL_FDE_AFTER = "a-fde"
UNIVERSAL_FDE = [["architect", "a-discovery", "Discovery, requirements and SOW scoping"], ["architect", "a-pilot", "Pilot to production: security, residency, procurement"],
 ["architect", "a-entint", "Enterprise integration: SSO, VPN/on-prem, SAP, Salesforce, ServiceNow"], ["architect", "a-adoption", "Change management and adoption"],
 ["architect", "a-roi", "Measuring business impact and ROI"]]
PATH = dict(id="fde-dhanush", title="Forward Deployed Engineer (Dhanush N roadmap)", untimed=True, emoji="🚀",
  who="Untimed path following Dhanush N's 'Forward Deployed Engineer: The Ultimate Roadmap', in its 11 sections. Each step maps a roadmap section to an Atlas lesson. The path ends with the FDE capstone.",
  steps=[["backend", "b-python", "1 Programming fundamentals: Python, TypeScript, APIs"], ["backend", "b-dsa", "1 Programming fundamentals: data structures and algorithms"],
   ["backend", "b-cli", "1 Programming fundamentals: Git and Linux"], ["backend", "b-debug", "1 Programming fundamentals: debugging"],
   ["backend", "b-apis", "2 Backend: REST and GraphQL"], ["backend", "b-postgres", "2 Backend: PostgreSQL"], ["backend", "b-docstore", "2 Backend: MongoDB"],
   ["backend", "b-auth", "2 Backend: authentication and authorization"], ["backend", "b-async", "2 Backend: caching, queues, background jobs"], ["backend", "b-apidesign", "2 Backend: API design"],
   ["shared", "sc-llm", "3 AI/LLM fundamentals"], ["engineer", "e-api", "4 AI app development: calling models"], ["engineer", "e-rag", "4 AI app development: RAG"],
   ["engineer", "e-tools", "4 AI app development: tool calling"], ["engineer", "e-agents", "4 AI app development: agents"],
   ["infra", "f-cloud", "5 Cloud and infrastructure"], ["infra", "f-k8s", "5 Cloud and infrastructure: containers and Kubernetes"],
   ["data", "d-model", "6 Data engineering: SQL modeling"], ["data", "d-found", "6 Data engineering: ETL/ELT"], ["data", "d-quality", "6 Data engineering: validation"],
   ["backend", "b-webhooks", "6 Data engineering: webhooks and event-driven"], ["data", "d-connect", "6 Data engineering: data access"],
   ["backend", "b-resilience", "7 Security and reliability: rate limiting, retries, timeouts"], ["trust", "t-cloudsec", "7 Security and reliability: cloud security"],
   ["architect", "a-fde", "8 Customer and product understanding: the FDE model"], ["architect", "a-discovery", "8 Customer understanding: discovery and SOW"],
   ["architect", "a-pilot", "9 Deployment: pilot to production"], ["architect", "a-entint", "9 Deployment: enterprise integration"], ["engineer", "e-prod", "9 Production operations"],
   ["trust", "t-evalfound", "10 Evals"], ["architect", "a-adoption", "8 Customer understanding: adoption and stakeholder communication"], ["architect", "a-roi", "8 Customer understanding: business impact"], ["capstone", "backend", "11 Real-world project: the FDE capstone"]])
CAPSTONE = dict(title="FDE Capstone: Ship an AI Support Assistant into an Existing Product",
  goal="Embed an AI support assistant in an existing web product the way a forward deployed engineer would: discovery to SOW, SSO, ticketing integration, evals, production gate and an ROI report.",
  architecture="Existing product (any open-source helpdesk or a mock SaaS app) + assistant service (FastAPI or TypeScript) with RAG over the help center, tools for ticket lookup, creation and work notes (ServiceNow developer instance, Zendesk or Jira Service Management sandbox), Postgres with pgvector for chunks and conversation state, and a webhook receiver for ticket events.",
  infra="Containerized services on a small Kubernetes cluster or a PaaS. Managed Postgres, Redis for cache and queue, and a model gateway (LiteLLM or similar) with budgets and fallbacks.",
  deploy="Feature-flagged rollout inside the existing UI (side panel), staged waves with a 10% holdout, and rollback by flag. Infrastructure as code plus CI that runs unit tests, snippet checks and the eval gate.",
  security="OIDC or SAML SSO against a test IdP (Keycloak or an Okta developer tenant) with SCIM, least-privilege integration user for the ticketing system, delegated tokens for tool calls, HMAC-verified webhooks, prompt-injection tests on retrieved content, and a data-flow diagram plus completed CAIQ-style questionnaire.",
  observability="Traces per conversation and tool call (OpenTelemetry), dashboards for deflection, handle time, CSAT proxy, cost per resolved ticket, queue depth and webhook failures, with alerts on SLO burn.",
  scaling="Queue-backed ingestion and triage jobs, cached embeddings, rate limiting per tenant and an estimate of replicas and token spend at 10× ticket volume.",
  cost="Token and infrastructure cost per resolved ticket against the baseline cost per ticket, with payback and a sensitivity table.",
  deliverables=["Discovery notes and a two-page SOW with baseline metrics and acceptance criteria", "Integration map (SSO, ticketing, data, network paths, scopes)", "Running assistant inside the product, behind a feature flag", "Eval report (golden set of at least 150 real-shaped tickets, judge calibration) and CI gate", "Production readiness pack: data-flow diagram, questionnaire, runbook, rollback", "ROI report from the holdout: effect with confidence interval, TCO, payback, guardrails"])
GLOSSARY = [("SOW (statement of work)", "Contract document defining an engagement's objectives, scope, exclusions, deliverables, dependencies, acceptance criteria and change control."),
 ("SAML", "XML-based SSO standard where an identity provider sends a signed assertion about the user to a service provider."),
 ("OIDC", "OpenID Connect: an identity layer on OAuth 2.0 that issues signed ID tokens (JWTs) for login."),
 ("SCIM", "System for Cross-domain Identity Management: a protocol an IdP uses to create, update and deactivate users and groups in apps."),
 ("RBAC", "Role-based access control: users get roles, and roles grant permissions."),
 ("ABAC", "Attribute-based access control: policies evaluate attributes of the user, resource and context."),
 ("Webhook", "An HTTP callback a system sends to your endpoint when an event happens."),
 ("Dead-letter queue", "Queue that receives messages which repeatedly failed processing, so they can be inspected without blocking the main queue."),
 ("Token bucket", "Rate-limiting algorithm: tokens refill at a steady rate up to a capacity, allowing bursts while bounding the average rate."),
 ("Exponential backoff with jitter", "Retry strategy with growing, randomized delays that prevents synchronized retry storms."),
 ("Cursor pagination", "Paging through results with an opaque pointer to the last item, which stays stable as data changes."),
 ("Problem details (RFC 9457)", "Standard JSON format for HTTP API errors with type, title, status and detail."),
 ("ADKAR", "Prosci's individual change model: Awareness, Desire, Knowledge, Ability, Reinforcement."),
 ("Holdout group", "Users or items deliberately kept without a change so its effect can be measured against them."),
 ("Data residency", "Requirement that data, and often its processing, stays within a specified jurisdiction."),
 ("Outbound connector", "Agent installed inside a private network that dials out to a cloud service, avoiding inbound firewall openings.")]
AUDIT = [ # (topic, regex)
 ("Python for AI engineering", r"\bpython\b"), ("TypeScript", r"typescript"), ("Data structures and algorithms (DSA)", r"data structures? and algorithms|\bdsa\b|big-o|topological sort"),
 ("Git workflows (bisect, revert, branching)", r"git bisect|git revert|\bgit\b"), ("Linux / CLI", r"\blinux\b|command line|bash"),
 ("Debugging methodology", r"debugg"), ("REST APIs", r"\brest\b"), ("GraphQL", r"graphql"), ("gRPC", r"\bgrpc\b"),
 ("PostgreSQL", r"postgres"), ("MongoDB / document stores", r"mongodb|document stores?"), ("Database indexing and transactions", r"index(es|ing)?\b.*transaction|transaction isolation|explain analyze"),
 ("OAuth2 / OIDC", r"oauth|openid connect|\boidc\b"), ("SAML SSO", r"\bsaml\b"), ("RBAC / ABAC", r"\brbac\b|\babac\b"),
 ("Caching", r"cach(e|ing)"), ("Queues and background jobs", r"background jobs?|dead-letter|job queue"), ("Webhooks", r"webhook"),
 ("Event-driven integration", r"event-driven|cloudevents|event bus"), ("API design and versioning", r"api versioning|dated version|openapi|cursor pagination"),
 ("Rate limiting", r"rate limit"), ("Retries, timeouts, backoff", r"backoff|retr(y|ies).*timeout|timeouts?"), ("Idempotency", r"idempoten"),
 ("Discovery and requirements", r"discovery|requirements"), ("Statement of work (SOW) scoping", r"statement of work|\bsow\b"),
 ("Pilot to production (security review, procurement)", r"security review|procurement|pilot to production|pilot-to-production"),
 ("Data residency", r"residency"), ("Enterprise integration: SAP / Salesforce / ServiceNow", r"\bsap\b|salesforce|servicenow"),
 ("VPN / on-prem connectivity", r"\bvpn\b|on-prem"), ("Change management and adoption", r"change management|adoption|adkar"),
 ("Stakeholder communication", r"stakeholder"), ("Business impact / ROI baseline", r"\broi\b|baseline|payback"), ("Evals for FDE deliverables", r"\bevals?\b"),
 ("Real-world FDE capstone project", r"capstone")]
