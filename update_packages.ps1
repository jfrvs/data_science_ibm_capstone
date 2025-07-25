<#
.SYNOPSIS
    Updates Python packages in an active virtual environment and freezes requirements
.DESCRIPTION
    This script:
    1. Verifies if a virtual environment is active
    2. Updates core data science packages
    3. Freezes requirements to requirements.txt
.NOTES
    File Name      : update-packages.ps1
    Prerequisite  : Active Python virtual environment
#>

param(
    [string]$REQUIREMENTS_FILE = "docs/requirements.txt"
)

function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if virtual environment is active
if (-not $env:VIRTUAL_ENV) {
    Write-Error "No active virtual environment detected!"
    Write-Host @"
You must activate your virtual environment first. Run:
    .\venv\Scripts\Activate.ps1
Then run this script again.
"@ -ForegroundColor Yellow
    exit 1
}

Write-Info "Active virtual environment: $($env:VIRTUAL_ENV)"

# Core packages to update (modern data science stack)
$CORE_PACKAGES = @(
    # Core
    "pip",
    "setuptools",
    "wheel",
    
    # Data Processing
    "numpy",
    "pandas",
    "scipy",
    "pyarrow",
    "polars",
    
    # Machine Learning
    "scikit-learn",
    "xgboost",
    "lightgbm",
    "catboost",
    
    # Visualization
    "matplotlib",
    "seaborn",
    "plotly",
    
    # App Development
    "streamlit",
    
    # Utilities
    "tqdm",
    "python-dotenv",
    
    # Notebooks
    "jupyter",
    "jupyterlab",
    "ipython"
)

# Update packages
Write-Info "Updating core packages..."
foreach ($package in $CORE_PACKAGES) {
    try {
        $current_version = pip show $package | Select-String "Version:"
        Write-Info "Updating $package ($($current_version -replace 'Version: ',''))..."
        pip install --upgrade $package
    }
    catch {
        Write-Warning "Failed to update $package : $($_.Exception.Message)"
    }
}

# Freeze requirements
Write-Info "Freezing requirements to $REQUIREMENTS_FILE..."
try {
    pip freeze > $REQUIREMENTS_FILE
    $updated_packages = (Get-Content $REQUIREMENTS_FILE).Count
    Write-Success "Saved $updated_packages packages to $REQUIREMENTS_FILE"
}
catch {
    Write-Error "Failed to freeze requirements: $($_.Exception.Message)"
}

Write-Success "Package update process completed!"
Write-Host @"
Review your updated packages:
    1. Check $REQUIREMENTS_FILE for version changes
    2. Test your code with the new versions
    3. Commit the updated $REQUIREMENTS_FILE to version control
"@ -ForegroundColor Magenta