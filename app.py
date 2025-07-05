import streamlit as st
import pandas as pd
from matcher import match_resume_to_jobs
from generator import generate_reasoning
from upload_resume import extract_texts_from_pdfs
import os
import time

st.set_page_config(page_title="📄 AI Resume Matcher", layout="wide", initial_sidebar_state="collapsed")

# Enhanced styling with better blur handling and progress indicators
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Page background */
    .main, .block-container {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        padding-top: 2rem;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Headers */
    h1 {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.3)); }
        to { filter: drop-shadow(0 0 20px rgba(118, 75, 162, 0.5)); }
    }
    
    /* File uploaders - Reduced blur for better readability */
    .stFileUploader > div {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    /* Progress bar with better visibility */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
    }
    
    /* Processing indicator */
    .processing-indicator {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Time estimate display */
    .time-estimate {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid rgba(102, 126, 234, 0.4);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
        font-weight: 500;
        backdrop-filter: blur(3px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .time-estimate h3 {
        color: #667eea !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.2rem !important;
    }
    
    .time-estimate p {
        color: #a0a0a0 !important;
        margin: 0 !important;
        font-size: 0.9rem !important;
    }
    
    /* Navigation buttons */
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        cursor: pointer !important;
    }
    
    .nav-button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .nav-button:disabled {
        background: linear-gradient(135deg, #4a4a4a 0%, #3a3a3a 100%) !important;
        color: #888 !important;
        transform: none !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stButton button:disabled {
        background: linear-gradient(135deg, #4a4a4a 0%, #3a3a3a 100%) !important;
        color: #888 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Download buttons */
    .stDownloadButton button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3) !important;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4) !important;
    }
    
    /* Pagination info */
    .pagination-info {
        background: rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
        font-weight: 500;
        color: #667eea;
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stMetric > div {
        color: #667eea !important;
    }
    
    /* Alerts with better visibility */
    .stAlert {
        background: rgba(255, 193, 7, 0.15) !important;
        border: 1px solid rgba(255, 193, 7, 0.4) !important;
        border-radius: 10px !important;
        color: #ffc107 !important;
        backdrop-filter: blur(3px) !important;
    }
    
    .stSuccess {
        background: rgba(40, 167, 69, 0.15) !important;
        border: 1px solid rgba(40, 167, 69, 0.4) !important;
        border-radius: 10px !important;
        color: #28a745 !important;
        backdrop-filter: blur(3px) !important;
    }
    
    .stInfo {
        background: rgba(23, 162, 184, 0.15) !important;
        border: 1px solid rgba(23, 162, 184, 0.4) !important;
        border-radius: 10px !important;
        color: #17a2b8 !important;
        backdrop-filter: blur(3px) !important;
    }
    
    /* Custom containers with reduced blur */
    .upload-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .upload-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    }
    
    .result-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease;
    }
    
    .result-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .download-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Status indicators */
    .status-processing {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #8B0000;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        animation: processing 1.5s infinite;
    }
    
    .status-complete {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #006400;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    
    @keyframes processing {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📄 AI Resume Matcher")
st.markdown('<p class="subtitle">✨ Intelligently match resumes to perfect job opportunities with AI-powered analysis</p>', unsafe_allow_html=True)

# Upload section
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Upload Resumes")
    resume_files = st.file_uploader("Drop your PDF resumes here", type=["pdf"], accept_multiple_files=True, key="resume_upload")

with col2:
    st.markdown("### 📁 Upload Job Listings")
    job_file = st.file_uploader("Drop your CSV job file here", type=["csv"], key="job_upload")

st.markdown('</div>', unsafe_allow_html=True)

if resume_files and job_file:
    job_df = pd.read_csv(job_file)
    resume_texts = extract_texts_from_pdfs(resume_files)
    
    # Initialize session state
    if "all_results" not in st.session_state:
        st.session_state["all_results"] = []
    if "processing_complete" not in st.session_state:
        st.session_state["processing_complete"] = False
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0
    if "avg_processing_time" not in st.session_state:
        st.session_state["avg_processing_time"] = 30  # Default estimate
    
    total_resumes = len(resume_texts)
    
    # Time estimation before processing
    if not st.session_state["processing_complete"] and len(st.session_state["all_results"]) == 0:
        estimated_time = st.session_state["avg_processing_time"] * total_resumes
        estimated_minutes = int(estimated_time // 60)
        estimated_seconds = int(estimated_time % 60)
        
        st.markdown(f'''
            <div class="time-estimate">
                <h3>⏱️ Processing Time Estimate</h3>
                <p><strong>{estimated_minutes}m {estimated_seconds}s</strong> estimated for {total_resumes} resumes</p>
                <p>Average: ~{st.session_state["avg_processing_time"]}s per resume</p>
            </div>
        ''', unsafe_allow_html=True)
    
    # Check if we need to process
    if not st.session_state["processing_complete"] or len(st.session_state["all_results"]) != total_resumes:
        # Reset results for fresh processing
        st.session_state["all_results"] = []
        st.session_state["processing_complete"] = False
        st.session_state["current_page"] = 0
        
        # Progress section
        st.markdown(f"### 🎯 Processing All Resumes ({total_resumes} files)")
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_remaining_text = st.empty()
        
        # Overall processing indicator
        st.markdown('''
            <div class="processing-indicator">
                🔄 <strong>Processing all resumes in batch...</strong>
                <br>
                <small>AI is analyzing all resumes and matching with job opportunities</small>
            </div>
        ''', unsafe_allow_html=True)
        
        # Start timing
        overall_start_time = time.time()
        processing_times = []
        
        # Process all resumes at once
        for idx, (file_name, resume_text) in enumerate(resume_texts.items()):
            # Update progress
            progress = (idx + 1) / total_resumes
            progress_bar.progress(progress)
            
            # Calculate time remaining
            if processing_times:
                avg_time_so_far = sum(processing_times) / len(processing_times)
                remaining_resumes = total_resumes - (idx + 1)
                estimated_remaining = avg_time_so_far * remaining_resumes
                remaining_minutes = int(estimated_remaining // 60)
                remaining_seconds = int(estimated_remaining % 60)
                
                status_text.text(f"🔄 Processing {file_name} ({idx + 1}/{total_resumes})")
                time_remaining_text.text(f"⏱️ Estimated time remaining: {remaining_minutes}m {remaining_seconds}s")
            else:
                status_text.text(f"🔄 Processing {file_name} ({idx + 1}/{total_resumes}) - Calculating time...")
                time_remaining_text.text("⏱️ Estimating time remaining...")
            
            # Start timing for individual resume
            start_time = time.time()
            
            # Process resume
            top_matches = match_resume_to_jobs(resume_text, job_df)
            
            if top_matches is not None and not top_matches.empty:
                best_match = top_matches.iloc[0]
                explanation = generate_reasoning(resume_text, best_match.get('job_description', '')) if 'job_description' in best_match else "Explanation not available."
                
                # End timing
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                
                # Store result
                result_data = {
                    "resume": file_name,
                    "job_title": best_match['job_title'],
                    "role": best_match['role'],
                    "score": best_match['score'],
                    "explanation": explanation,
                    "processing_time": processing_time
                }
                
                st.session_state["all_results"].append(result_data)
                
            else:
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                
                # Store result even for no matches
                result_data = {
                    "resume": file_name,
                    "job_title": "No Match Found",
                    "role": "N/A",
                    "score": 0,
                    "explanation": "No suitable match found for this resume.",
                    "processing_time": processing_time
                }
                
                st.session_state["all_results"].append(result_data)
        
        # Complete processing
        overall_end_time = time.time()
        total_processing_time = overall_end_time - overall_start_time
        
        # Update average processing time for future estimates
        if processing_times:
            st.session_state["avg_processing_time"] = sum(processing_times) / len(processing_times)
        
        # Update final progress
        progress_bar.progress(1.0)
        status_text.empty()
        time_remaining_text.empty()
        
        # Mark as complete
        st.session_state["processing_complete"] = True
        
        # Show completion message
        minutes = int(total_processing_time // 60)
        seconds = int(total_processing_time % 60)
        st.success(f"🎉 All {total_resumes} resumes processed successfully! Total time: {minutes}m {seconds}s")
    
    # Display results with pagination
    if st.session_state["all_results"]:
        st.markdown("### 📋 Results")
        
        # Pagination info
        total_results = len(st.session_state["all_results"])
        current_page = st.session_state["current_page"]
        current_result = st.session_state["all_results"][current_page]
        
        st.markdown(f'''
            <div class="pagination-info">
                📄 Showing result {current_page + 1} of {total_results}
            </div>
        ''', unsafe_allow_html=True)
        
        # Display current result
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        
        # Resume header with status
        col_status1, col_status2 = st.columns([3, 1])
        with col_status1:
            st.markdown(f"## 🎯 {current_result['resume']}")
        with col_status2:
            st.markdown(f'<span class="status-complete">✅ Complete ({current_result["processing_time"]:.1f}s)</span>', unsafe_allow_html=True)
        
        if current_result['score'] > 0:  # Valid match found
            # Display results using Streamlit components
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**🧠 Best Match:**")
                st.write(current_result['job_title'])
                
                st.markdown("**💼 Role:**")
                st.write(current_result['role'])
            
            with col2:
                st.markdown("**✅ Match Score:**")
                score_color = "#28a745" if current_result['score'] >= 70 else "#ffc107" if current_result['score'] >= 50 else "#dc3545"
                st.markdown(f'<div style="background: {score_color}; color: white; padding: 10px; border-radius: 20px; text-align: center; font-weight: bold; font-size: 1.2rem;">{current_result["score"]:.1f}%</div>', unsafe_allow_html=True)
            
            # Explanation section
            st.markdown("**🧩 AI Analysis:**")
            st.write(current_result['explanation'])
        else:
            st.warning(f"⚠️ No suitable match found for resume: {current_result['resume']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Previous", disabled=(current_page == 0), key="prev_btn"):
                st.session_state["current_page"] = max(0, current_page - 1)
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 0.5rem; color: #a0a0a0;'>Page {current_page + 1} of {total_results}</div>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Next ➡️", disabled=(current_page >= total_results - 1), key="next_btn"):
                st.session_state["current_page"] = min(total_results - 1, current_page + 1)
                st.rerun()
        
        # Quick navigation
        if total_results > 1:
            st.markdown("**🔍 Quick Navigation:**")
            selected_page = st.selectbox(
                "Jump to result:",
                options=range(total_results),
                index=current_page,
                format_func=lambda x: f"{x+1}. {st.session_state['all_results'][x]['resume']}",
                key="page_selector"
            )
            
            if selected_page != current_page:
                st.session_state["current_page"] = selected_page
                st.rerun()
    
    # Download section
    if st.session_state["all_results"]:
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        st.markdown("## 📊 Analysis Results")
        
        results_df = pd.DataFrame(st.session_state["all_results"])
        
        # Enhanced metrics with processing time
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Processed", len(st.session_state["all_results"]))
        with col2:
            avg_score = sum(r['score'] for r in st.session_state["all_results"]) / len(st.session_state["all_results"]) if st.session_state["all_results"] else 0
            st.metric("📈 Average Score", f"{avg_score:.1f}%")
        with col3:
            best_score = max(r['score'] for r in st.session_state["all_results"]) if st.session_state["all_results"] else 0
            st.metric("🏆 Best Score", f"{best_score:.1f}%")
        with col4:
            total_time = sum(r['processing_time'] for r in st.session_state["all_results"]) if st.session_state["all_results"] else 0
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            st.metric("⏱️ Total Time", f"{minutes}m {seconds}s")
        
        # Download buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name="resume_match_results.csv",
                mime="text/csv",
                key="download_csv"
            )
        
        with col2:
            json_data = results_df.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name="resume_match_results.json",
                mime="application/json",
                key="download_json"
            )
        
        with col3:
            if st.button("🔄 Reset Analysis"):
                st.session_state["all_results"] = []
                st.session_state["processing_complete"] = False
                st.session_state["current_page"] = 0
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-save
    if st.session_state["all_results"]:
        os.makedirs("output", exist_ok=True)
        pd.DataFrame(st.session_state["all_results"]).to_csv("output/match_results.csv", index=False)

elif not resume_files and not job_file:
    st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #a0a0a0;">
            <h3>🚀 Ready to find the perfect job matches?</h3>
            <p>Upload your resumes and job listings to get started with AI-powered matching!</p>
        </div>
    """, unsafe_allow_html=True)
elif not resume_files:
    st.info("📄 Please upload at least one resume PDF to begin the analysis.")
elif not job_file:
    st.info("📁 Please upload a job listings CSV file to start matching.")