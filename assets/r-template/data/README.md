# Data directory

The first run of `R/run_example.R` creates three simulated CSVs and their dictionary using the configured seed. Later runs validate and reuse the saved inputs. Day-28 rows in the distribution table must match the same group and replicate in the trend table. For an incomplete set, recover the listed CSVs from the same revision. To try a new simulation seed, start a separate scaffold.

Use an explicit import and cleaning script for research data. Preserve raw inputs, units, group names, sample identifiers, missing-value rules, transformations and exclusions. Adapt the simulation-specific validation, plot labels and caption to the study.
