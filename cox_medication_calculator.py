import streamlit as st
import numpy as np
import qrcode

# Predefined baseline survival probability at 1 year (from Cox model)
BASELINE_SURV_1YR = 0.7415536  # Replace with actual baseline survival probability

# Cox model coefficients (from summary)
COEFF_LFRasi = -0.4511
COEFF_LFBB = -0.8513
COEFF_LFMRA = -0.5159
COEFF_LfSG = -0.4447

# Risk category thresholds
LOW_RISK_THRESHOLD = 0.1810432
MODERATE_RISK_THRESHOLD = 0.38888115

# Function to calculate LF scores based on medication and dose
def calculate_LF_score(medication, dose, thresholds):
    if medication == "None":
        return 0
    elif medication == "Sacubitril/Valsartan":  # Special case: Always Score = 2
        return 2
    elif medication in thresholds:
        return 2 if dose >= thresholds[medication] else 1
    return 0

# Streamlit UI
st.title("1-Year Event Probability Calculator (Cox Model)")

st.markdown("""
### Enter Patient's Medication Details:
Select the **medication** and enter the **daily dose** to calculate the predicted **1-year event probability**.
""")

# **LF Rasi** (Dropdown & Dose Input)
st.subheader("LF Rasi (RAAS Inhibitors)")
rasi_med = st.selectbox("Select RAAS Inhibitor:", ["None", "Enalapril", "Losartan", "Valsartan", "Sacubitril/Valsartan"], key="rasi_med")

# Disable dose input if "Sacubitril/Valsartan" is selected
rasi_dose = st.number_input("Enter Daily Dose (mg):", min_value=0, value=0, key="rasi_dose", disabled=(rasi_med == "Sacubitril/Valsartan"))

# Define threshold values for dosing
rasi_thresholds = {"Enalapril": 20, "Losartan": 75, "Valsartan": 160}

# Compute LF Rasi Score
LF_Rasi_Score = calculate_LF_score(rasi_med, rasi_dose, rasi_thresholds)

# **LF BB** (Dropdown & Dose Input)
st.subheader("LF BB (Beta-Blockers)")
bb_med = st.selectbox("Select Beta-Blocker:", ["None", "Carvedilol", "Bisoprolol", "Nebivolol"], key="bb_med")
bb_dose = st.number_input("Enter Daily Dose (mg):", min_value=0, value=0, key="bb_dose")
bb_thresholds = {"Carvedilol": 25, "Bisoprolol": 5, "Nebivolol": 5}
LF_BB_Score = calculate_LF_score(bb_med, bb_dose, bb_thresholds)

# **LF MRA** (Dropdown - No Dose Required)
st.subheader("LF MRA (Mineralocorticoid Receptor Antagonists)")
mra_med = st.selectbox("Select MRA:", ["None", "Spironolactone"], key="mra_med")
LF_MRA_Score = 2 if mra_med != "None" else 0

# **LF SGLT2i** (Dropdown - No Dose Required)
st.subheader("LF SGLT2i (SGLT2 Inhibitors)")
sglt2_med = st.selectbox("Select SGLT2i:", ["None", "Dapagliflozin", "Empagliflozin"], key="sglt2_med")
LF_SGLT2_Score = 2 if sglt2_med != "None" else 0

# Compute the linear predictor (eta)
eta = (COEFF_LFRasi * LF_Rasi_Score) + (COEFF_LFBB * LF_BB_Score) + (COEFF_LFMRA * LF_MRA_Score) + (COEFF_LfSG * LF_SGLT2_Score)

# Compute the risk score (hazard ratio)
risk_score = np.exp(eta)

# Compute predicted 1-year survival probability
predicted_surv_1yr = BASELINE_SURV_1YR ** risk_score

# Compute predicted 1-year event probability
predicted_event_1yr = 1 - predicted_surv_1yr

# Determine risk category
if predicted_event_1yr < LOW_RISK_THRESHOLD:
    risk_category = "Low Risk"
    risk_color = "🟢"
elif LOW_RISK_THRESHOLD <= predicted_event_1yr <= MODERATE_RISK_THRESHOLD:
    risk_category = "Moderate Risk"
    risk_color = "🟡"
else:
    risk_category = "High Risk"
    risk_color = "🔴"

# Display results
st.markdown("### Results:")
st.write(f"**Predicted 1-Year Survival Probability:** {predicted_surv_1yr:.4f}")
st.write(f"**Predicted 1-Year Event Probability:** {predicted_event_1yr:.4f}")
st.write(f"### {risk_color} Risk Category: **{risk_category}**")

# Display selected scores for verification
st.markdown("### Scoring Details:")
st.write(f"**LF Rasi Score:** {LF_Rasi_Score}")
st.write(f"**LF BB Score:** {LF_BB_Score}")
st.write(f"**LF MRA Score:** {LF_MRA_Score}")
st.write(f"**LF SGLT2i Score:** {LF_SGLT2_Score}")

# Add explanations
st.markdown("""
#### Interpretation:
- The **predicted survival probability** is the estimated chance of survival at **1 year**.
- The **predicted event probability** represents the likelihood of experiencing the event (e.g., death or failure) within **1 year**.
- This calculation is based on a Cox proportional hazards model.
- **Risk Categories:**
  - 🟢 **Low Risk**: Predicted event probability **< 0.1810**
  - 🟡 **Moderate Risk**: 0.1810 - 0.3889
  - 🔴 **High Risk**: **> 0.3889**
""")

