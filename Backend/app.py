import os
import uuid
from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for
from blockchain import Blockchain
from qr_utils import generate_qr

# Absolute paths for templates and static
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)
app.secret_key = "supersecretkey"  # required for session handling

# Initialize blockchain
blockchain = Blockchain()

# Dummy users
users = {
    "farmer1": {"password": "farmer123", "role": "farmer"},
    "processor1": {"password": "proc123", "role": "processor"},
    "lab1": {"password": "lab123", "role": "lab"}
}

ROLE_DETAILS = {
    "farmer": {
        "label": "Farmer",
        "eyebrow": "Origin intake",
        "summary": "Create herb batches with source and harvest details before they move downstream."
    },
    "processor": {
        "label": "Processor",
        "eyebrow": "Processing stage",
        "summary": "Update transformation records and keep the chain transparent after harvest."
    },
    "lab": {
        "label": "Lab Analyst",
        "eyebrow": "Quality assurance",
        "summary": "Attach testing insights and finalize verified batches for consumer trust."
    }
}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("role"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def latest_transaction_for_herb(herb_id):
    for block in reversed(blockchain.chain):
        for tx in reversed(block["transactions"]):
            if tx["herb_id"] == herb_id:
                return tx
    return None


def dashboard_context(role):
    all_transactions = [
        tx
        for block in blockchain.chain
        for tx in block["transactions"]
    ]
    recent_transactions = list(reversed(all_transactions[-5:]))
    herb_ids = sorted({tx["herb_id"] for tx in all_transactions})

    return {
        "role": role,
        "role_details": ROLE_DETAILS.get(role, ROLE_DETAILS["farmer"]),
        "total_blocks": len(blockchain.chain),
        "tracked_herbs": len(herb_ids),
        "recent_transactions": recent_transactions,
    }

# Root redirect to login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Test route
@app.route('/test')
def test():
    return "Flask is working!"

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            flash(f"Welcome back, {username}.", "success")
            return redirect(url_for('dashboard_default'))

        flash("Invalid credentials. Try one of the sample project accounts.", "error")
    return render_template('login.html')

# Dashboard (auto-detect role from session)
@app.route('/dashboard')
@login_required
def dashboard_default():
    role = session.get('role')
    return render_template('dashboard.html', **dashboard_context(role))

# Dashboard with explicit role
@app.route('/dashboard/<role>')
@login_required
def dashboard(role):
    session_role = session.get("role")
    if role != session_role:
        flash("Showing the dashboard for your signed-in role.", "warning")
    return redirect(url_for("dashboard_default"))


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# New herb form
@app.route('/new_herb')
@login_required
def new_herb_form():
    return render_template('new_herb.html')

# Add new herb
@app.route('/add_herb', methods=['POST'])
@login_required
def add_herb():
    herb_name = request.form['herb_name'].strip()
    origin = request.form['origin'].strip()
    harvest_date = request.form['harvest_date']
    farmer_id = request.form['farmer_id'].strip()

    if not all([herb_name, origin, harvest_date, farmer_id]):
        flash("Please fill in all herb intake fields.", "error")
        return redirect(url_for("new_herb_form"))

    herb_id = str(uuid.uuid4())[:8]  # short unique herb ID
    blockchain.new_transaction(
        herb_id, herb_name, origin, harvest_date, farmer_id, status="harvested"
    )
    block = blockchain.new_block(proof=12345)

    return render_template(
        'scan.html',
        block=block,
        qr_code=None,
        headline="Batch Created",
        description="The herb batch is now recorded on-chain and ready for the next traceability step.",
        highlight_id=herb_id,
    )

# Update herb form
@app.route('/update_herb')
@login_required
def update_herb_form():
    return render_template('update_herb.html')

# Update herb step
@app.route('/update_step', methods=['POST'])
@login_required
def update_step():
    herb_id = request.form['herb_id'].strip()
    step = request.form['step']
    processor_id = request.form.get('processor_id', '').strip()
    lab_id = request.form.get('lab_id', '').strip()
    test_results = request.form.get('test_results', '').strip()

    if not herb_id:
        flash("Enter a valid herb ID to continue.", "error")
        return redirect(url_for("update_herb_form"))

    last_tx = latest_transaction_for_herb(herb_id)

    if not last_tx:
        flash("Herb ID not found. Double-check the batch code and try again.", "error")
        return redirect(url_for("update_herb_form"))

    if step == "processor" and not processor_id:
        flash("Processor ID is required for the processing stage.", "error")
        return redirect(url_for("update_herb_form"))

    if step in {"lab", "finalize"} and not lab_id:
        flash("Lab ID is required for lab and finalization steps.", "error")
        return redirect(url_for("update_herb_form"))

    if step in {"lab", "finalize"} and not test_results:
        flash("Add test results before completing this stage.", "error")
        return redirect(url_for("update_herb_form"))

    # Determine status
    if step == "processor":
        status = "processed"
    elif step == "lab":
        status = "tested"
    elif step == "finalize":
        status = "ready_for_sale"
    else:
        status = last_tx.get('current_status', 'harvested')

    # Create new transaction
    blockchain.new_transaction(
        herb_id,
        last_tx['herb_name'],
        last_tx['origin'],
        last_tx['harvest_date'],
        last_tx['farmer_id'],
        processor_id=processor_id or last_tx.get('processor_id',''),
        lab_id=lab_id or last_tx.get('lab_id',''),
        test_results=test_results or last_tx.get('test_results',''),
        status=status
    )

    block = blockchain.new_block(proof=12345)

    # Generate QR only at final step
    qr_path = generate_qr(block, f"qr_{block['index']}.png") if step == "finalize" else None

    return render_template(
        'scan.html',
        block=block,
        qr_code=qr_path,
        headline="Traceability Updated",
        description="The blockchain entry has been refreshed with the latest supply-chain checkpoint.",
        highlight_id=herb_id,
    )

# Run Flask
if __name__ == '__main__':
    app.run(debug=True)
