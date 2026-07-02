# Day 11 - R Implementation: duration_convexity_analysis.R
# This script trains GBM, XGBoost, and H2O neural networks in R to predict duration and convexity.

# 1. Load required libraries
if (!require("tidyverse")) install.packages("tidyverse", dependencies=TRUE)
if (!require("caret")) install.packages("caret", dependencies=TRUE)
if (!require("xgboost")) install.packages("xgboost", dependencies=TRUE)
if (!require("Metrics")) install.packages("Metrics", dependencies=TRUE)
if (!require("h2o")) install.packages("h2o", dependencies=TRUE)

library(tidyverse)
library(caret)
library(xgboost)
library(Metrics)
library(h2o)

# 2. Load the portfolio data
message("Loading bond portfolio data...")
df <- read.csv("bond_portfolio_krd.csv")

# Clean/select feature columns
feature_cols <- c("CouponRate", "YearsToMaturity", "YieldToMaturity")
target_dur <- "ModifiedDuration"
target_conv <- "Convexity"

# Prepare dataset
df_clean <- df %>% select(all_of(c(feature_cols, target_dur, target_conv)))

# Split into 80/20 train/test
set.seed(42)
train_idx <- createDataPartition(df_clean$ModifiedDuration, p = 0.8, list = FALSE)
train_set <- df_clean[train_idx, ]
test_set  <- df_clean[-train_idx, ]

# 3. Train GBM Model (via caret) for Duration
message("Training GBM model for Duration...")
fit_control <- trainControl(method = "cv", number = 5)
gbm_dur_model <- train(
  ModifiedDuration ~ CouponRate + YearsToMaturity + YieldToMaturity,
  data = train_set,
  method = "gbm",
  trControl = fit_control,
  verbose = FALSE
)

# Predict & Evaluate
pred_gbm_dur <- predict(gbm_dur_model, test_set)
rmse_gbm_dur <- rmse(test_set$ModifiedDuration, pred_gbm_dur)
message(paste("GBM Duration Test RMSE:", round(rmse_gbm_dur, 6)))

# 4. Train XGBoost Model for Convexity
message("Training XGBoost model for Convexity...")
train_x <- as.matrix(train_set[, feature_cols])
train_y <- train_set[[target_conv]]
test_x  <- as.matrix(test_set[, feature_cols])
test_y  <- test_set[[target_conv]]

xgb_conv_model <- xgboost(
  data = train_x,
  label = train_y,
  max_depth = 4,
  eta = 0.1,
  nrounds = 100,
  objective = "reg:squarederror",
  verbose = 0
)

# Predict & Evaluate
pred_xgb_conv <- predict(xgb_conv_model, test_x)
rmse_xgb_conv <- rmse(test_y, pred_xgb_conv)
message(paste("XGBoost Convexity Test RMSE:", round(rmse_xgb_conv, 6)))

# 5. Train H2O Neural Network for Duration & Convexity
message("Initializing H2O cluster...")
h2o.init(nthreads = -1) # Use all CPU cores

# Convert to H2O Frame
train_h2o <- as.h2o(train_set)
test_h2o  <- as.h2o(test_set)

message("Training H2O Deep Learning Model for Duration...")
h2o_nn_dur <- h2o.deeplearning(
  x = feature_cols,
  y = target_dur,
  training_frame = train_h2o,
  activation = "RectifierWithDropout",
  hidden = c(128, 64, 32),
  epochs = 50,
  seed = 42
)

# Predict & Evaluate
pred_nn_dur <- as.vector(h2o.predict(h2o_nn_dur, test_h2o))
rmse_nn_dur <- rmse(test_set$ModifiedDuration, pred_nn_dur)
message(paste("H2O Neural Network Duration Test RMSE:", round(rmse_nn_dur, 6)))

# Save locally
saveRDS(gbm_dur_model, "gbm_dur_model.rds")
saveRDS(xgb_conv_model, "xgb_conv_model.rds")
h2o.saveModel(h2o_nn_dur, path = getwd(), force = TRUE)

message("R Model training completed and models saved.")
h2o.shutdown(prompt = FALSE)
