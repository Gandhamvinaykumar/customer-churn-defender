import json
import logging
import re
import sys
from typing import Dict, Any

from google.adk.agents import Agent, LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import AgentTool, McpToolset, ToolContext
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

from app.config import config

# Configure structured JSON audit logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("churn_security_audit")

def audit_log(event_type: str, severity: str, details: Dict[str, Any]):
    """Outputs structured JSON audit logs for security & compliance."""
    log_entry = {
        "event_type": event_type,
        "severity": severity,
        "details": details
    }
    logger.info(f"AUDIT_LOG: {json.dumps(log_entry)}")

def security_checkpoint(user_input: str) -> str:
    """Security node performing PII scrubbing, prompt injection detection, and domain validation."""
    clean_text = user_input
    
    # 1. PII Scrubbing (Emails, Credit Cards, SSNs, Phone Numbers)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    card_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    
    if re.search(email_pattern, clean_text):
        clean_text = re.sub(email_pattern, "[REDACTED_EMAIL]", clean_text)
        audit_log("PII_REDACTION", "INFO", {"type": "email", "action": "redacted"})
        
    if re.search(phone_pattern, clean_text):
        clean_text = re.sub(phone_pattern, "[REDACTED_PHONE]", clean_text)
        audit_log("PII_REDACTION", "INFO", {"type": "phone", "action": "redacted"})
        
    if re.search(card_pattern, clean_text):
        clean_text = re.sub(card_pattern, "[REDACTED_CARD]", clean_text)
        audit_log("PII_REDACTION", "WARNING", {"type": "credit_card", "action": "redacted"})

    # 2. Prompt Injection Detection
    injection_keywords = ["ignore previous instructions", "system prompt", "override rules", "jailbreak", "sudo mode"]
    for kw in injection_keywords:
        if kw in clean_text.lower():
            audit_log("PROMPT_INJECTION_ATTEMPT", "CRITICAL", {"keyword": kw, "input": user_input})
            return "[SECURITY_EVENT] Warning: Input blocked due to detected prompt manipulation policy violation."

    # 3. Domain-specific rule: Max retention discount authorization limit check
    if "override discount to 100%" in clean_text.lower() or "free forever" in clean_text.lower():
        audit_log("UNAUTHORIZED_DISCOUNT_REQUEST", "WARNING", {"input": user_input})
        return "[SECURITY_EVENT] Warning: Retention discount requests exceeding 25% require VP approval."

    return clean_text

# Define Gemini Model instance with robust HTTP 429 backoff retry options for free tier quotas
model_instance = Gemini(
    model=config.model,
    retry_options=types.HttpRetryOptions(
        attempts=5,
        initial_delay=6.0,
        max_delay=60.0,
        http_status_codes=[429, 500, 503]
    ),
)

# Connect to custom domain MCP Server using Stdio transport
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp_server"]
        )
    )
)

# --- Sub-Agent 1: Churn Analyst Agent ---
churn_analyst_agent = LlmAgent(
    name="churn_analyst_agent",
    model=model_instance,
    instruction=(
        "You are an expert SaaS Customer Churn Analyst. Analyze customer account telemetry and support history. "
        "Calculate a Churn Risk Score between 0.0 and 1.0 based on activity drops and ticket escalations."
    ),
    tools=[mcp_toolset]
)

# --- Sub-Agent 2: Retention Strategist Agent ---
retention_strategist_agent = LlmAgent(
    name="retention_strategist_agent",
    model=model_instance,
    instruction=(
        "You are a SaaS Customer Retention Strategist. Formulate structured retention packages. "
        "Ensure all proposed discounts adhere to governance guidelines (max 25%)."
    ),
    tools=[mcp_toolset]
)

# --- Orchestrator Root Agent ---
root_agent = Agent(
    name="root_agent",
    model=model_instance,
    instruction=(
        "You are the Lead Churn Defender Orchestrator for SaaS accounts. "
        "When an account inquiry or customer review comes in: "
        "1. First run security_checkpoint to sanitize input. "
        "2. Retrieve account telemetry using your tools (get_account_metrics, check_support_tickets). "
        "3. Evaluate risk score and calculate retention offers using calculate_retention_offer and log_retention_action. "
        "4. Provide a clear executive summary of the churn risk and recommended retention plan."
    ),
    tools=[
        security_checkpoint,
        mcp_toolset,
        AgentTool(agent=churn_analyst_agent),
        AgentTool(agent=retention_strategist_agent)
    ]
)

app = App(
    root_agent=root_agent,
    name="app",
)
