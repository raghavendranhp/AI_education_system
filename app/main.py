import streamlit as st
import pandas as pd
import joblib
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.groq_assistant import GroqTutorAssistant
from src.feature_recalculation import recalculate_features
from src.diagnostics import run_diagnostics, generate_fallback_intervention
from src.recommendation_engine import HybridRecommender

st.set_page_config(page_title="Seshat AI - Educational Intelligence", layout="wide", initial_sidebar_state="expanded")

# --- UI Styling ---
st.markdown("""
<style>
    .workspace-card { padding: 20px; border-radius: 10px; background-color: #ffffff; border-top: 4px solid #2563eb; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .risk-high { color: #dc2626; font-weight: bold; font-size: 20px;}
    .risk-low { color: #16a34a; font-weight: bold; font-size: 20px;}
    .stat-val { font-size: 24px; font-weight: bold; color: #1e293b; }
    .stat-label { font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: bold;}
    .weakness-item { border-left: 3px solid #f59e0b; padding-left: 10px; margin-bottom: 5px; background: #fffbeb;}
    .history-item { font-size: 14px; padding: 5px; border-bottom: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

#Diagnostics Gate
@st.cache_resource
def load_and_verify():
    status = run_diagnostics("d:/OFFICE/Tasks/tutoring_system/models")
    return status

diag_status = load_and_verify()
if not diag_status['healthy']:
    st.error("Platform Diagnostics Failed:")
    for e in diag_status['errors']: st.error(f"- {e}")
    st.stop()

#Resource Loading 
@st.cache_data
def load_data():
    df = pd.read_csv("d:/OFFICE/Tasks/tutoring_system/data/processed/master_dataset.csv")
    try:
        kmeans = joblib.load("d:/OFFICE/Tasks/tutoring_system/models/kmeans_clusterer.pkl")
        scaler = joblib.load("d:/OFFICE/Tasks/tutoring_system/models/kmeans_scaler.pkl")
        cluster_features = ['engagement_ratio', 'average_score', 'resource_diversity_score']
        X_clust = df[cluster_features].fillna(0)
        X_scaled = scaler.transform(X_clust)
        df['cluster_id'] = kmeans.predict(X_scaled)
        cluster_mapping = {
            0: 'Passive Learners',
            1: 'Highly Engaged Achievers',
            2: 'Inconsistent Learners',
            3: 'Silent Dropout Risk'
        }
        df['educational_segment'] = df['cluster_id'].map(cluster_mapping)
    except Exception as e:
        df['educational_segment'] = 'Pending'
    return df

@st.cache_resource
def load_ml_artifacts():
    models_dir = "d:/OFFICE/Tasks/tutoring_system/models"
    perf = joblib.load(os.path.join(models_dir, "performance_pipeline.pkl"))
    drop = joblib.load(os.path.join(models_dir, "dropout_pipeline.pkl"))
    rec = HybridRecommender(models_dir=models_dir)
    return perf, drop, rec

df = load_data()
perf_model, drop_model, recommender = load_ml_artifacts()

#Navigation 
page = option_menu(
    menu_title=None,
    options=["1. Home", "2. Student Intelligence Workspace", "3. Cohort Analytics", "4. AI Tutor Assistant"],
    icons=["house", "laptop", "bar-chart-line", "robot"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)


#HOME
if page == "1. Home":
    st.title("Educational Intelligence Overview")
    st.markdown("Global perspective of cohort health and active interventions.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='workspace-card'><div class='stat-label'>Total Students</div><div class='stat-val'>{len(df):,}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='workspace-card'><div class='stat-label'>At-Risk</div><div class='stat-val' style='color:#dc2626;'>{len(df[df['dropout_risk_score'] > 0.5]):,}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='workspace-card'><div class='stat-label'>Avg Score</div><div class='stat-val'>{df['average_score'].mean():.1f}%</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='workspace-card'><div class='stat-label'>AI Tutor</div><div class='stat-val' style='color:#16a34a;'>Online</div></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Educational Segmentation")
        if 'educational_segment' in df.columns:
            seg_counts = df['educational_segment'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Count']
            fig_seg = px.pie(seg_counts, names='Segment', values='Count', hole=0.4, title="KMeans Cohort Breakdown")
            st.plotly_chart(fig_seg, use_container_width=True)
        else:
            st.info("KMeans segmentation artifact pending.")
            
    with col2:
        st.subheader("Dropout Risk Distribution")
        fig_risk = px.histogram(df, x='dropout_risk_score', nbins=20, title="Cohort Risk Spread", color_discrete_sequence=['#dc2626'])
        st.plotly_chart(fig_risk, use_container_width=True)


#STUDENT INTELLIGENCE WORKSPACE (CORE)

elif page == "2. Student Intelligence Workspace":
    st.title("Student Intelligence Workspace")
    
    if "intervention_history" not in st.session_state:
        st.session_state.intervention_history = []
        
    student_id = st.selectbox("Select Target Student ID", df['id_student'].unique()[:1000])
    base_data = df[df['id_student'] == student_id].iloc[0].to_dict()
    
    #WHAT-IF ENGINE UI
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧪 What-If Simulation")
    st.sidebar.markdown("Modify behaviors to preview risk impacts.")
    
    sim_clicks = st.sidebar.slider("Total VLE Clicks", 0, 5000, int(base_data.get('total_clicks', 0)))
    sim_score = st.sidebar.slider("Average Score (%)", 0, 100, int(base_data.get('average_score', 0)))
    sim_late = st.sidebar.slider("Late Submissions", 0, 10, int(base_data.get('late_submission_count', 0)))
    
    #RECALCULATE FEATURES
    simulated_data = dict(base_data)
    simulated_data['total_clicks'] = sim_clicks
    simulated_data['average_score'] = sim_score
    simulated_data['late_submission_count'] = sim_late
    
    #Native invocation of exact feature math
    simulated_data = recalculate_features(simulated_data)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### A. Student Profile")
        st.write(f"**Segment:** {simulated_data.get('educational_segment', 'Pending')}")
        st.write(f"**Region:** {simulated_data.get('region', 'N/A')}")
        st.write(f"**Total Clicks:** {simulated_data['total_clicks']}")
        st.write(f"**Average Score:** {simulated_data['average_score']:.1f}%")
        st.write(f"**Engagement Ratio:** {simulated_data['engagement_ratio']:.2f}")
        
    with col2:
        st.markdown("### B. & C. Outcome Predictions")
        inf_df = pd.DataFrame([simulated_data])
        inf_df = inf_df.drop(columns=['final_result', 'id_student', 'date_unregistration', 'date_registration', 'cluster_id', 'educational_segment'], errors='ignore')
        for c in inf_df.select_dtypes(include=['object']).columns: inf_df[c] = inf_df[c].astype(str)
        
        try:
            drop_prob = drop_model.predict_proba(inf_df)[0][1]
            perf_pred = perf_model.predict(inf_df)[0]
            
            #History Tracking Logic
            if len(st.session_state.intervention_history) == 0 or st.session_state.intervention_history[-1]['prob'] != drop_prob:
                st.session_state.intervention_history.append({'clicks': sim_clicks, 'score': sim_score, 'prob': drop_prob})
                
            c1, c2 = st.columns(2)
            c1.metric("Predicted Outcome", perf_pred)
            c2.metric("Dropout Risk Probability", f"{drop_prob:.1%}", delta=f"{(drop_prob - st.session_state.intervention_history[0]['prob']):.1%}" if len(st.session_state.intervention_history)>1 else None, delta_color="inverse")
            
            if drop_prob > 0.6: st.markdown(f"<div class='risk-high'>HIGH RISK: Immediate Intervention Required</div>", unsafe_allow_html=True)
            elif drop_prob > 0.3: st.markdown(f"<div style='color:#ca8a04; font-weight:bold; font-size:20px;'>MODERATE RISK: Monitor Engagement</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='risk-low'>LOW RISK: Mentoring Stable</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Inference Engine Error: {e}")
            drop_prob, perf_pred = 0, "Unknown"

    st.markdown("---")
    col3, col4, col5 = st.columns([1, 1, 1])
    
    with col3:
        st.markdown("### D. Weaknesses")
        weaknesses = []
        if simulated_data['low_engagement_flag'] == 1: weaknesses.append("Severe lack of VLE interaction.")
        if simulated_data['low_score_flag'] == 1: weaknesses.append("Failing average assessment scores.")
        if simulated_data['late_submission_ratio'] > 0.3: weaknesses.append("High late submission rate.")
        
        if weaknesses:
            for w in weaknesses: st.markdown(f"<div class='weakness-item'>{w}</div>", unsafe_allow_html=True)
        else:
            st.success("No behavioral weaknesses detected.")
            
    with col4:
        st.markdown("### E. Recommendations")
        recs = recommender.recommend(student_id, top_n=2)
        if "error" not in recs[0]:
            for r in recs: st.markdown(f"- **VLE #{r['site_id']}**<br><span style='font-size:12px; color:#666;'>Reason: {r['reason']}</span>", unsafe_allow_html=True)
        else: st.warning("Matrix offline.")
            
    with col5:
        st.markdown("### 📈 Intervention History")
        for i, hist in enumerate(st.session_state.intervention_history[-3:]):
            st.markdown(f"<div class='history-item'>Step {i+1}: Clicks={hist['clicks']}, Risk={hist['prob']:.1%}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### F. AI Tutor Strategy")
    if st.button("Generate Structured AI Intervention"):
        with st.spinner("AI Mentoring Engine processing..."):
            tutor = GroqTutorAssistant()
            if tutor.client:
                #Structured 7-Section Prompt payload
                prompt = f"""
                Analyze this student:
                1. Profile: {simulated_data.get('educational_segment')}
                2. Engagement: {simulated_data['total_clicks']} clicks (Ratio: {simulated_data['engagement_ratio']:.2f})
                3. Performance: Predicted {perf_pred}
                4. Risk: {drop_prob:.1%} Dropout Probability
                5. Weaknesses: {', '.join(weaknesses) if weaknesses else 'None'}
                6. What-If Simulation: Baseline Risk was {st.session_state.intervention_history[0]['prob']:.1%}. Modified Risk is {drop_prob:.1%}.
                
                Generate a targeted mentoring intervention strategy based on these exact metrics. Mention the Before vs After simulation delta.
                """
                reply = tutor.get_response(prompt)
                st.info(reply)
            else:
                # Native Fallback
                st.warning("Groq API offline. Utilizing Rule-Based Fallback Intervention:")
                st.info(generate_fallback_intervention(drop_prob, ", ".join(weaknesses)))


#COHORT ANALYTICS & 4. AI TUTOR

elif page == "3. Cohort Analytics":
    st.title("Cohort Analytics")
    fig = px.scatter(df.sample(3000, random_state=42), x="engagement_ratio", y="average_score", color="educational_segment", opacity=0.7, title="Engagement vs Score by Learner Archetype")
    st.plotly_chart(fig, use_container_width=True)

elif page == "4. AI Tutor Assistant":
    st.title("General AI Educational Assistant")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Ask a mentoring question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            tutor = GroqTutorAssistant()
            if tutor.client:
                response = tutor.get_response(prompt, chat_history=st.session_state.chat_history[:-1])
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            else:
                st.error("API Offline.")
