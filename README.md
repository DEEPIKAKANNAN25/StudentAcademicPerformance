# Student Academic Performance Analysis

## Project Overview
This project analyses a student academic-performance dataset to uncover the
factors that influence academic achievement and placement outcomes.  
Key areas covered: grade distributions, skill scores, attendance, backlogs,
and placement probability.

## Dataset
**Source (Kaggle):**  
https://www.kaggle.com/datasets/student-academic-performance

Place the raw file in the project root as `student_data.csv`  
(the analysis script also accepts `student_dataset.csv`).

## Repository Structure
```
.
├── student_data.csv                          # raw dataset
├── requirements.txt                          # Python dependencies
├── generate_submission.py                    # generates all artefacts
├── YourName_StudentAcademicPerformance.py    # main analysis script
├── YourName_ProjectReport.docx               # full project report
├── score_distribution.png                    # generated chart
└── correlation_matrix.png                    # generated chart
```

## Setup & Execution

### 1 · Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2 · Install dependencies
```bash
pip install -r requirements.txt
```

### 3 · Run the analysis
```bash
python YourName_StudentAcademicPerformance.py
```

### 4 · (Optional) Regenerate all artefacts
```bash
python generate_submission.py
```

## Outputs
| File | Description |
|---|---|
| `score_distribution.png` | Distribution of CGPA, exam & skill scores |
| `correlation_matrix.png` | Pearson correlation heat-map of numeric features |
| `YourName_ProjectReport.docx` | Full written report with embedded charts |
