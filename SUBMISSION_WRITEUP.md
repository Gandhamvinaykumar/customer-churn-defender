# Submission Write-Up — Customer Churn Defender Agent

## 1. Problem Statement
In B2B SaaS businesses, enterprise customer churn represents millions of dollars in lost ARR annually. Account management teams struggle to detect subtle usage drop-offs, unresolved support ticket friction, and declining sentiment early enough to intervene. Manual account audits are time-consuming and often lead to reactive, unstandardized retention discounts that erode margin without policy compliance.

`customer-churn-defender` solves this by orchestrating autonomous AI agents that proactively monitor account telemetry, evaluate churn probability, formulate policy-compliant retention offers, and enforce rigorous enterprise security controls.

## 2. Solution Architecture
The application leverages Google ADK 2.0 with a multi-agent hierarchy:

```
                  +-------------------------------+
                  |      User Request / Input     |
                  +-------------------------------+
                                  |
                                  v
                  +-------------------------------+
                  |     security_checkpoint       |
                  |  (PII Scrubbing & Guardrails) |
                  +-------------------------------+
                                  |
                                  v
                  +-------------------------------+
                  |    root_agent Orchestrator    |
                  +-------------------------------+
                    /                           \
       (AgentTool) /                             \ (AgentTool)
                  v                               v
    +---------------------------+   +---------------------------+
    |   churn_analyst_agent     |   | retention_strategist_agent|
    | (Telemetry & Risk Evaluation)| |(Offer Packaging & Governance)|
    +---------------------------+   +---------------------------+
                  \                               /
                   +--------------+--------------+
                                  | (Stdio MCP)
                                  v
                  +-------------------------------+
                  |       Domain MCP Server       |
                  | (Metrics, Tickets, CRM Logs)  |
                  +-------------------------------+
```

## 3. Core Concepts Used
* **ADK Multi-Agent Orchestration**: `root_agent` delegates tasks to specialized sub-agents (`churn_analyst_agent` and `retention_strategist_agent`) using `AgentTool` definitions in [app/agent.py](file:///c:/Users/vv033/OneDrive/Attachments/adk-workspace/customer-churn-defender/app/agent.py).
* **Model Context Protocol (MCP)**: Custom stdio-based MCP server in [app/mcp_server.py](file:///c:/Users/vv033/OneDrive/Attachments/adk-workspace/customer-churn-defender/app/mcp_server.py) exposing 4 domain tools connected via ADK's `McpToolset`.
* **Security Checkpoint**: Embedded input validation node (`security_checkpoint`) performing real-time regex sanitization and threat detection.
* **Agents CLI & Universal Config**: Managed via `google-agents-cli` tooling with decoupled configuration in [app/config.py](file:///c:/Users/vv033/OneDrive/Attachments/adk-workspace/customer-churn-defender/app/config.py).

## 4. Security Design
* **PII Redaction**: Automatic scrubbing of customer email addresses, phone numbers, and payment cards prior to LLM processing.
* **Prompt Injection Defense**: Keyword evaluation blocking adversarial system overrides and prompt leaks.
* **Structured Audit Logging**: Every security event generates structured JSON logs (`AUDIT_LOG`) with severity ratings (`INFO`, `WARNING`, `CRITICAL`) for SIEM compliance.
* **Policy Authorization Limit**: Enforces a strict 25% cap on autonomous retention discounts, routing higher discount requests to human executives.

## 5. MCP Server Design
The domain MCP server exposes 4 tailored tools:
1. `get_account_metrics`: Fetches login drops, active user shifts, and MRR.
2. `check_support_tickets`: Inspects unresolved ticket sentiment and escalation count.
3. `calculate_retention_offer`: Computes allowable discounts and bonus perks based on risk tiers.
4. `log_retention_action`: Audits final retention plans directly to the CRM system.

## 6. HITL (Human-in-the-Loop) Flow
High-value accounts (MRR > $10,000) or high-risk retention plans generate structured summaries in the playground UI for Account Executive review and manual sign-off before executing CRM log actions.

## 7. Demo Walkthrough
Refer to the sample test queries detailed in [README.md](file:///c:/Users/vv033/OneDrive/Attachments/adk-workspace/customer-churn-defender/README.md) demonstrating standard account analysis, automatic PII redaction, and prompt injection defense.

## 8. Business Impact & Value
`customer-churn-defender` transforms customer success operations from reactive firefighting to automated, intelligent retention. Teams save hours of manual data aggregation per account while protecting gross margins through strict governance guardrails.
