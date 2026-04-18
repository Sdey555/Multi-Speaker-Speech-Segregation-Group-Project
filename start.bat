@echo off
cd /d "%~dp0"

:: Lauch Loader Window
start powershell -WindowStyle Hidden -Command ^
"Add-Type -AssemblyName System.Windows.Forms; ^
Add-Type -AssemblyName System.Drawing; ^
$form = New-Object System.Windows.Forms.Form; ^
$form.Text = 'Starting Project'; ^
$form.Size = New-Object System.Drawing.Size(300,120); ^
$form.StartPosition = 'CenterScreen'; ^
$form.TopMost = $true; ^
$label = New-Object System.Windows.Forms.Label; ^
$label.Text = 'Launching Speaker Segregation...'; ^
$label.AutoSize = $true; ^
$label.Location = New-Object System.Drawing.Point(30,40); ^
$form.Controls.Add($label); ^
$form.Show(); ^
while ($true) { Start-Sleep -Seconds 1 }"

echo =====================================
echo Setting up environment...
echo =====================================

:: Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =====================================
echo Running project...
echo =====================================

:: Popup before main execution
powershell -Command "[System.Windows.MessageBox]::Show('Running main pipeline now...', 'Processing', 'OK', 'Information')"

python main.py

echo.
echo Done!

:: Final popup
powershell -Command "[System.Windows.MessageBox]::Show('Project execution completed!', 'Finished', 'OK', 'Information')"

pause