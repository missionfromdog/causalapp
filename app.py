import re
import json
import sys
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# Suppress noisy but benign warnings in visual/refutation steps
import warnings
try:
    from sklearn.exceptions import DataConversionWarning
    warnings.filterwarnings("ignore", category=DataConversionWarning)
except Exception:
    pass
warnings.filterwarnings("ignore", category=FutureWarning, module="numpy")
warnings.filterwarnings("ignore", category=FutureWarning, module="dowhy")

import requests
from io import BytesIO

try:
    from dowhy import CausalModel  # type: ignore
    DOWHY_AVAILABLE = True
    DOWHY_IMPORT_ERROR = None
except Exception as _e:
    CausalModel = None  # type: ignore
    DOWHY_AVAILABLE = False
    DOWHY_IMPORT_ERROR = _e

import networkx as nx
import plotly.express as px
from statsmodels.nonparametric.smoothers_lowess import lowess

from utils.synthetic import generate_media_marketing_data


# ---------- UI HELPERS ----------

def _header() -> None:
    st.set_page_config(page_title="Causal Media/Marketing (DoWhy)", layout="wide")
    st.title("Causal Media/Marketing App")
    st.caption(
        "Model → Identify → Estimate → Refute using DoWhy. Provide CSV, Google Sheets, or generate synthetic data."
    )


def _init_session_state() -> None:
    defaults = {
        "src": "CSV Upload",
        "gs_link": "",
        "syn_n": 5000,
        "syn_noise": 0.5,
        "syn_season": True,
        "syn_channels": ["tv", "search", "social"],
        "syn_price": True,
        "syn_seed": 123,
        "treatment": None,
        "outcome": None,
        "confounders": [],
        "results": None,
        "df": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _convert_google_sheet_to_csv_url(link: str) -> Optional[str]:
    if not link:
        return None
    m = re.search(r"docs.google.com/spreadsheets/d/([a-zA-Z0-9-_]+)", link)
    if not m:
        return None
    sheet_id = m.group(1)
    gid_match = re.search(r"gid=(\d+)", link)
    gid = gid_match.group(1) if gid_match else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def _load_data_from_source(center_ui) -> Tuple[Optional[pd.DataFrame], str]:
    source = center_ui.radio(
        "Data source",
        ["CSV Upload", "Google Sheets Link", "Synthetic Data"],
        index=["CSV Upload", "Google Sheets Link", "Synthetic Data"].index(st.session_state["src"]),
        key="src",
        horizontal=True,
    )

    if source == "CSV Upload":
        uploaded = center_ui.file_uploader("Upload CSV", type=["csv"], key="csv_upload") 
        if uploaded is None:
            return None, source
        return pd.read_csv(uploaded), source

    if source == "Google Sheets Link":
        link = center_ui.text_input("Paste Google Sheets share link", key="gs_link", placeholder="https://docs.google.com/spreadsheets/d/...")
        if not link:
            return None, source
        csv_url = _convert_google_sheet_to_csv_url(link)
        if not csv_url:
            center_ui.error("Could not parse the Google Sheets link. Paste the full URL.")
            return None, source
        try:
            with st.spinner("Loading Google Sheet as CSV (timeout 15s)..."):
                df = _fetch_csv_with_timeout(csv_url, timeout_s=15, max_retries=1)
            return df, source
        except Exception as e:
            center_ui.error(f"Failed to load sheet as CSV: {e}")
            return None, source

    # Synthetic
    n = center_ui.number_input("Rows (n)", min_value=200, max_value=200000, value=st.session_state["syn_n"], step=500, key="syn_n")
    noise = center_ui.slider("Noise scale", 0.0, 2.0, st.session_state["syn_noise"], 0.1, key="syn_noise")
    seasonality = center_ui.checkbox("Include seasonality", value=st.session_state["syn_season"], key="syn_season")
    channels = center_ui.multiselect(
        "Media channels",
        ["tv", "search", "social", "display", "email"],
        default=st.session_state["syn_channels"],
        key="syn_channels",
    )
    price_on = center_ui.checkbox("Include price as confounder", value=st.session_state["syn_price"], key="syn_price")
    seed = center_ui.number_input("Random seed", min_value=0, max_value=10_000, value=st.session_state["syn_seed"], step=1, key="syn_seed")
    if len(channels) == 0:
        center_ui.warning("Select at least one media channel")
        return None, source
    return generate_media_marketing_data(
        num_rows=int(n),
        channels=channels,
        include_seasonality=seasonality,
        include_price=price_on,
        noise_scale=float(noise),
        random_seed=int(seed),
    ), source


# ---------- DOWHY PIPELINE ----------

def _build_graph(treatment: str, outcome: str, confounders: List[str]) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_node(treatment)
    g.add_node(outcome)
    g.add_edge(treatment, outcome)
    for c in confounders:
        g.add_node(c)
        g.add_edge(c, treatment)
        g.add_edge(c, outcome)
    return g


def _run_dowhy(df: pd.DataFrame, treatment: str, outcome: str, confounders: List[str]):
    if not DOWHY_AVAILABLE:
        raise RuntimeError(f"DoWhy not available: {DOWHY_IMPORT_ERROR}")
    graph = _build_graph(treatment, outcome, confounders)
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        graph=graph,
    )

    identified = model.identify_effect()
    estimate = model.estimate_effect(
        identified,
        method_name="backdoor.linear_regression",
        confidence_intervals=True,
    )
    refute = model.refute_estimate(identified, estimate, method_name="random_common_cause")
    return graph, identified, estimate, refute, model


def _config_download_button(center_ui) -> None:
    cfg = {
        "src": st.session_state.get("src"),
        "gs_link": st.session_state.get("gs_link"),
        "syn": {
            "n": st.session_state.get("syn_n"),
            "noise": st.session_state.get("syn_noise"),
            "season": st.session_state.get("syn_season"),
            "channels": st.session_state.get("syn_channels"),
            "price": st.session_state.get("syn_price"),
            "seed": st.session_state.get("syn_seed"),
        },
        "causal": {
            "treatment": st.session_state.get("treatment"),
            "outcome": st.session_state.get("outcome"),
            "confounders": st.session_state.get("confounders", []),
        },
    }
    center_ui.download_button(
        label="Save config (JSON)",
        data=json.dumps(cfg, indent=2),
        file_name="causalapp_config.json",
        mime="application/json",
    )


def _config_upload(center_ui) -> None:
    with center_ui.expander("Load config", expanded=False):
        up = st.file_uploader("Load config (JSON)", type=["json"], key="cfg_upload")
        if up is not None:
            try:
                cfg = json.loads(up.getvalue())
                for k in ["src", "gs_link"]:
                    if k in cfg:
                        st.session_state[k] = cfg[k]
                if "syn" in cfg:
                    m = cfg["syn"]
                    for k_src, k_dst in [
                        ("n", "syn_n"),
                        ("noise", "syn_noise"),
                        ("season", "syn_season"),
                        ("channels", "syn_channels"),
                        ("price", "syn_price"),
                        ("seed", "syn_seed"),
                    ]:
                        if k_src in m:
                            st.session_state[k_dst] = m[k_src]
                if "causal" in cfg:
                    c = cfg["causal"]
                    for k in ["treatment", "outcome", "confounders"]:
                        if k in c:
                            st.session_state[k] = c[k]
                st.rerun()
            except Exception as e:
                center_ui.error(f"Invalid config: {e}")


def _get_confidence_intervals(estimate):
    """Extract confidence intervals from DoWhy estimate object."""
    try:
        # Try get_confidence_intervals method
        if hasattr(estimate, 'get_confidence_intervals'):
            ci = estimate.get_confidence_intervals()
            if ci is not None:
                if isinstance(ci, (list, tuple)) and len(ci) >= 2:
                    return (float(ci[0]), float(ci[1]))
                elif isinstance(ci, dict):
                    # Some estimators return dict with 'lower' and 'upper' keys
                    if 'lower' in ci and 'upper' in ci:
                        return (float(ci['lower']), float(ci['upper']))
        
        # Try confidence_intervals attribute
        if hasattr(estimate, 'confidence_intervals'):
            ci = estimate.confidence_intervals
            if ci is not None:
                if isinstance(ci, (list, tuple)) and len(ci) >= 2:
                    return (float(ci[0]), float(ci[1]))
                elif isinstance(ci, dict):
                    if 'lower' in ci and 'upper' in ci:
                        return (float(ci['lower']), float(ci['upper']))
        
        # Try CI as attributes directly
        if hasattr(estimate, 'ci_lower') and hasattr(estimate, 'ci_upper'):
            return (float(estimate.ci_lower), float(estimate.ci_upper))
    except Exception as e:
        # Silently fail - CIs may not be available
        pass
    return None


def _interpret_estimate(estimate_value: float, treatment: str, outcome: str, ci_lower=None, ci_upper=None) -> str:
    """Generate interpretation text for the causal estimate."""
    sign = "positive" if estimate_value > 0 else "negative"
    direction = "increase" if estimate_value > 0 else "decrease"
    
    ci_text = ""
    if ci_lower is not None and ci_upper is not None:
        ci_text = f"\n\n**Confidence Interval (95%):** [{ci_lower:.4f}, {ci_upper:.4f}]\n"
        if (ci_lower < 0 < ci_upper):
            ci_text += "⚠️ **Note:** The confidence interval includes zero, suggesting the effect may not be statistically significant."
        elif estimate_value > 0:
            ci_text += f"✅ The effect is {sign}, meaning increasing {treatment} is associated with higher {outcome}."
        else:
            ci_text += f"✅ The effect is {sign}, meaning increasing {treatment} is associated with lower {outcome}."
    
    interpretation = f"""
**What this means:**
- **Average Treatment Effect (ATE):** {estimate_value:.4f}
- This is the expected change in `{outcome}` for a one-unit increase in `{treatment}`
- A {sign} value ({estimate_value:.4f}) means that, on average, increasing `{treatment}` by 1 unit will {direction} `{outcome}` by {abs(estimate_value):.4f} units, after controlling for all confounders.

**Important assumptions:**
- The estimate assumes unconfoundedness (all relevant confounders are included)
- The relationship is assumed to be linear
- Results should be validated with refutation tests
{ci_text}
"""
    return interpretation


def _interpret_refutation(refute_str: str, original_estimate: float, refuter_type: str = "generic") -> str:
    """Extract key info from refutation result and interpret."""
    lines = refute_str.split('\n')
    new_effect = None
    p_value = None
    
    for line in lines:
        if 'New effect:' in line:
            try:
                new_effect = float(line.split(':')[-1].strip())
            except:
                pass
        if 'p value:' in line:
            try:
                p_value = float(line.split(':')[-1].strip())
            except:
                pass
    
    if new_effect is None or p_value is None:
        return "Could not parse refutation results."
    
    change_pct = abs((new_effect - original_estimate) / original_estimate * 100) if original_estimate != 0 else 0
    
    # Custom interpretations per refuter type
    if refuter_type == "random_common_cause":
        test_desc = """
**What this test does:**
- Adds a random (simulated) confounder that affects both treatment and outcome
- Checks if the estimate changes significantly when an unobserved confounder is present
- Mimics the scenario where you missed an important confounder in your model
"""
        robustness_note = "If the estimate is stable, it suggests your result is relatively robust to unobserved confounding."
    elif refuter_type == "placebo_treatment":
        test_desc = """
**What this test does:**
- Replaces the real treatment with a random/permuted "placebo" treatment
- The placebo has no causal effect on the outcome (by design)
- If you still find a significant effect, it suggests your method is picking up spurious correlations
"""
        robustness_note = "A near-zero effect and high p-value mean your original estimate is likely causal, not spurious."
    elif refuter_type == "data_subset":
        test_desc = """
**What this test does:**
- Re-estimates the effect on random subsets of your data
- Checks if the effect is consistent across different samples
- Tests stability to sampling variability
"""
        robustness_note = "Small variation across subsets suggests the estimate is stable and not driven by outliers or specific data points."
    elif refuter_type == "bootstrap":
        test_desc = """
**What this test does:**
- Resamples your data with replacement many times (bootstrap)
- Re-estimates the effect on each bootstrap sample
- Checks how much the estimate varies due to sampling uncertainty
"""
        robustness_note = "Low variance across bootstrap samples indicates a stable, reliable estimate."
    else:
        test_desc = "This test perturbs the data or model to check robustness."
        robustness_note = ""
    
    interpretation = f"""
{test_desc}

**Results:**
- **Original estimate:** {original_estimate:.4f}
- **New estimate:** {new_effect:.4f}
- **Change:** {change_pct:.1f}%
- **p-value:** {p_value:.4f}

**Interpretation:**
- **p-value > 0.05:** The difference is NOT statistically significant → estimate is robust ✅
- **p-value < 0.05:** The difference IS significant → estimate may be sensitive ⚠️
- **Small change (<20%):** Estimate is stable
- **Large change (>20%):** Estimate is sensitive; investigate further

{robustness_note}
"""
    return interpretation


def _plot_response_curves(df: pd.DataFrame, treatment: str, outcome: str, estimate_value=None, ci_lower=None, ci_upper=None):
    fig_scatter = px.scatter(df, x=treatment, y=outcome, opacity=0.3, trendline="ols")
    fig_scatter.update_layout(title=f"{treatment} vs {outcome}")

    # LOWESS smooth as a non-parametric response curve
    x = df[treatment].values
    y = df[outcome].values
    sm = lowess(y, x, frac=0.2, it=0, return_sorted=True)
    fig_lowess = px.line(x=sm[:,0], y=sm[:,1], labels={"x": treatment, "y": outcome}, title="LOWESS response curve")

    dist = px.histogram(df, x=treatment, nbins=40, title=f"Distribution of {treatment}")
    
    # Add estimate visualization with CI if available
    fig_estimate = None
    if estimate_value is not None:
        error_y_dict = None
        if ci_upper is not None and ci_lower is not None:
            error_y_dict = dict(
                type='data',
                array=[ci_upper - estimate_value],
                arrayminus=[estimate_value - ci_lower]
            )
        
        fig_estimate = px.bar(
            x=["ATE"],
            y=[estimate_value],
            error_y=error_y_dict,
            labels={"x": "", "y": "Effect on " + outcome},
            title=f"Causal Effect Estimate: {treatment} → {outcome}"
        )
        fig_estimate.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="No effect")
        fig_estimate.update_layout(showlegend=False)
    
    return fig_scatter, fig_lowess, dist, fig_estimate


def _run_refuter_with_fallbacks(model, identified, estimate, method_name: str, attempts: list):
    """Try running a refuter with several parameter sets until one works."""
    last_err = None
    for params in attempts:
        try:
            return model.refute_estimate(identified, estimate, method_name=method_name, method_params=params)
        except Exception as e:
            last_err = e
            continue
    raise last_err


# Estimator mapping for selection
ESTIMATOR_MAP = {
    "Linear regression": "backdoor.linear_regression",
    "Propensity score matching": "backdoor.propensity_score_matching",
    "Stratification": "backdoor.propensity_score_stratification",
    "IPW (inverse probability weighting)": "backdoor.propensity_score_weighting",
}


def _run_estimator(model, identified, method_name: str):
    est = model.estimate_effect(
        identified,
        method_name=method_name,
        confidence_intervals=True,
    )
    ci = _get_confidence_intervals(est)
    ci_lower = ci[0] if ci is not None else None
    ci_upper = ci[1] if ci is not None else None
    # value extraction
    value = None
    for attr in ("value", "estimate", "causal_estimate"):
        if hasattr(est, attr):
            value = getattr(est, attr)
            break
    if value is None:
        est_str = str(est)
        for line in est_str.split('\n'):
            if 'Mean value:' in line or 'ATE:' in line:
                try:
                    value = float(line.split(':')[-1].strip())
                    break
                except:
                    pass
    return est, value, ci_lower, ci_upper


def _significant(ci_lower, ci_upper) -> Optional[bool]:
    if ci_lower is None or ci_upper is None:
        return None
    return not (ci_lower <= 0 <= ci_upper)


def _run_estimators_comparison(df: pd.DataFrame, treatment: str, outcome: str, confounders: List[str], estimator_labels: List[str]):
    graph = _build_graph(treatment, outcome, confounders)
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        graph=graph,
    )
    identified = model.identify_effect()

    rows = []
    details = {}
    for label in estimator_labels:
        method = ESTIMATOR_MAP[label]
        try:
            est, value, ci_l, ci_u = _run_estimator(model, identified, method)
            # refute per estimator (random common cause)
            try:
                r = model.refute_estimate(identified, est, method_name="random_common_cause", method_params={"num_simulations": 50})
                r_str = str(r)
                # parse
                new_effect = None
                p_value = None
                for line in r_str.split('\n'):
                    if 'New effect:' in line:
                        try:
                            new_effect = float(line.split(':')[-1].strip())
                        except:
                            pass
                    if 'p value:' in line:
                        try:
                            p_value = float(line.split(':')[-1].strip())
                        except:
                            pass
                delta_pct = None
                if value is not None and new_effect is not None and value != 0:
                    delta_pct = abs((new_effect - value) / value * 100)
            except Exception as e:
                r_str = f"Refutation failed: {e}"
                new_effect = None
                p_value = None
                delta_pct = None

            rows.append({
                "Estimator": label,
                "ATE": value,
                "CI Lower": ci_l,
                "CI Upper": ci_u,
                "Significant": _significant(ci_l, ci_u),
                "Refute New": new_effect,
                "Refute p": p_value,
                "Delta %": delta_pct,
            })
            details[label] = {
                "estimate_str": str(est),
                "refute_str": r_str,
            }
        except Exception as e:
            rows.append({
                "Estimator": label,
                "ATE": None,
                "CI Lower": None,
                "CI Upper": None,
                "Significant": None,
                "Refute New": None,
                "Refute p": None,
                "Delta %": None,
                "Error": str(e),
            })
            details[label] = {"error": str(e)}

    return identified, rows, details, model, graph


def _fetch_csv_with_timeout(url: str, timeout_s: int = 15, max_retries: int = 2) -> pd.DataFrame:
    last_err = None
    headers = {"User-Agent": "causalapp/1.0"}
    for _ in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout_s)
            resp.raise_for_status()
            return pd.read_csv(BytesIO(resp.content))
        except Exception as e:
            last_err = e
            continue
    raise last_err


def main() -> None:
    _header()
    _init_session_state()

    if not DOWHY_AVAILABLE:
        st.warning(
            f"DoWhy is not installed in the current Python environment.\n\n"
            f"**Current Python:** `{sys.executable}`\n\n"
            f"Install with one of the following commands:\n\n"
            f"```bash\n"
            f"pip install 'dowhy>=0.10.0'\n"
            f"# or latest from GitHub (may be less stable):\n"
            f"pip install --upgrade 'git+https://github.com/py-why/dowhy@main'\n"
            f"```\n\n"
            f"**Import error:** {DOWHY_IMPORT_ERROR}\n\n"
            f"**Note:** Make sure Streamlit is launched using: `python -m streamlit run app.py`\n"
            f"from the same Python environment where DoWhy is installed."
        )

    setup_tab, analysis_tab, visuals_tab, refute_tab = st.tabs(["Setup", "Analysis", "Visuals", "Refutations"])

    with setup_tab:
        _config_upload(st)
        st.subheader("Data setup")
        df, _ = _load_data_from_source(st)
        if df is None:
            st.info("Provide data to continue.")
            st.stop()
        st.session_state["df"] = df

        st.dataframe(df.head(20), width="stretch")

        st.subheader("Causal setup")
        
        with st.expander("ℹ️ How to set up your causal model", expanded=False):
            st.markdown("""
            ### Understanding causal inference setup
            
            **Treatment (intervention):**
            - The variable you're interested in changing (e.g., marketing spend on TV, social media)
            - Ask: "What happens if I increase this?"
            - In media/marketing: typically a channel's spend or exposure
            
            **Outcome (dependent variable):**
            - What you want to measure the effect on (e.g., sales, conversions, revenue)
            - Ask: "What am I trying to improve or understand?"
            
            **Confounders (common causes):**
            - Variables that affect BOTH treatment and outcome
            - Create "backdoor paths" that make naive correlations misleading
            - Examples in media/marketing:
              - **Seasonality:** affects both budget allocation (more spend in Q4) and sales (holidays boost sales)
              - **Price/promotions:** affects spend decisions and sales directly
              - **Competitor activity:** may trigger more spend and also affect sales
              - **Economic indicators:** affect budget and consumer demand
            
            ### How to identify confounders:
            1. **Domain knowledge:** What factors influence both your treatment decision AND your outcome?
            2. **Timing:** Did the confounder happen before treatment? (It can't be a mediator or collider)
            3. **Causal direction:** Does it cause both T and Y, or is it caused by them?
            
            ### About the DAG (Directed Acyclic Graph):
            - **Arrows are one-directional** in causal graphs (X → Y means X causes Y)
            - **No bi-directional arrows** in standard causal graphs (that would imply feedback loops or simultaneity)
            - When you select confounders, the app creates: Confounder → Treatment, Confounder → Outcome
            - Treatment → Outcome is always assumed
            - The goal: block backdoor paths by conditioning on confounders
            
            ### What if I'm not sure?
            - Start with variables you're confident affect both (e.g., seasonality, price)
            - Use refutation tests to check robustness
            - Compare multiple estimators
            - Consider sensitivity analysis for unobserved confounders
            """)
        
        cols = list(df.columns)
        if len(cols) < 2:
            st.warning("Need at least two columns for treatment and outcome.")
            st.stop()
        if st.session_state.get("treatment") not in cols:
            st.session_state["treatment"] = cols[1 if len(cols) > 1 else 0]
        if st.session_state.get("outcome") not in cols:
            st.session_state["outcome"] = cols[0]
        safe_confounders = [c for c in st.session_state.get("confounders", []) if c in cols and c not in {st.session_state["treatment"], st.session_state["outcome"]}]
        st.session_state["confounders"] = safe_confounders

        treatment = st.selectbox(
            "Treatment (media channel)",
            cols,
            key="treatment",
            help="The variable you're changing or interested in (e.g., a media channel's spend). This is your intervention."
        )
        outcome = st.selectbox(
            "Outcome (e.g., sales)",
            cols,
            key="outcome",
            help="The variable you want to measure the effect on (e.g., sales, conversions). This is your dependent variable."
        )
        confounder_options = [c for c in cols if c not in {treatment, outcome}]
        confounders = st.multiselect(
            "Confounders (affect treatment and outcome)",
            confounder_options,
            key="confounders",
            help="Variables that affect BOTH treatment and outcome (e.g., seasonality, price, competitor activity). Including these blocks backdoor paths and helps identify the true causal effect."
        )

        st.subheader("Estimators")
        estimator_labels = list(ESTIMATOR_MAP.keys())
        selected_estimators = st.multiselect(
            "Select estimators to run",
            estimator_labels,
            default=estimator_labels,
            key="estimators_selected",
        )

        col_a, col_b = st.columns([1,1])
        with col_a:
            _config_download_button(st)
        with col_b:
            run_disabled = not DOWHY_AVAILABLE
            if st.button("Run DoWhy Analysis", disabled=run_disabled, use_container_width=True):
                with st.spinner("Running model → identify → estimate → refute ..."):
                    try:
                        # Keep single-estimator run for backward compatibility
                        graph, identified, estimate, refute, model = _run_dowhy(df, treatment, outcome, confounders)
                        # Comparison run across selected estimators
                        identified2, rows, details, model2, graph2 = _run_estimators_comparison(df, treatment, outcome, confounders, selected_estimators)
                        st.session_state["results"] = {
                            "graph": graph,
                            "identified": str(identified),
                            "estimate": str(estimate),
                            "refute": str(refute),
                            "treatment": treatment,
                            "outcome": outcome,
                            "confounders": confounders,
                            "compare_rows": rows,
                            "compare_details": details,
                        }
                        st.success("Done. See the Analysis / Visuals / Refutations tabs.")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

    with analysis_tab:
        st.subheader("Analysis")
        res = st.session_state.get("results")
        if not res:
            st.info("Run the analysis on the Setup tab to see results here.")
        else:
            # Comparison summary table
            compare_rows = res.get("compare_rows", [])
            if compare_rows:
                st.markdown("### 🧪 Estimator comparison")
                import pandas as _pd
                table_df = _pd.DataFrame(compare_rows)
                # Order columns
                cols_order = [c for c in ["Estimator","ATE","CI Lower","CI Upper","Significant","Refute New","Refute p","Delta %","Error"] if c in table_df.columns]
                table_df = table_df[cols_order]
                st.dataframe(table_df, width="stretch")
                
                with st.expander("Estimator details"):
                    details = res.get("compare_details", {})
                    for label, info in details.items():
                        st.markdown(f"**{label}**")
                        if "error" in info:
                            st.warning(info["error"])
                        else:
                            st.markdown("Estimate output")
                            st.code(info.get("estimate_str",""))
                            st.markdown("Refutation output")
                            st.code(info.get("refute_str",""))
            
            st.markdown("---")
            
            # Existing interpretation + graph and details
            # Extract estimate value for interpretation
            estimate_val = res.get("estimate_value")
            if estimate_val is None:
                # Try to extract from estimate string
                est_str = res.get("estimate", "")
                for line in est_str.split('\n'):
                    if 'Mean value:' in line:
                        try:
                            estimate_val = float(line.split(':')[-1].strip())
                            break
                        except:
                            pass
            
            ci_lower = res.get("ci_lower")
            ci_upper = res.get("ci_upper")
            
            st.markdown("### 📊 Causal Effect Estimate")
            if estimate_val is not None:
                interpretation = _interpret_estimate(
                    estimate_val, 
                    res["treatment"], 
                    res["outcome"],
                    ci_lower,
                    ci_upper
                )
                st.markdown(interpretation)
            
            if ci_lower is not None and ci_upper is not None:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ATE", f"{estimate_val:.4f}" if estimate_val else "N/A")
                with col2:
                    st.metric("CI Lower", f"{ci_lower:.4f}")
                with col3:
                    st.metric("CI Upper", f"{ci_upper:.4f}")
            
            st.markdown("---")
            
            left, right = st.columns([1, 1])
            with left:
                st.markdown("**Causal Graph**")
                st.graphviz_chart(nx.nx_pydot.to_pydot(res["graph"]).to_string())
                with st.expander("What is a causal graph?"):
                    st.markdown("""
                    A causal graph shows the relationships between variables:
                    - **Arrows (→)** indicate causal direction (e.g., Treatment → Outcome)
                    - **Confounders** affect both treatment and outcome (creates backdoor paths)
                    - **Backdoor paths** are alternative routes from treatment to outcome that must be blocked
                    """)
                
                st.markdown("**Identified estimand**")
                with st.expander("View detailed estimand", expanded=False):
                    st.code(res["identified"])
                st.caption("The estimand shows what needs to be adjusted to estimate the causal effect.")
            with right:
                st.markdown("**Estimate Details**")
                with st.expander("View full estimate output", expanded=False):
                    st.code(res["estimate"])
                    
                st.markdown("**Refutation Test**")
                if estimate_val is not None:
                    refute_interp = _interpret_refutation(res["refute"], estimate_val, "random_common_cause")
                    st.markdown(refute_interp)
                with st.expander("View raw refutation output", expanded=False):
                    st.code(res["refute"]) 
            
            st.caption("Powered by DoWhy. See docs at https://www.pywhy.org/dowhy/v0.13/")

    with visuals_tab:
        st.subheader("Visuals")
        res = st.session_state.get("results")
        df = st.session_state.get("df")
        if not res or df is None:
            st.info("Run the analysis on the Setup tab to populate visuals.")
        else:
            treatment = res["treatment"]
            outcome = res["outcome"]
            estimate_val = res.get("estimate_value")
            if estimate_val is None:
                est_str = res.get("estimate", "")
                for line in est_str.split('\n'):
                    if 'Mean value:' in line:
                        try:
                            estimate_val = float(line.split(':')[-1].strip())
                            break
                        except:
                            pass
            
            ci_lower = res.get("ci_lower")
            ci_upper = res.get("ci_upper")
            
            # Show estimate with CI at the top
            if estimate_val is not None:
                st.markdown("### 📈 Causal Effect Visualization")
                fig1, fig2, fig3, fig_estimate = _plot_response_curves(df, treatment, outcome, estimate_val, ci_lower, ci_upper)
                if fig_estimate:
                    st.plotly_chart(fig_estimate, use_container_width=True)
                    if ci_lower is not None and ci_upper is not None:
                        st.caption(f"Error bars show 95% confidence interval: [{ci_lower:.4f}, {ci_upper:.4f}]")
                st.markdown("---")
            
            st.markdown("### 📊 Data Exploration")
            fig1, fig2, fig3, _ = _plot_response_curves(df, treatment, outcome)
            st.plotly_chart(fig1, use_container_width=True)
            st.caption("Scatter plot with OLS trendline showing the relationship between treatment and outcome.")
            
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("LOWESS (Locally Weighted Scatterplot Smoothing) shows a non-parametric response curve.")
            
            st.plotly_chart(fig3, use_container_width=True)
            st.caption("Distribution of the treatment variable.")

    with refute_tab:
        st.subheader("Refutations")
        res = st.session_state.get("results")
        df = st.session_state.get("df")
        if not res or df is None:
            st.info("Run the analysis on the Setup tab to enable refutations.")
        else:
            treatment = res["treatment"]
            outcome = res["outcome"]
            confounders = res["confounders"]
            if st.button("Run extra refuters", use_container_width=True):
                graph, identified, estimate, refute, model = _run_dowhy(df, treatment, outcome, confounders)

                # get numeric estimate value for narrative
                estimate_val = None
                for attr in ("value", "estimate", "causal_estimate"):
                    if hasattr(estimate, attr):
                        estimate_val = getattr(estimate, attr)
                        break
                if estimate_val is None:
                    est_str = str(estimate)
                    for line in est_str.split('\n'):
                        if 'Mean value:' in line or 'ATE:' in line:
                            try:
                                estimate_val = float(line.split(':')[-1].strip())
                                break
                            except:
                                pass

                refuter_summary = []
                
                def run_and_display(title: str, method_name: str, refuter_type: str, method_params: dict | None = None):
                    try:
                        r = model.refute_estimate(identified, estimate, method_name=method_name, method_params=method_params or {})
                        st.markdown(f"**{title}**")
                        # Narrative
                        if estimate_val is not None:
                            interp = _interpret_refutation(str(r), estimate_val, refuter_type)
                            st.markdown(interp)
                        with st.expander("Raw output"):
                            st.code(str(r))
                        
                        # Extract for summary table
                        r_str = str(r)
                        new_effect = None
                        p_value = None
                        for line in r_str.split('\n'):
                            if 'New effect:' in line:
                                try:
                                    new_effect = float(line.split(':')[-1].strip())
                                except:
                                    pass
                            if 'p value:' in line:
                                try:
                                    p_value = float(line.split(':')[-1].strip())
                                except:
                                    pass
                        change_pct = None
                        if estimate_val is not None and new_effect is not None and estimate_val != 0:
                            change_pct = abs((new_effect - estimate_val) / estimate_val * 100)
                        
                        refuter_summary.append({
                            "Refuter": title,
                            "Original": estimate_val,
                            "New Effect": new_effect,
                            "Change %": change_pct,
                            "p-value": p_value,
                        })
                    except Exception as e:
                        st.warning(f"{title} skipped: {e}")
                        refuter_summary.append({
                            "Refuter": title,
                            "Original": estimate_val,
                            "New Effect": None,
                            "Change %": None,
                            "p-value": None,
                            "Error": str(e),
                        })

                st.markdown("### 🔍 Robustness checks")
                st.markdown("These tests perturb assumptions/data to check how stable the effect is. Each test checks a different aspect of robustness.")
                run_and_display("Random common cause", "random_common_cause", "random_common_cause", {"num_simulations": 100})
                run_and_display("Placebo treatment", "placebo_treatment_refuter", "placebo_treatment", {"placebo_type": "permute", "num_simulations": 50})
                run_and_display("Data subset", "data_subset_refuter", "data_subset", {"subset_fraction": 0.8, "num_subsets": 10})
                run_and_display("Bootstrap refuter", "bootstrap_refuter", "bootstrap", {"num_simulations": 200, "sample_size": int(len(df) * 0.8)})
                
                if refuter_summary:
                    st.markdown("---")
                    st.markdown("### 📊 Refutation summary")
                    import pandas as _pd
                    summary_df = _pd.DataFrame(refuter_summary)
                    st.dataframe(summary_df, width="stretch")


if __name__ == "__main__":
    main()
