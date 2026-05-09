import streamlit as st
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Ensure environment is loaded BEFORE anything else
load_dotenv(override=True)

from pipeline.shortlisting_pipeline import ShortlistingPipeline
from services.candidate_scorer import CandidateScorer
from services.candidate_ranker import CandidateRanker
from services.override_logger import log_override

# --- UI CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="TalentLens | Candidate Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS Injection for Visual Excellence
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Glowing Gradient Title */
    .talentlens-title {
        background: -webkit-linear-gradient(45deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    
    .talentlens-subtitle {
        color: #A0AEC0;
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0px;
        margin-bottom: 30px;
    }
    
    /* Metrics glassmorphism styling */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        border-color: rgba(255,255,255,0.15);
    }
    
    /* Styled run button */
    .stButton > button {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4);
        width: 100%;
        margin-top: 15px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.6);
        color: white !important;
    }
    
    /* Status Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 10px;
    }
    .badge-hire { background: rgba(72, 187, 120, 0.15); color: #48BB78; border: 1px solid rgba(72, 187, 120, 0.3); }
    .badge-consider { background: rgba(237, 137, 54, 0.15); color: #ED8936; border: 1px solid rgba(237, 137, 54, 0.3); }
    .badge-nohire { background: rgba(245, 101, 101, 0.15); color: #F56565; border: 1px solid rgba(245, 101, 101, 0.3); }
    .badge-tier { background: rgba(66, 153, 225, 0.15); color: #4299E1; border: 1px solid rgba(66, 153, 225, 0.3); }
    
    /* Custom divider */
    hr {
        border-top: 1px solid rgba(255,255,255,0.1);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- APP INITIALIZATION ---
@st.cache_resource
def get_pipeline():
    """Cache the pipeline so we don't reload the HuggingFace model constantly."""
    return ShortlistingPipeline()

def main():
    if "pipeline_results" not in st.session_state:
        st.session_state.pipeline_results = None
    if "session_overrides" not in st.session_state:
        st.session_state.session_overrides = []

    # --- SIDEBAR CONFIGURATION ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>⚙️ Configure Run</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #A0AEC0; font-size: 0.9rem;'>Setup Job Description & Candidates</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        st.subheader("📝 Job Description")
        jd_input_method = st.radio("Provide JD via:", ["Upload File", "Paste Text"], horizontal=True)
        
        jd_raw_text = ""
        
        if jd_input_method == "Paste Text":
            jd_raw_text = st.text_area("Paste the exact Job Description here:", height=150, placeholder="e.g. We are looking for a Senior Software Engineer...")
        else:
            jd_file = st.file_uploader("Upload JD Document", type=["pdf", "docx", "txt"])
            if jd_file:
                ext = jd_file.name.lower().split('.')[-1]
                from utils.document_parser import extract_text_from_pdf, extract_text_from_docx
                if ext == 'pdf':
                    jd_raw_text = extract_text_from_pdf(jd_file)
                elif ext == 'docx':
                    jd_raw_text = extract_text_from_docx(jd_file)
                elif ext == 'txt':
                    jd_raw_text = jd_file.read().decode('utf-8')

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("👥 Candidate Pool")
        resume_files = st.file_uploader("Upload Candidate Resumes", type=["pdf", "docx"], accept_multiple_files=True, help="You can upload multiple PDFs or DOCX files at once.")
        
        start_btn = st.button("✨ Run Intelligence Pipeline")

    # --- MAIN CONTENT AREA ---
    st.markdown("<div class='talentlens-title'>TalentLens</div>", unsafe_allow_html=True)
    st.markdown("<div class='talentlens-subtitle'>AI-powered candidate intelligence platform for semantic resume analysis, smart ranking, and transparent hiring decisions.</div>", unsafe_allow_html=True)
    
    if start_btn:
        if not jd_raw_text.strip():
            st.error("⚠️ Please provide a Job Description (either typed or uploaded) in the sidebar.")
            return
        if not resume_files:
            st.error("⚠️ Please upload at least one Candidate Resume in the sidebar.")
            return

        pipeline = get_pipeline()

        with st.status("🧠 Initializing Intelligence Pipeline...", expanded=True) as status:
            st.write("Targeting key requirements from Job Description...")
            try:
                jd_data = pipeline.process_job_description(jd_raw_text)
                st.write(f"✅ Context Locked: **{jd_data.get('role_title', 'Unknown')}**")
            except Exception as e:
                status.update(label="Pipeline Failed", state="error", expanded=True)
                st.error(f"Failed to parse JD: {e}")
                return

            st.write(f"Processing {len(resume_files)} candidate vectors...")
            resumes_input = [(f.name, f) for f in resume_files]
            
            try:
                final_results = pipeline.process_candidates(jd_data, jd_raw_text, resumes_input)
                # Store in session state to enable overrides without rerunning pipeline
                st.session_state.pipeline_results = final_results
                st.session_state.session_overrides = [] # Reset log on new run
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Pipeline Failed", state="error", expanded=True)
                st.error(f"Error during candidate processing: {e}")
                return

    # Render results from session state (allows interactive updates without reloading)
    if st.session_state.pipeline_results:
        final_results = st.session_state.pipeline_results
        summary = final_results.get("summary", {})
        
        st.markdown("### 📊 Executive Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Candidates Analyzed", summary.get("total_candidates", 0))
        col2.metric("🏆 Top Tier", summary.get("Top Tier", 0))
        col3.metric("🤔 Consider", summary.get("Consider", 0))
        col4.metric("❌ Weak Match", summary.get("Weak Match", 0))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🏆 Ranked Leaderboard")
        
        ranked_list = final_results.get("ranked_candidates", [])
        if not ranked_list:
            st.warning("No candidates were successfully ranked.")
        else:
            for idx, candidate in enumerate(ranked_list):
                score = candidate["weighted_total"]
                name = candidate["candidate_name"]
                rank = candidate["rank"]
                rec = candidate["recommendation"]
                tier = candidate["categorization"]
                rubric = candidate["rubric_scores"]
                
                # Badge generation
                badge_class = "badge-nohire"
                if rec == "Hire":
                    badge_class = "badge-hire"
                elif rec == "Consider":
                    badge_class = "badge-consider"
                    
                badge_html = f"<span class='badge {badge_class}'>{rec}</span>"
                tier_html = f"<span class='badge badge-tier'>{tier}</span>"

                with st.expander(f"#{rank} — {name}  (Score: {score}/10)"):
                    st.markdown(f"{badge_html} {tier_html}", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown("##### Dimension Breakdown")
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    cols = [c1, c2, c3, c4, c5]
                    dims = [
                        ("Skills (30%)", "skills_match"),
                        ("Experience (25%)", "experience_relevance"),
                        ("Education (15%)", "education_certs"),
                        ("Portfolio (20%)", "project_portfolio"),
                        ("Communication (10%)", "communication_quality")
                    ]
                    
                    for i, (label, key) in enumerate(dims):
                        dim_data = rubric[key]
                        score_val = dim_data.get('score', 0)
                        is_overriden = "original_score" in dim_data
                        
                        with cols[i]:
                            if is_overriden:
                                st.metric(f"{label} ⚠️", f"{score_val}/10")
                                st.markdown(f"<div style='font-size: 0.75rem; color: #718096;'>Original: {dim_data['original_score']}/10</div>", unsafe_allow_html=True)
                            else:
                                st.metric(label, f"{score_val}/10")
                            st.markdown(f"<div style='font-size: 0.8rem; color: #A0AEC0; font-style: italic;'>{dim_data.get('justification', '')}</div>", unsafe_allow_html=True)
                    
                    # HR Override Section
                    st.markdown("<hr style='margin: 1.5rem 0; border-top: 1px dashed rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                    with st.expander("⚙️ HR Override"):
                        dim_options = {
                            "Skills": "skills_match",
                            "Experience": "experience_relevance",
                            "Education": "education_certs",
                            "Portfolio": "project_portfolio",
                            "Communication": "communication_quality"
                        }
                        
                        o_col1, o_col2 = st.columns([1, 1.5])
                        with o_col1:
                            selected_dim_label = st.selectbox("Select Dimension to Override", options=list(dim_options.keys()), key=f"dim_{name}_{idx}")
                            new_score = st.number_input("New Score (0-10)", min_value=0, max_value=10, value=5, key=f"score_{name}_{idx}")
                        with o_col2:
                            reason = st.text_input("Reason for Override (Required)", key=f"reason_{name}_{idx}")
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("Apply Override", key=f"btn_{name}_{idx}"):
                                if not reason.strip():
                                    st.error("Reason is required.")
                                else:
                                    dim_key = dim_options[selected_dim_label]
                                    old_score = candidate["rubric_scores"][dim_key].get("score", 0)
                                    
                                    # Save original score if this is the first override
                                    if "original_score" not in candidate["rubric_scores"][dim_key]:
                                        candidate["rubric_scores"][dim_key]["original_score"] = old_score
                                        
                                    candidate["rubric_scores"][dim_key]["score"] = new_score
                                    
                                    # Recalculate Totals
                                    scorer = CandidateScorer()
                                    dim_scores = {k: v.get("score", 0) for k, v in candidate["rubric_scores"].items()}
                                    new_total = scorer.calculate_weighted_total(dim_scores)
                                    new_rec = scorer.generate_recommendation(new_total)
                                    
                                    old_total = candidate["weighted_total"]
                                    old_rec = candidate["recommendation"]
                                    
                                    candidate["weighted_total"] = new_total
                                    candidate["recommendation"] = new_rec
                                    
                                    ranker = CandidateRanker()
                                    candidate["categorization"] = ranker._categorize_candidate(new_total)
                                    
                                    # Log to file
                                    log_override(name, selected_dim_label, old_score, new_score, reason, old_rec, new_rec)
                                    
                                    # Add to session log
                                    st.session_state.session_overrides.append({
                                        "Candidate": name,
                                        "Dimension": selected_dim_label,
                                        "Original Score": old_score,
                                        "New Score": new_score,
                                        "Reason": reason,
                                        "Timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                    
                                    # Re-sort ranked_list based on new totals
                                    sorted_list = sorted(
                                        st.session_state.pipeline_results["ranked_candidates"],
                                        key=lambda x: x["weighted_total"],
                                        reverse=True
                                    )
                                    
                                    # Update ranks
                                    for i_rank, c in enumerate(sorted_list):
                                        c["rank"] = i_rank + 1
                                        
                                    st.session_state.pipeline_results["ranked_candidates"] = sorted_list
                                    
                                    # Update Summary
                                    new_summary = {
                                        "total_candidates": len(sorted_list),
                                        "Top Tier": 0, "Consider": 0, "Weak Match": 0
                                    }
                                    for c in sorted_list:
                                        new_summary[c["categorization"]] += 1
                                    st.session_state.pipeline_results["summary"] = new_summary
                                    
                                    # Trigger UI refresh
                                    st.rerun()

        # Render Override Log Table if any overrides occurred in this session
        if st.session_state.session_overrides:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 📝 Override Log (Current Session)")
            df = pd.DataFrame(st.session_state.session_overrides)
            st.dataframe(df, use_container_width=True)

    elif not start_btn:
        # Default empty state
        st.info("👈 Please configure the pipeline in the sidebar and click **Run Intelligence Pipeline**.")
        
        st.markdown("""
        <div style="margin-top: 50px; text-align: center; padding: 40px; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1);">
            <h3 style="color: #A0AEC0;">Waiting for data...</h3>
            <p style="color: #718096; max-width: 500px; margin: 0 auto;">
                Upload a Job Description and a batch of Candidate Resumes to see the semantic scoring engine in action.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
