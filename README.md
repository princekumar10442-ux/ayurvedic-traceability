Ayurvedic Traceability
A Flask-based traceability dashboard for Ayurvedic herbs that records supply-chain updates on a simple blockchain-like ledger.

Features
Role-based login for farmer, processor, and lab users
Herb batch creation with origin and harvest details
Step-by-step batch updates across processing and lab stages
Final QR code generation for consumer-side verification
Refreshed responsive UI for login, dashboard, forms, and traceability views
Project Structure
backend/
  app.py
  blockchain.py
  qr_utils.py
frontend/
  static/
    style.css
  templates/
    base.html
    dashboard.html
    login.html
    new_herb.html
    scan.html
    update_herb.html
Requirements
Python 3.9+
Flask
qrcode
Pillow
Install dependencies:

python3 -m pip install -r requirements.txt
Run Locally
From the project root:

python3 backend/app.py
Then open:

http://127.0.0.1:5000
Demo Accounts
Farmer: farmer1 / farmer123
Processor: processor1 / proc123
Lab: lab1 / lab123
Workflow
Log in with one of the sample roles.
Farmers create a new herb batch.
Processors and labs update the batch using the generated herb ID.
Finalization generates a QR code for verification.
Notes
The blockchain implementation in this project is educational and lightweight.
Data is stored in memory while the Flask app is running.
QR images are generated into frontend/static/.
