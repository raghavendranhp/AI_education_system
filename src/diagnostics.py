import os
import json
import joblib

def run_diagnostics(models_dir='models'):
    """Runs a health check on the ML architecture."""
    status = {'healthy': True, 'errors': []}
    
    # 1. Check Artifacts
    required_files = [
        f'{models_dir}/performance_pipeline.pkl',
        f'{models_dir}/dropout_pipeline.pkl',
        f'{models_dir}/recommender_matrix.pkl',
        f'{models_dir}/kmeans_clusterer.pkl',
        f'{models_dir}/metadata/feature_schema.json'
    ]
    
    for f in required_files:
        if not os.path.exists(f):
            status['healthy'] = False
            status['errors'].append(f"Missing critical artifact: {f}")
            
    # 2. Check API
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv('GROQ_API_KEY'):
        status['healthy'] = False
        status['errors'].append("GROQ_API_KEY missing from .env. AI Tutor will use fallback rules.")
        
    return status

def generate_fallback_intervention(risk_prob, weaknesses):
    """Rule-based fallback if Groq API is down."""
    if risk_prob > 0.6:
        return f"CRITICAL INTERVENTION: Student has a {risk_prob:.1%} chance of dropping out. Focus immediately on resolving: {weaknesses}. Recommend immediate 1-on-1 meeting."
    elif risk_prob > 0.3:
        return f"WARNING: Moderate dropout risk ({risk_prob:.1%}). Monitor closely. Weaknesses: {weaknesses}."
    return "Student is performing adequately. Continue standard mentoring."
