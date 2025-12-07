# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-07

### Added
- Initial release of Causal Media/Marketing App
- DoWhy-based causal inference pipeline (Model → Identify → Estimate → Refute)
- Multiple data source support:
  - CSV file upload
  - Google Sheets integration
  - Synthetic data generator
- Four estimation methods:
  - Linear regression (backdoor)
  - Propensity score matching
  - Propensity score stratification
  - Inverse probability weighting (IPW)
- Comprehensive refutation tests:
  - Random common cause
  - Placebo treatment
  - Data subset validation
  - Bootstrap resampling
- Interactive visualizations:
  - Causal graphs (DAG)
  - Response curves (OLS and LOWESS)
  - Treatment effect plots with confidence intervals
  - Distribution histograms
- Estimator comparison table
- Educational features:
  - Contextual help for causal concepts
  - Result interpretation guidance
  - Detailed tooltips
- Configuration save/load functionality
- Streamlit-based web interface

### Technical Details
- Python 3.11+ support
- Streamlit 1.39+
- DoWhy 0.10+
- Plotly interactive charts
- NetworkX for graph operations

### Known Limitations
- Requires Python < 3.13 (DoWhy compatibility)
- Linear relationships assumed for regression estimators
- Single treatment/single outcome analysis
- No time-series or lagged effects support

## [Unreleased]

### Planned Features
- Time-series and lagged effects support
- Instrumental variables estimation
- Regression discontinuity design
- Heterogeneous treatment effects analysis
- Multi-treatment/multi-outcome support
- Automated confounder detection
- Export functionality for publication-ready outputs
- Database integration
- API support for programmatic access
- Enhanced sensitivity analysis tools

