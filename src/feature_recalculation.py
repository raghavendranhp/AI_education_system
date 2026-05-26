import pandas as pd
import numpy as np

def recalculate_features(row_dict):
    """
    Takes a dictionary representing a student's metrics, and dynamically
    recalculates all derived features.
    
    Expected Base Keys:
    - total_clicks
    - active_days
    - average_score
    - total_assessments
    - late_submission_count
    - num_unique_sites
    """
    row = dict(row_dict)
    
    # Avoid div by zero
    total_clicks = max(1, float(row.get('total_clicks', 1)))
    total_assessments = max(1, float(row.get('total_assessments', 1)))
    
    # 1. Engagement Features
    row['engagement_ratio'] = min(1.0, float(row.get('active_days', 0)) / 260.0) # Assume 260 day course
    row['avg_daily_clicks'] = total_clicks / max(1, float(row.get('active_days', 1)))
    row['resource_diversity_score'] = float(row.get('num_unique_sites', 1)) / total_clicks
    
    # 2. Assessment Features
    row['late_submission_ratio'] = float(row.get('late_submission_count', 0)) / total_assessments
    row['assessment_completion_rate'] = float(row.get('completed_assessments', total_assessments)) / total_assessments
    
    # 3. Risk Flags
    row['low_engagement_flag'] = 1 if total_clicks < 100 else 0
    row['low_score_flag'] = 1 if float(row.get('average_score', 0)) < 40 else 0
    
    # 4. Dropout Risk Score (Heuristic baseline)
    risk_score = 0
    if row['low_engagement_flag']: risk_score += 0.4
    if row['low_score_flag']: risk_score += 0.4
    if row['late_submission_ratio'] > 0.3: risk_score += 0.2
    row['dropout_risk_score'] = risk_score
    
    return row
