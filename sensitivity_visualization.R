# Day 11 - R Implementation: sensitivity_visualization.R
# This script performs interest rate sensitivity analysis and generates ggplot2 visualizations.

if (!require("tidyverse")) install.packages("tidyverse", dependencies=TRUE)
if (!require("ggplot2")) install.packages("ggplot2", dependencies=TRUE)
if (!require("scales")) install.packages("scales", dependencies=TRUE)

library(tidyverse)
library(ggplot2)
library(scales)

# 1. Generate Interest Rate Shocks (-2% to +2% in 0.2% steps)
rate_shocks <- seq(-0.02, 0.02, by = 0.002)

# Load portfolio baseline averages
# Baseline Modified Duration = 4.2031
# Baseline Convexity = 176.2455
base_dur <- 4.2031
base_conv <- 176.2455
r_base <- 0.0674 / 2 # semi-annual yield baseline

results <- data.frame(
  RateChange = rate_shocks,
  AdjDuration = numeric(length(rate_shocks)),
  AdjConvexity = numeric(length(rate_shocks))
)

# 2. Compute Adjusted Duration and Convexity for each shock
# Analytical adjustments:
# Duration decreases as rates rise, and increases as rates fall.
# AdjDuration = base_dur / (1 + RateChange/2)
# AdjConvexity = base_conv / (1 + RateChange/2)^2
for (i in 1:length(rate_shocks)) {
  dr = rate_shocks[i]
  results$AdjDuration[i]  <- base_dur / (1 + dr / 2.0)
  results$AdjConvexity[i] <- base_conv / (1 + dr / 2.0)^2
}

# Export sensitivity results to CSV for Power BI import
write.csv(results, "sensitivity_results.csv", row.names = FALSE)
message("Sensitivity results exported to: sensitivity_results.csv")

# 3. Create ggplot2 Sensitivity Chart (with dual-axis or facet)
# Since ggplot2 secondary axis requires transforming the data, we scale Convexity to fit on the same scale
scale_factor <- 40 # 176 / 40 = 4.4, which aligns with duration around 4.2
p1 <- ggplot(results, aes(x = RateChange)) +
  geom_line(aes(y = AdjDuration, color = "Adjusted Duration"), size = 1.2) +
  geom_line(aes(y = AdjConvexity / scale_factor, color = "Adjusted Convexity"), size = 1.2, linetype = "dashed") +
  geom_point(aes(y = AdjDuration, color = "Adjusted Duration"), size = 2) +
  geom_point(aes(y = AdjConvexity / scale_factor, color = "Adjusted Convexity"), size = 2) +
  scale_y_continuous(
    name = "Adjusted Duration (Years)",
    sec.axis = sec_axis(~ . * scale_factor, name = "Adjusted Convexity")
  ) +
  scale_x_continuous(labels = percent) +
  labs(
    title = "Duration & Convexity Sensitivity to Interest Rate Changes",
    subtitle = "Calculated in R using portfolio baseline risk metrics",
    x = "Interest Rate Shock (YTM Change)",
    color = "Risk Measure"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    legend.position = "bottom"
  )

# Save chart
ggsave("r_sensitivity_chart.png", plot = p1, width = 8, height = 6, dpi = 300)
message("Sensitivity plot saved to: r_sensitivity_chart.png")

# 4. Generate Mock VaR Histogram
set.seed(42)
mock_pnl <- rnorm(1000, mean = 200000, sd = 800000) # Parallel shift simulation
var_95 <- quantile(mock_pnl, 0.05)

p2 <- ggplot(data.frame(PnL = mock_pnl), aes(x = PnL / 1e6)) +
  geom_histogram(bins = 40, fill = "darkblue", color = "black", alpha = 0.7) +
  geom_vline(xintercept = var_95 / 1e6, color = "red", linetype = "dashed", size = 1.2) +
  annotate("text", x = var_95 / 1e6 - 0.4, y = 50, label = paste("95% VaR\n", round(var_95 / 1e6, 2), "M"), color = "red") +
  labs(
    title = "Portfolio P&L Monte Carlo Distribution",
    subtitle = "R-based GBM yield shock simulation (1000 runs)",
    x = "P&L (INR Millions)",
    y = "Count"
  ) +
  theme_minimal(base_size = 14) +
  theme(plot.title = element_text(face = "bold", size = 16))

# Save chart
ggsave("r_var_histogram.png", plot = p2, width = 8, height = 6, dpi = 300)
message("VaR histogram saved to: r_var_histogram.png")
