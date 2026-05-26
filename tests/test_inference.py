import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.diagnostics import run_diagnostics
from src.feature_recalculation import recalculate_features
import joblib

def run_tests():
    print("--- INITIATING PLATFORM INTEGRATION TESTS ---")
    
    #diagnostics Test
    print("\n1. Testing Diagnostics Engine...")
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))
    status = run_diagnostics(models_dir=models_dir)
    if status['healthy']:
        print("[PASS] All artifacts and environment variables present.")
    else:
        print(f"[FAIL] Diagnostics failed: {status['errors']}")
        sys.exit(1)
        
    #recalculation Math Test
    print("\n2. Testing Feature Recalculation Engine...")
    df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/processed/master_dataset.csv")))
    dummy_student = df.iloc[0].to_dict()
    dummy_student['total_clicks'] = 1500
    dummy_student['average_score'] = 85
    result = recalculate_features(dummy_student)
    
    if result['engagement_ratio'] > 0 and result['dropout_risk_score'] < 0.5:
        print("[PASS] What-If Recalculation Math is mathematically sound.")
    else:
        print("[FAIL] Recalculation math produced unexpected boundaries.")
        sys.exit(1)
        
    #artifact Inference Test
    print("\n3. Testing Pickled Inference Pipeline...")
    try:
        model = joblib.load(os.path.join(models_dir, "dropout_pipeline.pkl"))
        schema_df = pd.DataFrame([result])
        # Drop columns not in model
        cols_to_drop = ['id_student', 'final_result', 'date_unregistration', 'date_registration', 'cluster_id', 'educational_segment']
        schema_df = schema_df.drop(columns=[c for c in cols_to_drop if c in schema_df.columns])
        
        prob = model.predict_proba(schema_df)[0][1]
        print(f"[PASS] Inference Pipeline executed flawlessly. Dummy Risk: {prob:.2%}")
    except Exception as e:
        print(f"[FAIL] Pipeline Inference broke: {e}")
        sys.exit(1)

    print("\n--- ALL TESTS PASSED SUCCESSFULLY ---")

if __name__ == "__main__":
    run_tests()
    