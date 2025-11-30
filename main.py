import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

# ==========================================
# 核心逻辑类 (原 cycle_model.py 内容)
# ==========================================
class CycleModel:
    """
    Handles the logic for menstrual cycle tracking, prediction, and risk assessment.
    Core requirement: 4-phase model, non-medical, rule-based.
    """

    def __init__(self, age: int):
        self.age = age
        self.min_cycle_days = 21
        self.max_cycle_days = 40
        # Age-based thresholds
        self._adjust_thresholds_by_age()

    def _adjust_thresholds_by_age(self):
        """
        Adjusts strictness based on age groups defined in the prompt.
        """
        if self.age < 18:
            # Teenage: irregular is common
            self.irregularity_tolerance_days = 5
        elif 18 <= self.age <= 35:
            # Typical reproductive: strict
            self.irregularity_tolerance_days = 3
        elif 36 <= self.age <= 45:
            # Late reproductive
            self.irregularity_tolerance_days = 4
        else:
            # Perimenopause: very unpredictable
            self.irregularity_tolerance_days = 7

    def analyze_history(self, dates: list, typical_length: int = 28):
        """
        Analyzes a list of period start dates.
        Returns a dictionary with stats (avg, std, history_count).
        """
        if not dates:
            return {
                "avg_length": typical_length,
                "std_dev": 0.0,
                "count": 0,
                "lengths": []
            }

        # Sort dates to be sure
        dates = sorted([d for d in dates if d is not None])
        
        # Calculate cycle lengths (diff between consecutive starts)
        lengths = []
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i-1]).days
            if 15 < delta < 100: # Filter out obvious data entry errors (e.g. typos)
                lengths.append(delta)

        if not lengths:
            # If we have dates but no intervals (e.g. only 1 date), use fallback
            return {
                "avg_length": typical_length,
                "std_dev": 0.0,
                "count": len(dates),
                "lengths": []
            }

        avg_len = np.mean(lengths)
        std_dev = np.std(lengths) if len(lengths) > 1 else 0.0

        return {
            "avg_length": float(avg_len),
            "std_dev": float(std_dev),
            "count": len(dates),
            "lengths": lengths,
            "last_date": dates[-1]
        }

    def predict_phases(self, last_period_date: datetime.date, avg_length: float):
        """
        Determines current phase and predicts next dates based on the 4-phase model.
        Phase rules (scaled to avg_length if needed, but fixed for simplicity as requested):
        - Menstrual: 1-5
        - Follicular: 6-13
        - Ovulation: 14-15
        - Luteal: 16-End
        """
        if not last_period_date:
            return None

        today = datetime.now().date()
        days_since_last = (today - last_period_date).days
        current_cycle_day = days_since_last + 1
        
        # Round avg_length for calculations
        cycle_len = int(round(avg_length))
        
        # Determine Phase
        phase = "Unknown"
        if 1 <= current_cycle_day <= 5:
            phase = "Menstrual Phase"
        elif 6 <= current_cycle_day <= 13:
            phase = "Follicular Phase"
        elif 14 <= current_cycle_day <= 15:
            phase = "Ovulation Phase"
        elif 16 <= current_cycle_day <= cycle_len:
            phase = "Luteal Phase"
        elif current_cycle_day > cycle_len:
            phase = "Late / Delayed"
        else:
            phase = "Future date selected?"

        # Predictions
        next_period_start = last_period_date + timedelta(days=cycle_len)
        
        # Ovulation estimation: Usually 14 days before the NEXT period
        # Est. Ovulation Day = Cycle Length - 14
        ovulation_day_index = cycle_len - 14
        ovulation_date = last_period_date + timedelta(days=ovulation_day_index)
        
        return {
            "current_day": current_cycle_day,
            "current_phase": phase,
            "next_period_start": next_period_start,
            "est_ovulation_date": ovulation_date,
            "days_since_last": days_since_last
        }

    def calculate_regularity_score(self, stats: dict):
        """
        Calculates a simple 0-100 score.
        """
        score = 80 # Baseline
        lengths = stats.get("lengths", [])
        std_dev = stats.get("std_dev", 0)

        if not lengths:
            return 80, "Insufficient Data"

        # Penalty for high standard deviation
        # If std is higher than tolerance, subtract points
        if std_dev > self.irregularity_tolerance_days:
            excess = std_dev - self.irregularity_tolerance_days
            score -= (excess * 5) # Steep penalty

        # Penalty for very short or very long cycles
        short_cycles = sum(1 for l in lengths if l < self.min_cycle_days)
        long_cycles = sum(1 for l in lengths if l > self.max_cycle_days)
        
        score -= (short_cycles * 10)
        score -= (long_cycles * 10)

        # Clamp score
        score = max(0, min(100, int(score)))

        # Label
        if score >= 80:
            label = "Relatively Regular"
        elif 50 <= score < 80:
            label = "Moderate Variability"
        else:
            label = "High Variability"

        return score, label

    def generate_hints(self, stats: dict, prediction: dict):
        """
        Generates safe, conservative text hints.
        """
        hints = []
        lengths = stats.get("lengths", [])
        
        # 1. Long cycles warning
        long_cycles = sum(1 for l in lengths if l > self.max_cycle_days)
        if long_cycles >= 2:
            hints.append(f"⚠️ You have recorded {long_cycles} cycles longer than {self.max_cycle_days} days. This can be normal, but worth monitoring.")

        # 2. Short cycles warning
        short_cycles = sum(1 for l in lengths if l < self.min_cycle_days)
        if short_cycles >= 2:
            hints.append(f"⚠️ You have recorded {short_cycles} cycles shorter than {self.min_cycle_days} days.")

        # 3. Missed period warning (90 days rule)
        if prediction:
            days_since = prediction["days_since_last"]
            if days_since > 90:
                hints.append("❗ It has been over 90 days since your last recorded period. If this is unexpected, please consider consulting a doctor or taking a pregnancy test.")

        # 4. Age specific context
        if self.age < 18:
            hints.append("ℹ️ At your age (under 18), cycle variability is often normal as your body adjusts.")
        elif self.age > 45:
            hints.append("ℹ️ At your age (45+), changes in cycle length may be related to perimenopause.")

        return hints


# ==========================================
# 界面与交互代码 (原 main.py 内容)
# ==========================================

# --- Configuration & Setup ---
st.set_page_config(
    page_title="CycleTracker AI",
    page_icon="🌸",
    layout="wide"
)

# --- Helper Functions ---
def local_css():
    st.markdown("""
    <style>
    .phase-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        text-align: center;
        margin-bottom: 20px;
    }
    .warning-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #ffecd1;
        border-left: 5px solid #ff9800;
        color: #663c00;
        margin-bottom: 10px;
    }
    .disclaimer {
        font-size: 0.8em;
        color: #666;
        border-top: 1px solid #ddd;
        padding-top: 10px;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Main App ---
def main():
    local_css()

    st.title("🌸 Menstrual Cycle Tracker")
    st.markdown("**Personalized insights based on your history.**")

    # --- Sidebar: User Input ---
    with st.sidebar:
        st.header("Profile & Settings")
        
        # 1. Basic Info
        age = st.number_input("Age", min_value=12, max_value=60, value=25)
        
        with st.expander("Physical Stats (Optional)"):
            height = st.number_input("Height (cm)", 100, 250, 165)
            weight = st.number_input("Weight (kg)", 30, 200, 60)
            if height > 0:
                bmi = weight / ((height/100)**2)
                st.caption(f"Estimated BMI: {bmi:.1f}")

        # 2. Lifestyle
        st.subheader("Lifestyle Indicators")
        stress = st.select_slider("Stress Level", options=["Low", "Medium", "High"], value="Medium")
        sleep = st.select_slider("Sleep Quality", options=["Poor", "Normal", "Good"], value="Normal")
        
        st.text_area("Known Conditions (Notes only)", placeholder="e.g. PCOS, thyroid (for your reference)")

        # 3. Menstrual History
        st.header("Cycle History")
        st.info("Please enter the start dates of your last few periods.")
        
        # Initialize session state for dates if not present
        if 'period_dates' not in st.session_state:
            # Default: specific dates for demo purposes
            st.session_state.period_dates = [
                date.today() - timedelta(days=28),
                date.today() - timedelta(days=57),
                date.today() - timedelta(days=86)
            ]

        # Date Input Widget (Multi-date picker is tricky in basic Streamlit, using a list approach)
        # For simplicity in this demo, we let user pick a date and add it button style
        new_date = st.date_input("Add a Period Start Date", value=date.today())
        
        col1, col2 = st.columns(2)
        if col1.button("Add Date"):
            if new_date not in st.session_state.period_dates:
                st.session_state.period_dates.append(new_date)
                st.success("Date added!")
        
        if col2.button("Clear All"):
            st.session_state.period_dates = []

        # Display current list
        st.write("Recorded Dates:")
        sorted_dates = sorted(st.session_state.period_dates, reverse=True)
        st.dataframe(pd.DataFrame(sorted_dates, columns=["Start Date"]), height=150)

        fallback_len = st.number_input("Typical Cycle Length (Fallback)", 21, 45, 28)

    # --- Logic Processing ---
    model = CycleModel(age=age)
    
    # Analyze History
    stats = model.analyze_history(st.session_state.period_dates, typical_length=fallback_len)
    avg_len = stats['avg_length']
    std_dev = stats['std_dev']
    last_date = stats.get('last_date')

    # Predictions
    prediction = model.predict_phases(last_date, avg_len)
    
    # Scores
    score, regularity_label = model.calculate_regularity_score(stats)
    
    # Hints
    hints = model.generate_hints(stats, prediction)

    # --- Main Dashboard ---
    
    # 1. Top KPI Row
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Average Cycle", f"{avg_len:.1f} days", f"± {std_dev:.1f} days")
    
    if prediction:
        kpi2.metric("Current Phase", prediction['current_phase'], f"Day {prediction['current_day']}")
        kpi3.metric("Next Period", f"{prediction['next_period_start']}")
    else:
        kpi2.metric("Current Phase", "No Data")
        kpi3.metric("Next Period", "--")

    st.divider()

    # 2. Phase Visualization & Status
    if prediction:
        st.subheader("Current Cycle Timeline")
        
        # Simple visual representation
        # Progress bar logic: cap at 100%
        progress = min(1.0, prediction['current_day'] / avg_len)
        st.progress(progress)
        
        # Phase Descriptions
        phase_cols = st.columns(4)
        phases = ["Menstrual (1-5)", "Follicular (6-13)", "Ovulation (14-15)", "Luteal (16+)"]
        current_p = prediction['current_phase']
        
        for i, p_name in enumerate(phases):
            # Highlight current phase
            is_active = False
            if "Menstrual" in current_p and i == 0: is_active = True
            elif "Follicular" in current_p and i == 1: is_active = True
            elif "Ovulation" in current_p and i == 2: is_active = True
            elif "Luteal" in current_p and i == 3: is_active = True
            
            box_bg = "background-color: #ffcdd2;" if is_active else "background-color: #f0f2f6; opacity: 0.5;"
            border = "border: 2px solid #e91e63;" if is_active else "border: 1px solid #ddd;"
            
            phase_cols[i].markdown(f"""
            <div style="{box_bg} {border} padding: 10px; border-radius: 5px; text-align: center; font-size: 0.8em;">
                <b>{p_name}</b>
            </div>
            """, unsafe_allow_html=True)
            
        st.caption(f"Estimated Ovulation Window: Around {prediction['est_ovulation_date']}")

    # 3. Regularity & Health Insights
    st.divider()
    st.subheader("Cycle Health Insights")
    
    col_score, col_hints = st.columns([1, 2])
    
    with col_score:
        st.write("**Regularity Score**")
        st.title(f"{score}/100")
        
        color = "green"
        if score < 50: color = "red"
        elif score < 80: color = "orange"
        
        st.markdown(f"<span style='color:{color}; font-weight:bold'>{regularity_label}</span>", unsafe_allow_html=True)
        st.caption("Based on consistency of cycle length.")

    with col_hints:
        st.write("**Observations & Hints**")
        if hints:
            for hint in hints:
                st.markdown(f"<div class='warning-box'>{hint}</div>", unsafe_allow_html=True)
        else:
            st.success("No unusual patterns detected based on current data.")
            
        if stress == "High" or sleep == "Poor":
            st.info("💡 Note: High stress or poor sleep can often delay your cycle or make it irregular.")

    # --- Footer / Disclaimer (CRITICAL) ---
    st.markdown("""
    <div class='disclaimer'>
        <h3>⚠️ IMPORTANT DISCLAIMER</h3>
        <p>This tool is for <b>personal tracking and general reference only</b>. It is <b>NOT</b> a medical device, diagnostic tool, or contraceptive aid.</p>
        <p>The predictions are estimates based on averages and may not reflect your actual physiology. 
        <b>Do not rely on this app for preventing pregnancy or specific medical decisions.</b></p>
        <p>If you have concerns about your health, pain, or irregularity, please consult a professional doctor.</p>
        <p><i>Data Privacy: All data entered here is processed locally in this session and is not sent to any external server.</i></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()