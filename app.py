import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.warning("""
This tool is for informational purposes only.
It does not constitute medical advice.

Always consult a qualified healthcare professional before using any medication or substance.
Use at your own risk.
""")
st.caption("Not medical advice • Use at your own risk")

def calculate_bac_water(vial_mg, desired_mcg, preferred_units, syringe_type):
    vial_mcg = vial_mg * 1000
    total_doses = vial_mcg / desired_mcg
    total_units_needed = total_doses * preferred_units
    return total_units_needed / syringe_type

def calculate_draw_units(vial_mg, bac_water_ml, desired_mcg, syringe_type):
    vial_mcg = vial_mg * 1000
    total_units = bac_water_ml * syringe_type
    mcg_per_unit = vial_mcg / total_units
    return desired_mcg / mcg_per_unit

def process_and_save(units, water, dose, p_name, v_mg, s_type, v_choice, r_b2a, p_b_name, exp_date):
    st.write("Syringe Fill Visual")
    st.progress(min(units / s_type, 1.0))
    
    if units > (s_type / 2):
        st.warning("High Volume Alert Large Injections May Cause Discomfort")
        
    if v_choice == "Combo Blended Vial":
        incidental = dose * r_b2a
        st.warning(f"Combo Alert Injecting {incidental:.1f}mcg Of {p_b_name} As Well")
        
    st.session_state.saved_profiles.append({
        "Peptide": p_name,
        "Vial mg": v_mg,
        "Dose mcg": dose,
        "Water mL": round(water, 2),
        "Units": round(units, 1),
        "Expires": exp_date
    })

if "saved_profiles" not in st.session_state:
    st.session_state.saved_profiles = []

st.title("Underground Peptide Calculator Pro")

with st.sidebar:
    st.header("Saved Profiles")
    if st.session_state.saved_profiles:
        df = pd.DataFrame(st.session_state.saved_profiles)
        st.dataframe(df, use_container_width=True)
        if st.button("Clear Saved Profiles"):
            st.session_state.saved_profiles = []
            st.rerun()
    else:
        st.write("No Profiles Saved Yet")

st.header("Syringe Setup")
syringe_selection = st.radio(
    "Select Your Syringe Type",
    ["U100 Standard", "U40 Veterinary"]
)
syringe_type = 100 if syringe_selection == "U100 Standard" else 40

st.header("Expiration Tracker")
mix_date = st.date_input("When Did You Mix This Vial", date.today())
expiration_date = mix_date + timedelta(days=28)
days_left = (expiration_date - date.today()).days

if days_left < 0:
    st.error("Warning This Vial Has Expired Discard Immediately")
elif days_left <= 7:
    st.warning(f"Heads Up Only {days_left} Days Left Until Expiration")
else:
    st.success(f"Vial Is Fresh Expires On {expiration_date}")

vial_choice = st.radio(
    "Vial Type",
    ["Single Peptide", "Combo Blended Vial"]
)

calc_choice = st.radio(
    "Calculation Method",
    ["Calculate BAC Water To Add", "Calculate Units To Draw"]
)

st.divider()

ratio_b_to_a = 0
pep_b_name = ""

if vial_choice == "Single Peptide":
    pep_name = st.text_input("Peptide Name")
    vial_mg = st.number_input("Vial Size In mg", min_value=0.0, value=5.0)
else:
    pep_a_name = st.text_input("Primary Peptide Name")
    vial_a_mg = st.number_input("Primary Peptide Amount In mg", min_value=0.0, value=5.0)
    pep_b_name = st.text_input("Incidental Peptide Name")
    vial_b_mg = st.number_input("Incidental Peptide Amount In mg", min_value=0.0, value=5.0)

    if vial_a_mg > 0:
        ratio_b_to_a = vial_b_mg / vial_a_mg
        pep_name = pep_a_name
        vial_mg = vial_a_mg
    else:
        st.warning("Amount Must Be Greater Than Zero")
        st.stop()

st.divider()

if calc_choice == "Calculate BAC Water To Add":
    desired_mcg = st.number_input("Target Dose In mcg", min_value=0.0, value=250.0)
    preferred_units = st.number_input("Preferred Syringe Draw In Units", min_value=0.0, value=10.0)

    if st.button("Calculate Water Needed", key="btn_calc_water"):
        if desired_mcg <= 0 or preferred_units <= 0:
            st.error("Inputs Must Be Greater Than Zero")
        elif desired_mcg > (vial_mg * 1000):
            st.error("Dose Exceeds Total Vial Amount Please Verify")
        else:
            bac_water_ml = calculate_bac_water(vial_mg, desired_mcg, preferred_units, syringe_type)
            st.success(f"Add Exactly {bac_water_ml:.2f} mL Of BAC Water")
            st.info(f"To Dose Draw Up To The {preferred_units:.1f} Unit Mark")
            process_and_save(preferred_units, bac_water_ml, desired_mcg, pep_name, vial_mg, syringe_type, vial_choice, ratio_b_to_a, pep_b_name, expiration_date)

else:
    bac_water_ml = st.number_input("BAC Water Added In mL", min_value=0.0, value=2.0)
    desired_mcg = st.number_input("Target Dose In mcg", min_value=0.0, value=250.0)

    if st.button("Calculate Draw Units", key="btn_calc_units"):
        if bac_water_ml <= 0 or desired_mcg <= 0:
            st.error("Inputs Must Be Greater Than Zero")
        elif desired_mcg > (vial_mg * 1000):
            st.error("Dose Exceeds Total Vial Amount Please Verify")
        else:
            units_to_draw = calculate_draw_units(vial_mg, bac_water_ml, desired_mcg, syringe_type)
            st.success(f"To Dose Draw Exactly {units_to_draw:.1f} Units")
            process_and_save(units_to_draw, bac_water_ml, desired_mcg, pep_name, vial_mg, syringe_type, vial_choice, ratio_b_to_a, pep_b_name, expiration_date)
