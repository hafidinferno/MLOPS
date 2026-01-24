import pandas as pd
import os
import datetime

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.test_suite import TestSuite
from evidently.tests import TestNumberOfColumnsWithMissingValues
from evidently import ColumnMapping
from evidently.ui.workspace import Workspace
from evidently.ui.dashboards import DashboardPanelCounter, DashboardPanelPlot, CounterAgg, PlotType, ReportFilter
from evidently.renderers.html_renderer import HtmlRenderer

def create_report():
    print("Loading data for reporting...")
    try:
        ref_data = pd.read_csv('/data/ref_data.csv')
    except Exception as e:
        print(f"Could not load ref_data.csv: {e}")
        return

    # Prod data might be empty or missing initially
    prod_data = None
    if os.path.exists('/data/prod_data.csv'):
        try:
            prod_data = pd.read_csv('/data/prod_data.csv')
        except:
            pass
            
    # If no prod data, we can't generate a drift report comparing Ref vs Prod efficiently yet.
    # But we can initialize the workspace.
    
    ws = Workspace("workspace")
    project = ws.create_project("Fraud Detection Monitoring")
    project.description = "Monitoring model performance and data drift."
    project.save()
    
    if prod_data is not None and len(prod_data) > 0:
        # Define Column Mapping
        # target = 'target'
        # prediction = 'prediction'
        # numerical_features = [c for c in ref_data.columns if c.startswith('PCA_')]
        
        column_mapping = ColumnMapping()
        column_mapping.target = 'target'
        column_mapping.prediction = 'prediction'
        column_mapping.numerical_features = [c for c in ref_data.columns if c.startswith('PCA_')]
        
        # 1. Data Drift Report
        drift_report = Report(metrics=[
            DataDriftPreset(),
        ])
        
        drift_report.run(reference_data=ref_data, current_data=prod_data, column_mapping=column_mapping)
        ws.add_report(project.id, drift_report)
        print("Data Drift report added.")
        
        # 2. Classification Performance (if we have targets in prod)
        # Assuming prod_data has ground truth 'target' coming from feedback
        if 'target' in prod_data.columns and prod_data['target'].notna().sum() > 0:
            classification_report = Report(metrics=[
                ClassificationPreset(),
            ])
            classification_report.run(reference_data=ref_data, current_data=prod_data, column_mapping=column_mapping)
            ws.add_report(project.id, classification_report)
            print("Classification report added.")

    print("Project initialized.")

if __name__ == "__main__":
    create_report()
