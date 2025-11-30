import sys
from pathlib import Path

# Ensure project root is importable
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import os
import traceback

from app.weather_api import fetch_metar_decoded
from app.rag_engine import SimpleRAG
from app.runway_logic import pick_best_runway
from app.decision_engine import apply_weather_rules, combine_with_poh_limits
from app.pdf_report import create_report_bytes

# ---------------------------------------------------------------------
# UI HEADER
# ---------------------------------------------------------------------
st.set_page_config(page_title="AIRMAN", layout="wide")
st.title("✈️ AIRMAN — Preflight Assistant (Prototype)")
st.write("This is a stable working version for demo purposes.")

# ---------------------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    dep = st.text_input("Departure ICAO", "VOBG")
    arr = st.text_input("Destination ICAO", "VOMM")
    aircraft = st.selectbox("Aircraft", ["Cessna 172S", "Diamond DA42 L360"])
    runway_raw = st.text_input("Runways", "09/27")
    run_button = st.button("Evaluate")

with col2:
    st.info("Upload POH PDFs to `/data/` to use your own manuals.")

# ---------------------------------------------------------------------
# BUILD RAG INDEX (SAFE MODE)
# ---------------------------------------------------------------------
if "rag" not in st.session_state:
    rag = SimpleRAG()
    pdf1 = str(Path(project_root) / "data" / "POH-Cessna-172S.pdf")
    pdf2 = str(Path(project_root) / "data" / "DA42-L360-POH.pdf")
    pdfs = [p for p in [pdf1, pdf2] if os.path.exists(p)]
    rag.build_index_from_pdfs(pdfs)
    st.session_state.rag = rag
else:
    rag = st.session_state.rag

# DEBUG
st.write("DEBUG — run_button =", run_button)

# ---------------------------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------------------------
if run_button:

    st.subheader("Running Evaluation…")

    try:
        # -------- WEATHER --------
        dep_metar = fetch_metar_decoded(dep)
        arr_metar = fetch_metar_decoded(arr)

        st.write("Departure METAR:", dep_metar)
        st.write("Arrival METAR:", arr_metar)

        # -------- POH LIMITS --------
        results = rag.retrieve("crosswind", k=6)
        chunks = [r["doc"] for r in results]

        poh_limits = rag.extract_limits_from_chunks(
            chunks,
            aircraft_label=aircraft,
            pdf_paths=[p for p in [pdf1, pdf2] if os.path.exists(p)],
        )

        st.write("POH Limits Extracted:", poh_limits)

        # -------- WEATHER EVAL --------
        dep_eval = apply_weather_rules(dep_metar)
        arr_eval = apply_weather_rules(arr_metar)

        # -------- RUNWAY LOGIC --------
        runways = []
        for r in runway_raw.split(","):
            r = r.strip()
            if "/" in r:
                try:
                    headings = [int(x) * 10 for x in r.split("/")]
                except:
                    headings = []
            else:
                try:
                    headings = [int(r) * 10]
                except:
                    headings = []

            runways.append({"name": r, "heading": headings})

        parsed_runways = []
        for r in runways:
            for h in r["heading"]:
                parsed_runways.append({"name": r["name"], "heading": h})

        best_runway = pick_best_runway(
            parsed_runways,
            dep_metar.get("wind_dir"),
            dep_metar.get("wind_speed_kt"),
        )

        st.write("Best Runway:", best_runway)

        # -------- FINAL DECISION --------
        final_dep = combine_with_poh_limits(dep_eval, poh_limits)
        final_arr = combine_with_poh_limits(arr_eval, poh_limits)
        decision = final_dep["decision_go"] and final_arr["decision_go"]

        st.subheader("FINAL DECISION:")
        st.success("GO") if decision else st.error("NO-GO")

        # -------- PDF DOWNLOAD --------
        pdf_bytes = create_report_bytes(
            route=f"{dep}->{arr}",
            aircraft=aircraft,
            dep=dep,
            arr=arr,
            dep_metar=dep_metar,
            arr_metar=arr_metar,
            poh_limits=poh_limits,
            best_runway=best_runway,
            final_dep=final_dep,
            final_arr=final_arr,
            decision_text="GO" if decision else "NO-GO",
            alt="1000–1500 ft",
        )

        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name="preflight_report.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error("An error occurred. See details below:")
        st.text(traceback.format_exc())
