# Cardiac rehabilitation after AMI and 1-year readmission
# Demo analysis script for the "Writing with AI" WS (2026-05-13)
#
# Note for workshop participants:
#   This script is a DEMO. The data file does not exist in the repository.
#   The goal is for the AI to read this code and derive the Methods text from it.
#   Do not try to run it.

library(dplyr)
library(gtsummary)
library(epitools)


# 1. Load data ----------------------------------------------------------------

d <- read.csv("data/cohort.csv")

# Apply eligibility (age >= 65, discharged alive, non-missing exposure/outcome)
d <- d %>%
  filter(age >= 65,
         discharged_alive == 1,
         !is.na(cr_participation),
         !is.na(readmission_1y))

d <- d %>%
  mutate(
    cr      = factor(cr_participation, levels = c(0, 1), labels = c("No CR", "CR")),
    outcome = factor(readmission_1y,   levels = c(0, 1), labels = c("No", "Yes"))
  )


# 2. Table 1: baseline characteristics by exposure ----------------------------
# Continuous variables: mean (SD)  ※ median (IQR) は使わない
# Categorical variables: n (%)

table1 <- d %>%
  select(cr, age, sex, diabetes) %>%
  tbl_summary(
    by = cr,
    statistic = list(all_continuous() ~ "{mean} ({sd})"),
    digits = all_continuous() ~ 1
  ) %>%
  add_overall()

print(table1)


# 3. 2x2 table and unadjusted risk ratio (RR, 95% CI) -------------------------

tab <- table(d$cr, d$outcome)
print(tab)

rr <- riskratio(tab)        # epitools: row1 = unexposed, col1 = no outcome
print(rr$measure)           # rows: exposure; columns: estimate, lower, upper


# 4. Logistic regression (adjusted) -------------------------------------------
# Outcome ~ exposure + age + sex + diabetes
# Report OR with 95% CI.

fit <- glm(
  readmission_1y ~ cr + age + sex + diabetes,
  data = d,
  family = binomial
)

or_ci <- exp(cbind(OR = coef(fit), confint(fit)))
print(or_ci)

tbl_reg <- tbl_regression(fit, exponentiate = TRUE)
print(tbl_reg)
