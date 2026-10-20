# Cloud-Based Business Data Analytics and Decision Support System

**Student:** Baisakhi Bhaduri  
**Roll Number:** O2BCA110280  
**University:** Chandigarh University  
**Programme:** BCA, Semester 5

## Project overview
This project analyses the supplied DataServe India client dataset and benchmarks it against Competitor Alpha and Competitor Beta. It includes an interactive Streamlit dashboard, cleaned CSV copies of all source datasets, KPI summaries, grouped analyses, charts, and a written report.

## Technology stack
- Python for data processing and KPI calculations
- Pandas and NumPy for data preparation and aggregation
- Streamlit for the interactive dashboard
- Matplotlib for report charts
- Microsoft Excel source workbooks for input data

## Run the dashboard
1. Install Python 3.10 or newer.
2. Extract the project ZIP to a folder.
3. Open a terminal/Command Prompt in that folder.
4. (Optional but recommended) Create a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Start the app: `streamlit run app.py`
7. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Files
- `app.py`: interactive dashboard source
- `data/`: CSV versions of the three uploaded datasets
- `company_kpi_comparison.csv`: comparison KPIs
- `dataserve_monthly_analysis.csv`: monthly client analysis
- `dataserve_region_analysis.csv`: regional client analysis
- `dataserve_segment_analysis.csv`: mining segment analysis
- `dataserve_service_model_analysis.csv`: service model analysis
- `charts/`: figures included in the report
- `Project_Report.docx` and `Project_Report.pdf`: final project report

## Metric definitions
- Average query time = arithmetic mean of `Avg_Query_Time_Sec`.
- Average uptime = arithmetic mean of `Uptime_Pct`.
- Cost per GB = sum of `Cloud_Cost_INR` divided by sum of `Data_Volume_GB`.
- Data quality and decision effectiveness = arithmetic means of the supplied scores.
- Comparisons are descriptive. Different dataset sizes and workloads mean cost and performance should be interpreted with workload context; the observed relationships do not prove causation.

## Suggested demonstration
1. Open the dashboard and show the KPI cards.
2. Compare all three companies in the benchmarking table.
3. Filter DataServe by month, region, and business unit.
4. Discuss monthly query performance and regional cloud costs.
5. Show mining-segment conversion and service-model performance.
6. Explain the recommendations and limitations.

## Important note
All findings in the report are calculated from the supplied workbooks. No missing values are fabricated. Improvement targets are proposals for future measurement, not achieved results.


## Enhanced dashboard version
The enhanced dashboard uses Plotly for interactive graphs. After extracting the ZIP, install/update the dependencies:
`py -m pip install -r requirements.txt`
Then run:
`py -m streamlit run app.py`
New visualisations include line charts, bar charts, donut chart, scatter plots, box plots, histograms, correlation heatmap, and mining-segment conversion comparisons. Use the tabs and sidebar filters to explore the data.
