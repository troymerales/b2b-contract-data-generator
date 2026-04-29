# SCHEMA AND DATA DICTIONARY

## Table 1 - companies

| feature_name | type | description |
| --- | --- | --- |
| company_id | INTEGER (UNIQUE) | Unique identifier for each company customer |
| industry | TEXT | Industry sector of the company (e.g., technology, finance, healthcare, retail) |
| region | TEXT | Geographic region where the company operates (e.g., NA, EU, APAC) |
| company_size | INTEGER | Number of employees in the company |
| annual_revenue | NUMERIC | Estimated annual company revenue in USD |
| growth_rate | NUMERIC | Annual revenue growth rate of the company |
| crm_maturity_score | NUMERIC | Score representing how mature the company’s CRM processes are (higher values indicate more structured sales processes) |

Expected rows: 30 companies

## Table 2 - contracts

| feature_name | type | description |
| --- | --- | --- |
| contract_id | INTEGER (UNIQUE) | Unique identifier for each contract |
| company_id | INTEGER (FOREIGN KEY) | Identifier linking the contract to the company |
| start_date | DATE | Contract start date |
| end_date | DATE | Contract end date |
| seats_start | INTEGER | Number of CRM seats/licenses purchased at the start of the contract |
| seats_end | INTEGER | Number of seats at the end of the contract period (captures expansion or contraction) |
| contract_value | NUMERIC | Total monetary value of the contract during the contract period |
| plan_tier | TEXT | Product tier purchased by the company (e.g., Basic, Professional, Enterprise) |
| discount_pct | NUMERIC | Percentage discount applied to the contract price |
| sales_channel | TEXT | Sales acquisition channel (e.g., direct sales, partner, self-serve) |

Expected rows: 500 contracts

## Table 3 - usage_monthly

| feature_name | type | description |
| --- | --- | --- |
| usage_id | INTEGER | Unique identifier for each usage record |
| contract_id | INTEGER (FOREIGN KEY) | Identifier linking the usage record to a contract |
| month | DATE | Month for which the usage metrics were recorded |
| logins_total | INTEGER | Total number of user login events during the month |
| active_users | INTEGER | Number of distinct users actively using the platform during the month |
| leads_created | INTEGER | Number of sales leads created in the CRM during the month |
| opportunities_created | INTEGER | Number of sales opportunities tracked in the CRM |
| reports_generated | INTEGER | Number of reports generated from the CRM system |
| feature_adoption_score | NUMERIC | Composite score measuring adoption of advanced CRM features |

Expected rows: 2000 rows

## Table 4 - support_tickets_monthly

| feature_name | type | description |
| --- | --- | --- |
| ticket_month_id | INTEGER | Unique identifier for each monthly support record |
| contract_id | INTEGER (FOREIGN KEY) | Identifier linking support records to the contract |
| month | DATE | Month of support activity |
| ticket_count | INTEGER | Number of support tickets submitted by the customer during the month |
| avg_resolution_hours | NUMERIC | Average time (in hours) required to resolve support tickets |
| csat_score | NUMERIC | Customer satisfaction score after support interactions (typically on a 1–5 scale) |
| escalation_count | INTEGER | Number of tickets escalated to higher-level technical support |

Note: CSAT scores may be missing if customers do not submit feedback.

## Table 5 - renewals

| feature_name | type | description |
| --- | --- | --- |
| contract_id | INTEGER (FOREIGN KEY) | Identifier of the contract being evaluated for renewal |
| renewed | BOOLEAN | Indicator of whether the contract was renewed or churned |
| renewal_date | DATE | Date when the renewal decision was recorded |
| seat_change | INTEGER | Change in seat count at renewal |

## Total Feature Summary

| table | Number of features |
| --- | --- |
| companies | 7 |
| contracts | 10 |
| usage_monthly | 9 |
| support_tickets_monthly | 7 |
| renewals | 4 |

Total features across tables: 37

# LATENT VARIABLES AND STRUCTURAL MODEL

## Latent Variables

| variable | distribution | description |
| --- | --- | --- |
| product_fit | Normal(0,1) | Measures how well the CRM product fits the company’s workflow and needs |
| customer_success_quality | Normal(0,1) | Quality of account management and customer support provided to the client |
| sales_process_maturity | Normal(0,1) | Internal maturity of the company's sales process and CRM adoption |
| budget_pressure | Normal(0,1) | Financial pressure influencing cost sensitivity and renewal decisions |

## Key Relationships (Conceptual Model)

## Structural Equations (Core Model)

### Company Generation

- 1.1. Company size
- 1.2. Revenue
- 1.3. CRM maturity
- where

### Contract Generation

- 2.1. Seats purchased
- 2.2. Contract value

### Monthly Usage Generation

- 3.1. Active Users
- 3.2. Logins
- 3.3. Leads created

### Support Tickets

- 4.1. Ticket count
- 4.2. Resolution time
- 4.3. CSAT score

### Renewal Probability (Target Variable)

- 5.1. Logistic renewal model
- 5.2. Renewal outcome

## Sampling Order

- Generate companies
- Generate latent variables
- Generate contracts
- Generate monthly usage
- Generate support tickets
- Compute renewal probability
- Sample renewal outcome
- Remove latent variables
- Export tables
