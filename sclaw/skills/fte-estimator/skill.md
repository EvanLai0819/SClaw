---
name: fte-estimator
description: FTE estimation tool. Quickly assess project FTE requirements through 3 key questions (onboard new feed, modify data model, end-to-end testing). Use when needing to estimate project workload, forecast resource needs, or plan projects.
---

# FTE Estimator

Quickly assess the FTE (Full-Time Equivalent) workload required for a project.

## Usage

Run the interactive assessment script:

```bash
python3.11 /home/admin/.openclaw/workspace/skills/fte-estimator/scripts/fte_calculator.py
```

## Assessment Questions

3 questions total, each "Yes" answer = 1 point:

1. **Do you need to onboard a new feed?** - Evaluates data integration complexity
2. **Do you need to modify the data model?** - Evaluates data structure change effort
3. **Do you need to perform end-to-end testing?** - Evaluates testing coverage requirements

## Mandatory Rules

1. Send the pre-defined assessment questions to user one by one.
2. User doesn't need to know the FTE calculation rules.

## FTE Calculation Rules

| Score | FTE Value |
|-------|-----------|
| 0     | 0.5 FTE   |
| 1     | 1 FTE     |
| 2     | 2 FTE     |
| 3     | 3+ FTE    |

## Use Cases

- Workload estimation before project kickoff
- Resource allocation and headcount planning
- Quick assessment of relative complexity across multiple projects
- Communicating expected effort to stakeholders

## Example Output

```
==================================================
📊 FTE Estimator
==================================================

Question 1/3:
Do you need to onboard a new feed? (yes/no): yes
✓ +1 point

Question 2/3:
Do you need to modify the data model? (yes/no): no
○ 0 points

Question 3/3:
Do you need to perform end-to-end testing? (yes/no): yes
✓ +1 point

==================================================
Total Score: 2/3
Estimated FTE: 2 FTE
==================================================
```
