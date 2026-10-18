# ADR-001: Production inference architecture

- **Date:** 2026-10-17
- **Status:** Proposed
- **Decision:** AWS WAF → CloudFront → ALB → Proxy Lambda → SageMaker Real-time Endpoint
- **Region for cost comparison:** eu-west-1
- **Scope:** Proposed production design; not deployed by this repository

## Decision

Use CloudFront, ALB, and a Proxy Lambda for the public API, with SageMaker for model inference. This separates company-specific API requirements from model serving and deployment.

![architect-schema.png](../../architect-schema.png)

## Assumptions

| Item | Planning input |
| --- | --- |
| Ongoing development | Assume the model and API will evolve separately. |
| Reference traffic | La Centrale quotation service · 200K–300K requests/day · uneven, bursty arrivals |
| Observed peak minute | 1,123 requests · 18.7 requests/second averaged over that minute, not an instantaneous peak |
| To validate | Production traffic · model latency · memory · concurrency · latency and availability targets · cost |

## Why this architecture

- **Separate API and model responsibilities:** Manage API contracts, logging, response and error formats, GLC authentication, and headers such as `X-Client-Source` separately from model inference and releases.
- **Model management:** Track model versions and approvals with Model Registry, and configure gradual rollout and alarm-based rollback with SageMaker deployment guardrails.
- **Independent scaling:** Configure API concurrency and model capacity separately.
- **Trade-offs:** Continuous endpoint cost, an extra service call, and deployment configuration.

## Options

- **Lambda / ECS Fargate:** Packaging the model with the app couples their releases; using S3 requires configuring model updates and rollback. Lambda also loads the model on cold starts, which can delay responses.
- **Proxy Lambda + SageMaker — selected:** Provides dedicated model serving and deployment features, but adds continuous endpoint costs and an extra service call.

### Cost calculation

Planning estimate in USD: eu-west-1 · 6–9M requests/month (`N`) · On-Demand · 730 hours · Linux/x86. Rates checked on 2026-10-18.

| Option | Monthly calculation | Estimate |
| --- | --- | --- |
| Lambda + in-process model | `N × (1 GB × 0.1 s × $0.0000166667/GB-s + $0.20/1M requests)` | $11.20–$16.80 |
| ECS Fargate + in-process model | `2 tasks × 730 h × (1 vCPU × $0.04048/vCPU-h + 2 GB × $0.004445/GB-h)` | $72.08 |
| Proxy Lambda + SageMaker | `730 h × $0.128/h` for one `ml.m5.large` endpoint + `N × (0.25 GB × 0.02 s × $0.0000166667/GB-s + $0.20/1M requests)` for the proxy | $95.14–$95.99 |

Lambda durations are assumptions, not measurements. Instance counts are cost scenarios, not validated capacity or availability settings.

Excludes WAF, CloudFront, ALB, free tier, discounts, CloudWatch, NAT, VPC endpoints, storage, data transfer, and temporary extra capacity during deployment. Sources: [Lambda pricing](https://aws.amazon.com/lambda/pricing/) · [Fargate eu-west-1 rates](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/eu-west-1/index.json) · [SageMaker eu-west-1 rates](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSageMaker/current/eu-west-1/index.json).

Exact cost requires measured latency, memory, instance size, autoscaling policy, and network configuration.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| AWS WAF | Blocks suspicious requests · limits excessive traffic |
| CloudFront | Connects the public API domain · terminates HTTPS · forwards requests to the ALB |
| ALB | Applies GLC shared authentication (ALB helper) · routes requests to the Proxy Lambda |
| Proxy Lambda | Validates the API contract · adds a request ID · invokes SageMaker · maps errors |
| SageMaker endpoint | Loads the approved model · runs inference · returns the prediction and model release ID |
| S3 + Model Registry | Stores artifacts · evaluation results · approval status · release history; CI/CD updates or rolls back the endpoint |
| CloudWatch, alarms | Tracks latency · errors · capacity · deployment health |

## Consequences

- API and compatible model releases can proceed independently.
- SageMaker endpoint capacity creates continuous cost.
- Deployment guardrails, autoscaling, alarms, and IaC must be configured before production.

