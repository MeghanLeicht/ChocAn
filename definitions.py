import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = "src/choc_an_simulator/reports"
PROVIDER_DIR_CSV = os.path.join(ROOT_DIR, REPORT_DIR, "provider_directory.csv")
# Replace backslashes with forward slashes for display consistency
PROVIDER_DIR_CSV = PROVIDER_DIR_CSV.replace(os.path.sep, "/")
