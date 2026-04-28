import numpy as np
import pandas as pd

np.random.seed(42)

# -----------------------------
# CONFIGURATION
# -----------------------------

N_COMPANIES = 1000
N_CONTRACTS = 5000
AVG_CONTRACT_MONTHS = 6

INDUSTRIES = ["tech", "finance", "healthcare", "retail", "manufacturing"]
REGIONS = ["NA", "EU", "APAC"]
PLAN_TIERS = ["Basic", "Professional", "Enterprise"]

PRICE_MAP = {
    "Basic": 25,
    "Professional": 60,
    "Enterprise": 120
}

# -----------------------------
# 1 GENERATE LATENT VARIABLES
# -----------------------------

latent = pd.DataFrame({
    "company_id": np.arange(N_COMPANIES),
    "product_fit": np.random.normal(0, 1, N_COMPANIES),
    "customer_success_quality": np.random.normal(0, 1, N_COMPANIES),
    "sales_process_maturity": np.random.normal(0, 1, N_COMPANIES),
    "budget_pressure": np.random.normal(0, 1, N_COMPANIES)
})

# -----------------------------
# 2 GENERATE COMPANIES
# -----------------------------

companies = pd.DataFrame({
    "company_id": np.arange(N_COMPANIES),
    "company_size": np.random.lognormal(mean=5, sigma=1, size=N_COMPANIES).astype(int),
    "industry": np.random.choice(INDUSTRIES, N_COMPANIES),
    "region": np.random.choice(REGIONS, N_COMPANIES),
    "growth_rate": np.random.normal(0.1, 0.05, N_COMPANIES)
})

companies["annual_revenue"] = (
    companies["company_size"] *
    np.random.normal(120000, 30000, N_COMPANIES)
)

companies = companies.merge(
    latent[["company_id", "sales_process_maturity"]],
    on="company_id"
)

companies["crm_maturity_score"] = (
    1 / (1 + np.exp(-(0.5 * companies["sales_process_maturity"]
                      + np.random.normal(0, 0.5, N_COMPANIES))))
)

# -----------------------------
# 3 GENERATE CONTRACTS
# -----------------------------

contracts = pd.DataFrame({
    "contract_id": np.arange(N_CONTRACTS),
    "company_id": np.random.choice(companies["company_id"], N_CONTRACTS)
})

contracts = contracts.merge(companies, on="company_id")

contracts["seats_start"] = (
    np.random.poisson(0.12 * contracts["company_size"]) + 5
)

contracts["plan_tier"] = np.random.choice(
    PLAN_TIERS,
    N_CONTRACTS,
    p=[0.5, 0.35, 0.15]
)

contracts["price_per_seat"] = contracts["plan_tier"].map(PRICE_MAP)

contracts["discount_pct"] = np.random.beta(2, 8, N_CONTRACTS)

contracts["contract_value"] = (
    contracts["seats_start"]
    * contracts["price_per_seat"]
    * (1 - contracts["discount_pct"])
)

contracts["duration_months"] = (
    np.random.poisson(AVG_CONTRACT_MONTHS, N_CONTRACTS) + 1
)

# -----------------------------
# 4 GENERATE MONTHLY USAGE
# -----------------------------

usage_rows = []

for _, row in contracts.iterrows():
    for m in range(row["duration_months"]):
        usage_rows.append({
            "contract_id": row["contract_id"],
            "company_id": row["company_id"],
            "month_index": m,
            "seats_start": row["seats_start"]
        })

usage = pd.DataFrame(usage_rows)

usage = usage.merge(latent, on="company_id")

usage["active_users"] = (
    usage["seats_start"]
    * (1 / (1 + np.exp(-(1.2 * usage["product_fit"]))))
).astype(int)

usage["logins_total"] = (
    usage["active_users"]
    * np.random.poisson(8, len(usage))
)

usage["leads_created"] = (
    usage["active_users"]
    * np.random.poisson(2, len(usage))
)

usage["opportunities_created"] = (
    usage["leads_created"]
    * np.random.uniform(0.3, 0.7, len(usage))
).astype(int)

usage["reports_generated"] = (
    usage["active_users"]
    * np.random.poisson(1, len(usage))
)

usage["feature_adoption_score"] = (
    1 / (1 + np.exp(-(usage["product_fit"])))
)

# -----------------------------
# 5 GENERATE SUPPORT TICKETS
# -----------------------------

tickets = usage[[
    "contract_id",
    "company_id",
    "month_index",
    "logins_total",
    "customer_success_quality"
]].copy()

tickets["ticket_count"] = np.random.poisson(
    0.03 * tickets["logins_total"]
)

tickets["avg_resolution_hours"] = (
    np.random.normal(12, 2, len(tickets))
    - 4 * tickets["customer_success_quality"]
)

tickets["csat_score"] = (
    3.5
    + 0.6 * tickets["customer_success_quality"]
    - 0.02 * tickets["ticket_count"]
    + np.random.normal(0, 0.3, len(tickets))
)

tickets["escalation_count"] = (
    tickets["ticket_count"]
    * np.random.uniform(0.05, 0.15, len(tickets))
).astype(int)

# Introduce missing CSAT values
mask = np.random.rand(len(tickets)) < 0.2
tickets.loc[mask, "csat_score"] = np.nan

# -----------------------------
# 6 GENERATE RENEWAL OUTCOMES
# -----------------------------

usage_summary = usage.groupby("contract_id").agg({
    "logins_total": "mean",
    "active_users": "mean"
}).reset_index()

renewals = contracts[["contract_id", "seats_start"]].merge(
    usage_summary,
    on="contract_id"
)

logit = (
    0.8 * renewals["logins_total"] / 100
    + 0.6 * renewals["active_users"] / 10
    - 0.5 * np.random.rand(len(renewals))
)

renewal_prob = 1 / (1 + np.exp(-logit))

renewals["renewed"] = np.random.binomial(1, renewal_prob)

renewals["seat_change"] = (
    renewals["seats_start"]
    * np.random.uniform(-0.2, 0.5, len(renewals))
).astype(int)

# -----------------------------
# 7 REMOVE LATENT VARIABLES
# -----------------------------

companies = companies.drop(columns=["sales_process_maturity"])

usage = usage.drop(columns=[
    "product_fit",
    "customer_success_quality",
    "sales_process_maturity",
    "budget_pressure"
])

tickets = tickets.drop(columns=["customer_success_quality"])

# -----------------------------
# 8 FINAL TABLE FORMATTING
# -----------------------------

usage_monthly = usage[[
    "contract_id",
    "month_index",
    "logins_total",
    "active_users",
    "leads_created",
    "opportunities_created",
    "reports_generated",
    "feature_adoption_score"
]]

support_tickets_monthly = tickets[[
    "contract_id",
    "month_index",
    "ticket_count",
    "avg_resolution_hours",
    "csat_score",
    "escalation_count"
]]

# -----------------------------
# 9 EXPORT DATASETS
# -----------------------------

companies.to_csv("dataset/companies.csv", index=False)
contracts.to_csv("dataset/contracts.csv", index=False)
usage_monthly.to_csv("dataset/usage_monthly.csv", index=False)
support_tickets_monthly.to_csv("dataset/support_tickets_monthly.csv", index=False)
renewals.to_csv("dataset/renewals.csv", index=False)

print("Synthetic dataset generation complete.")
print("Files exported:")
print(" - companies.csv")
print(" - contracts.csv")
print(" - usage_monthly.csv")
print(" - support_tickets_monthly.csv")
print(" - renewals.csv")