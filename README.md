# Seshat AI - Educational Intelligence Workspace

An end-to-end Machine Learning ecosystem designed to act as an AI-powered Educational Mentoring Simulator. The platform natively predicts dropout risk, forecasts academic performance, segments learner behavior, and utilizes a large language model (Llama-3.1) to generate explicitly structured intervention strategies.

## System Architecture

```mermaid
flowchart TD
    subgraph Data Layer
        A[(Raw OULAD CSVs)] --> B[Notebook 01: Native EDA]
        B --> C[Notebook 02: Explicit Aggregation]
        C --> D[(Processed CSVs)]
    end

    subgraph Native ML Engine
        D --> E[Notebook 03: Benchmarking & KMeans]
        D --> F[Notebook 04: Hybrid Recommender]
        E --> G[(CatBoost / LightGBM .pkl)]
        E --> H[{feature_schema.json}]
        F --> I[(recommender_matrix.pkl)]
    end

    subgraph Inference & UI Layer
        G --> J[app/main.py - Streamlit]
        I --> J
        H --> K[src/diagnostics.py]
        K --> J
        
        L[Mentor What-If Sliders] --> M[src/feature_recalculation.py]
        M --> J
        
        J --> N[7-Section Structured Prompt]
        N --> O((Groq Llama-3.1))
        O --> P[Actionable Mentoring Strategy]
    end
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#bbf,stroke:#333,stroke-width:2px
    style O fill:#bfb,stroke:#333,stroke-width:2px
```

## Platform Features
1. **Interactive What-If Simulation**: Mentors can use sliders to adjust a student's engagement levels (e.g. Clicks, Average Scores). `src/feature_recalculation.py` dynamically recreates the exact math used during Model Training to instantly render a new Dropout Probability Delta.
2. **KMeans Educational Segmentation**: Students are clustered into archetypes (e.g., *Highly Engaged Achievers*, *Silent Dropout Risk*) natively in the modeling layer, which the Streamlit Cohort Analytics page leverages for deep visual breakdowns.
3. **Structured AI Mentoring**: The Groq API is not fed raw data dumps. The platform constructs a rigid 7-section prompt, forcing the LLM to interpret the *Before vs After* Delta of the What-If simulation to explain exact educational strategies.
4. **Resilient Diagnostics**: `src/diagnostics.py` protects the platform from silent crashes by validating `.pkl` schemas, metadata schemas, and API connectivity before boot.

## Setup Instructions

**1. Environment:**
```bash
python -m venv edu_env
edu_env\Scripts\activate
pip install -r requirements.txt
```

**2. Generate Native ML Artifacts:**
Execute the notebooks to natively generate the intermediate datasets and Scikit-Learn/CatBoost pipelines.
```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb
```

**3. Launch the Intelligence Workspace:**
```bash
streamlit run app/main.py
```
