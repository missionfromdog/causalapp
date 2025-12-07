# 📊 Causal Media/Marketing App

> **A Streamlit web application for causal inference in media and marketing using DoWhy**

Perform rigorous causal effect estimation on your marketing data to understand the true impact of your media channels on sales and conversions. This tool helps you move beyond correlations to identify actual causal relationships using state-of-the-art causal inference methods.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-red.svg)](https://streamlit.io)
[![DoWhy](https://img.shields.io/badge/DoWhy-0.10+-green.svg)](https://github.com/py-why/dowhy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Features

### 🔬 **Causal Inference Pipeline**
- **Model**: Define causal relationships with directed acyclic graphs (DAGs)
- **Identify**: Automatically identify causal estimands using backdoor adjustment
- **Estimate**: Multiple estimation methods:
  - Linear regression (backdoor)
  - Propensity score matching
  - Stratification
  - Inverse probability weighting (IPW)
- **Refute**: Robustness checks with multiple refutation tests

### 📈 **Data Sources**
- **CSV Upload**: Drag and drop your own data files
- **Google Sheets**: Direct integration with shared Google Sheets links
- **Synthetic Data Generator**: Built-in generator for testing and learning
  - Customizable media channels (TV, search, social, display, email)
  - Realistic confounders (seasonality, price)
  - Adjustable noise levels and sample sizes

### 📊 **Visualizations**
- Interactive causal graphs showing variable relationships
- Response curves (linear and non-parametric LOWESS)
- Treatment effect estimates with confidence intervals
- Distribution plots for exploratory data analysis

### 🔍 **Robustness Testing**
- Random common cause refutation
- Placebo treatment tests
- Data subset validation
- Bootstrap resampling
- Sensitivity analysis across multiple estimators

### 💡 **Educational Features**
- Contextual help explaining causal concepts
- Interpretation guides for all results
- Interactive parameter selection with tooltips
- Save/load analysis configurations

---

## 🚀 Quick Start

### Prerequisites

**Important**: DoWhy currently requires Python < 3.13. We recommend **Python 3.11** or 3.12.

### Installation

#### Option 1: Using pyenv (Recommended for macOS)

```bash
# Install pyenv if you haven't already
brew install pyenv

# Install Python 3.11
pyenv install 3.11.9 -s
pyenv local 3.11.9

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

#### Option 2: Using conda

```bash
# Create conda environment with Python 3.11
conda create -n causalapp python=3.11 -y
conda activate causalapp

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

#### Option 3: Using standard venv

```bash
# Ensure you have Python 3.11 or 3.12
python3 --version

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 📖 Usage Guide

### 1. **Setup Tab: Load Your Data**

Choose from three data source options:

- **CSV Upload**: Upload your marketing data file
- **Google Sheets**: Paste a shareable link (must be set to "Anyone with link can view")
- **Synthetic Data**: Generate sample data for testing

**Data requirements:**
- At least 2 columns (treatment and outcome)
- Numeric values for analysis columns
- Recommended: 200+ rows for reliable estimates

### 2. **Define Your Causal Model**

Select your variables:

- **Treatment**: The variable you're manipulating (e.g., marketing spend on a channel)
- **Outcome**: What you're measuring (e.g., sales, conversions)
- **Confounders**: Variables that affect both treatment and outcome (e.g., seasonality, price)

**Example scenario:**
```
Treatment: tv_spend
Outcome: sales
Confounders: [seasonality, price]
```

This setup answers: *"What is the causal effect of TV advertising on sales, controlling for seasonal patterns and pricing?"*

### 3. **Select Estimation Methods**

Choose one or more estimators to compare:
- **Linear Regression**: Fast, interpretable, assumes linear relationships
- **Propensity Score Matching**: Matches treated/untreated units with similar characteristics
- **Stratification**: Divides data into strata based on propensity scores
- **IPW**: Weights observations by inverse probability of treatment

### 4. **Run Analysis**

Click "Run DoWhy Analysis" to:
1. Build the causal graph
2. Identify the causal estimand
3. Estimate treatment effects
4. Run initial robustness checks

### 5. **Interpret Results**

Navigate through the tabs:

- **Analysis Tab**: 
  - Estimator comparison table
  - Causal effect interpretation
  - Confidence intervals
  - Statistical significance tests

- **Visuals Tab**:
  - Treatment effect visualization with error bars
  - Scatter plots with trendlines
  - Non-parametric response curves
  - Distribution histograms

- **Refutations Tab**:
  - Run additional robustness tests
  - Validate assumptions
  - Check sensitivity to unmeasured confounding

### 6. **Save Your Analysis**

- Download configuration as JSON for reproducibility
- Load previous configurations to continue analysis
- Export results for reporting

---

## 🧪 Example: Marketing Mix Analysis

```python
# Sample synthetic data generation
Data includes:
  - Channels: TV, Search, Social media spending
  - Confounders: Seasonality (weekly patterns), Price
  - Outcome: Sales

Causal question: "Does increasing social media spend cause higher sales?"

Model setup:
  Treatment: social
  Outcome: sales
  Confounders: [seasonality, price]

Results interpretation:
  ATE = 0.8431
  → A $1 increase in social spend causes a $0.84 increase in sales
  → After controlling for seasonality and price effects
  → With 95% CI: [0.75, 0.93]
```

---

## 🔧 Technical Details

### Architecture

```
causalapp/
├── app.py                  # Main Streamlit application
├── utils/
│   └── synthetic.py        # Synthetic data generator
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Key Dependencies

- **Streamlit**: Web application framework
- **DoWhy**: Causal inference library (Microsoft Research)
- **NetworkX**: Graph manipulation for DAGs
- **Plotly**: Interactive visualizations
- **Pandas/NumPy**: Data manipulation
- **Scikit-learn**: Machine learning utilities
- **Statsmodels**: Statistical modeling

### Causal Inference Methods

The app implements the **DoWhy framework**:

1. **Model**: Create a causal graph representing variable relationships
2. **Identify**: Use graph theory to find identifying equations (backdoor adjustment)
3. **Estimate**: Apply statistical/ML methods to estimate causal effects
4. **Refute**: Test robustness with sensitivity analysis

**Assumptions**:
- **Unconfoundedness**: All relevant confounders are measured and included
- **Positivity**: All units have non-zero probability of receiving treatment
- **SUTVA**: No interference between units, treatment is well-defined
- **Correct model specification**: Relationships are correctly modeled

---

## 📚 Understanding Causal Inference

### Why Not Just Use Correlation?

**Problem**: Correlation ≠ Causation

Example: You might observe that higher TV spend correlates with higher sales. But:
- Maybe you spend more on TV during holiday seasons (when sales are naturally higher)
- Maybe you increase TV spend when prices are lower (which also boosts sales)
- The correlation might be driven by these **confounders**, not by TV's causal effect

### The Solution: Causal Inference

Causal inference methods help you:
1. **Identify confounders**: Variables affecting both treatment and outcome
2. **Block backdoor paths**: Control for confounders to isolate the true effect
3. **Estimate causal effects**: Measure the impact of changing treatment, holding everything else constant
4. **Test robustness**: Validate that your estimates are reliable

### Key Concepts

**Treatment (T)**: Variable you can control/manipulate (e.g., ad spend)

**Outcome (Y)**: Variable you want to affect (e.g., sales)

**Confounder (C)**: Variable affecting both T and Y, creating bias
```
C → T → Y
↓       ↑
└───────┘
```

**Causal Effect**: The change in Y caused by changing T, holding confounders constant

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Support for time-series data and lagged effects
- [ ] Additional estimation methods (instrumental variables, regression discontinuity)
- [ ] Export functionality for publication-ready tables/figures
- [ ] Automated confounder detection/suggestion
- [ ] Integration with more data sources (databases, APIs)
- [ ] Heterogeneous treatment effects analysis
- [ ] Multi-treatment/multi-outcome support

### Development Setup

```bash
# Clone the repository
git clone https://github.com/missionfromdog/causalapp.git
cd causalapp

# Create development environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if you add them)
pytest tests/

# Run the app
streamlit run app.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[DoWhy](https://github.com/py-why/dowhy)**: Microsoft Research's causal inference library
- **[PyWhy](https://www.pywhy.org/)**: Community for causal inference in Python
- **[Streamlit](https://streamlit.io/)**: Framework for data apps
- Judea Pearl's work on causal inference and graphical models
- Miguel Hernán and James Robins' "Causal Inference: What If" book

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/missionfromdog/causalapp/issues)
- **GitHub**: [github.com/missionfromdog/causalapp](https://github.com/missionfromdog/causalapp)
- **LinkedIn**: [Your LinkedIn Profile]
- **Email**: Casey Hess

---

## 📊 Resources for Learning Causal Inference

### Books
- Pearl, J., Glymour, M., & Jewell, N. P. (2016). *Causal inference in statistics: A primer*
- Hernán, M. A., & Robins, J. M. (2020). *Causal Inference: What If* (free online)
- Cunningham, S. (2021). *Causal Inference: The Mixtape* (free online)

### Online Resources
- [DoWhy Documentation](https://www.pywhy.org/dowhy/)
- [Causal Inference for the Brave and True](https://matheusfacure.github.io/python-causality-handbook/)
- [Brady Neal's Causal Inference Course](https://www.bradyneal.com/causal-inference-course)

### Papers
- Sharma, A., & Kiciman, E. (2020). DoWhy: An End-to-End Library for Causal Inference. *arXiv preprint*

---

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version: 1.0.0**
- Initial release with core causal inference functionality
- Support for multiple data sources
- Four estimation methods
- Comprehensive refutation tests
- Interactive visualizations

---

## 🐛 Troubleshooting

### Common Issues

**Google Sheets not loading:**
- Ensure the sheet is set to "Anyone with the link can view"
- Check that you're pasting the full URL from the address bar
- The app automatically converts sheet URLs to CSV export format

**DoWhy import errors:**
- Verify Python version is 3.11 or 3.12 (not 3.13+)
- Ensure virtual environment is activated
- Try reinstalling: `pip install --upgrade dowhy`

**"No module named 'utils'":**
- Make sure you're running from the project root directory
- Verify `utils/synthetic.py` exists

**Estimation fails:**
- Check for missing values in your data
- Ensure treatment and outcome are numeric
- Verify you have enough observations (200+ recommended)
- Try different estimation methods

**Refutation tests timeout:**
- Reduce `num_simulations` parameters
- Use smaller datasets for testing
- Some refuters may not work with certain estimators

---

## 🎓 Use Cases

This tool is useful for:

### Marketing & Advertising
- Measuring ROI of different marketing channels
- Attribution modeling
- Budget allocation optimization
- A/B test analysis with confounders

### Business Analytics
- Pricing impact analysis
- Promotion effectiveness
- Customer behavior analysis
- Product launch impact

### Research & Education
- Teaching causal inference concepts
- Validating research hypotheses
- Sensitivity analysis
- Methods comparison

---

**Built with ❤️ using Python, Streamlit, and DoWhy**

*Star ⭐ this repo if you find it useful!*
