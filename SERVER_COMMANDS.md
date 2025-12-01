# How to Access Your Server & Run Commands

## 1. Find Your Credentials
1.  Go to your **Cloudways Platform**.
2.  Click on **Applications** and select your new application (`pavilion-dev`).
3.  Look at the **Access Details** section (usually the first screen).
4.  You will see:
    *   **Public IP**: (e.g., `123.45.67.89`)
    *   **Username**: (e.g., `master_xxxx`)
    *   **Password**: (Click to view/copy)

## 2. Connect to the Server
You have two options:

### Option A: Use the Cloudways Web Terminal (Easiest)
1.  On the **Access Details** page, look for a button that says **"Launch SSH Terminal"** (usually on the right side).
2.  It will open a new window.
3.  Enter the **Username** and **Password** when prompted.

### Option B: Use Your Computer's Terminal
1.  Open **Terminal** (Mac) or **Command Prompt/PowerShell** (Windows).
2.  Type the following command (replace with your actual details):
    ```bash
    ssh username@public_ip
    ```
    *Example: `ssh master_user@123.45.67.89`*
3.  Press **Enter**.
4.  Type "yes" if asked about authenticity.
5.  Paste your **Password** (Note: You won't see the cursor move when typing the password).
6.  Press **Enter**.

---

# Server Setup Commands (Run these after connecting)

## 1. Navigate to Your App Folder
You need to find your application folder name. List the directories to see it:
```bash
ls applications
```
*You will see a folder name like `qweasdzxc`. That is your App ID.*

Enter that folder:
```bash
cd applications/[YOUR_APP_ID]/public_html/backend
```

## 2. Set up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn (Web Server)
pip install gunicorn
```

## 3. Create Environment File
```bash
nano .env
```
**Paste the following into the file (Right-click to paste):**
```env
# Security
DEBUG=False
SECRET_KEY=generate-a-random-key-here
ALLOWED_HOSTS=dev.pavilionend.in

# Subdirectory Config
FORCE_SCRIPT_NAME=/super-admin

# Database (Update with your Cloudways DB credentials)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://dev.pavilionend.in
```
*Press `Ctrl+X`, then `Y`, then `Enter` to save.*

## 4. Run Database Setup
```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## 5. Build Frontend
```bash
# Go to frontend folder
cd ../frontend

# Install dependencies
npm install

# Create production env
echo "VITE_API_BASE_URL=/super-admin/api/" > .env.production

# Build
npm run build
```
