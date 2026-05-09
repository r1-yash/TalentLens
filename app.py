import streamlit as st
import os
from dotenv import load_dotenv

# Ensure environment is loaded BEFORE anything else
load_dotenv(override=True)

from pipeline.shortlisting_pipeline import ShortlistingPipeline

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
            # Step 1: JD Extraction
            st.write("Targeting key requirements from Job Description...")
            try:
                jd_data = pipeline.process_job_description(jd_raw_text)
                st.write(f"✅ Context Locked: **{jd_data.get('role_title', 'Unknown')}**")
            except Exception as e:
                status.update(label="Pipeline Failed", state="error", expanded=True)
                st.error(f"Failed to parse JD: {e}")
                return

            # Step 2: Semantic Matching & Scoring
            st.write(f"Processing {len(resume_files)} candidate vectors...")
            resumes_input = [(f.name, f) for f in resume_files]
            
            try:
                final_results = pipeline.process_candidates(jd_data, jd_raw_text, resumes_input)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Pipeline Failed", state="error", expanded=True)
                st.error(f"Error during candidate processing: {e}")
                return
        
        # --- DISPLAY RESULTS ---
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
            return

        for candidate in ranked_list:
            score = candidate["weighted_total"]
            name = candidate["candidate_name"]
            rank = candidate["rank"]
            rec = candidate["recommendation"]
            tier = candidate["categorization"]
            
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
                
                # Rubric sub-scores
                st.markdown("##### Dimension Breakdown")
                rubric = candidate["rubric_scores"]
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Skills (30%)", f"{rubric['skills_match']}/10")
                c2.metric("Experience (25%)", f"{rubric['experience_relevance']}/10")
                c3.metric("Education (15%)", f"{rubric['education_certs']}/10")
                c4.metric("Portfolio (20%)", f"{rubric['project_portfolio']}/10")
                c5.metric("Communication (10%)", f"{rubric['communication_quality']}/10")
                
    else:
        # Default empty state
        st.info("👈 Please configure the pipeline in the sidebar and click **Run Intelligence Pipeline**.")
        
        # Adding a nice placeholder graphic or text
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
