import json
import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("churn_mcp_server")

mcp = FastMCP("Customer Churn Defender MCP")

# Mock database records
MOCK_ACCOUNTS = {
    "ACC-1001": {
        "company_name": "Acme Corp",
        "subscription_tier": "Enterprise",
        "monthly_recurring_revenue": 5000.00,
        "active_users_drop_pct": 35.0,
        "support_tickets_30d": 8,
        "nps_score": 4,
        "last_login_days_ago": 12
    },
    "ACC-2002": {
        "company_name": "TechStart Inc",
        "subscription_tier": "Pro",
        "monthly_recurring_revenue": 1200.00,
        "active_users_drop_pct": 5.0,
        "support_tickets_30d": 1,
        "nps_score": 9,
        "last_login_days_ago": 1
    },
    "ACC-3003": {
        "company_name": "Global Logistics",
        "subscription_tier": "Enterprise",
        "monthly_recurring_revenue": 12000.00,
        "active_users_drop_pct": 50.0,
        "support_tickets_30d": 14,
        "nps_score": 2,
        "last_login_days_ago": 18
    }
}

@mcp.tool()
def get_account_metrics(account_id: str) -> str:
    """Retrieves account usage metrics, login frequency, and activity drops for an account ID."""
    logger.info(f"Fetching metrics for account {account_id}")
    account = MOCK_ACCOUNTS.get(account_id.upper())
    if not account:
        return json.dumps({
            "account_id": account_id,
            "status": "not_found",
            "message": "Account ID not found in telemetry database. Returning baseline metrics.",
            "active_users_drop_pct": 20.0,
            "support_tickets_30d": 4,
            "nps_score": 6
        })
    return json.dumps({"account_id": account_id.upper(), **account})

@mcp.tool()
def check_support_tickets(account_id: str) -> str:
    """Fetches recent support ticket summaries and unresolved sentiment indicators."""
    logger.info(f"Checking support tickets for {account_id}")
    tickets = [
        {"ticket_id": "T-901", "subject": "Billing issue with renewal", "sentiment": "Negative", "status": "Open"},
        {"ticket_id": "T-844", "subject": "API latency degradation", "sentiment": "Frustrated", "status": "Escalated"}
    ]
    return json.dumps({"account_id": account_id, "ticket_count": len(tickets), "tickets": tickets})

@mcp.tool()
def calculate_retention_offer(monthly_recurring_revenue: float, risk_score: float) -> str:
    """Calculates max approved discount, free add-on modules, and retention contract terms."""
    logger.info(f"Calculating retention offer for MRR={monthly_recurring_revenue}, Risk={risk_score}")
    if risk_score > 0.7:
        max_discount_pct = 25.0
        bonus_features = ["Dedicated CSM", "Free API Throughput Boost", "Quarterly Executive Review"]
    elif risk_score > 0.4:
        max_discount_pct = 15.0
        bonus_features = ["Free API Throughput Boost"]
    else:
        max_discount_pct = 5.0
        bonus_features = []
        
    recommended_discount_value = monthly_recurring_revenue * (max_discount_pct / 100.0)
    return json.dumps({
        "mrr": monthly_recurring_revenue,
        "risk_score": risk_score,
        "max_discount_pct": max_discount_pct,
        "monthly_savings": recommended_discount_value,
        "bonus_features": bonus_features
    })

@mcp.tool()
def log_retention_action(account_id: str, risk_level: str, proposed_action: str) -> str:
    """Logs the churn mitigation plan to the CRM audit log and alerts the account owner."""
    logger.info(f"Logging action for {account_id}: Risk={risk_level}")
    return json.dumps({
        "status": "success",
        "account_id": account_id,
        "logged_at": "2026-06-29T11:40:00Z",
        "crm_record_created": True,
        "notification_sent_to_csm": True
    })

if __name__ == "__main__":
    mcp.run()
