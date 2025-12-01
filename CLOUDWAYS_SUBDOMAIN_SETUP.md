# Cloudways Subdomain Setup Guide for dev.pavilionend.in

This guide covers the specific steps to create a new application on Cloudways for your subdomain `dev.pavilionend.in` and link it to your existing setup.

## 1. Create a New Application

Since you already have a server, you don't need a new one. You will add a new application to your existing server.

1.  Log in to your **Cloudways Platform**.
2.  Go to **Servers** and click on your target server.
3.  Click the **www** icon (Applications) in the floating menu or the **Applications** tab.
4.  Click **+ Add Application**.
5.  **Select Application Type**: Choose **Custom App (PHP)** or **Laravel** (this gives you a clean environment to set up Python/Node).
    *   *Note: Do not choose WordPress unless you want another WP site at the root of `dev`.*
6.  **Name Your App**: e.g., `pavilion-dev`.
7.  **Select Project**: Choose your project.
8.  Click **Add Application**.

## 2. Point Domain (DNS)

You need to point the subdomain `dev.pavilionend.in` to this new application.

1.  **Get Server IP**: Note the **Public IP** of your Cloudways server.
2.  **Go to your DNS Provider** (where you bought `pavilionend.in`, e.g., GoDaddy, Namecheap, Cloudflare).
3.  **Add an A Record**:
    *   **Type**: `A`
    *   **Host/Name**: `dev`
    *   **Value/Target**: `[Your Server IP]`
    *   **TTL**: Automatic or 3600

## 3. Configure Domain in Cloudways

Now tell Cloudways to listen for this domain.

1.  In Cloudways, go to **Applications** -> Select your new app (`pavilion-dev`).
2.  Go to **Domain Management**.
3.  In **Primary Domain**, enter: `dev.pavilionend.in`.
4.  Click **Save Changes**.

## 4. Install SSL Certificate

1.  Go to **SSL Certificate** in the application menu.
2.  Select **Let's Encrypt**.
3.  **Email Address**: Your email.
4.  **Domain Name**: `dev.pavilionend.in`.
5.  Click **Install Certificate**.
6.  When asked, select **Enable HTTPS Redirection**.

## 5. Deployment & Configuration

Now that the infrastructure is ready, you need to deploy your code.

### A. Access via SSH
1.  Go to **Access Details** in your application.
2.  Create/Note your **Master Credentials** (Username/Password).
3.  SSH into the server:
    ```bash
    ssh [username]@[server-ip]
    ```
4.  Navigate to your application folder (it will be something like `applications/[app-folder-name]/public_html`).

### B. Upload Code
You can use Git or SFTP.
```bash
# Example using Git
git clone [your-repo-url] .
```

### C. Backend Setup (Django)
Follow the steps in `HOSTING_SETUP_GUIDE.md`:
1.  Set up Virtual Environment.
2.  Install requirements.
3.  Create `.env` file with `FORCE_SCRIPT_NAME=/super-admin`.
4.  Run migrations.
5.  Set up Gunicorn/Supervisor (or use a simple background process for testing).

### D. Frontend Setup (React)
1.  Build your React app locally or on the server as per `HOSTING_SETUP_GUIDE.md`.
2.  Ensure the `dist` folder is in `public_html/frontend/dist`.

### E. Nginx Configuration
This is crucial. You need to edit the Nginx config specifically for this application.

1.  In Cloudways, go to **Application Settings** -> **Nginx Configuration**.
2.  Paste the configuration block provided in `HOSTING_SETUP_GUIDE.md` into the editor.
    *   *Note: Cloudways might restrict direct editing of the main `server` block. If so, you might need to use `.htaccess` (for Apache) or ask support to add the location blocks. However, usually, you can add `location` blocks in the "Advanced" section or via SSH in `nginx.conf` if you have permissions.*

    **Alternative (SSH)**:
    If the panel doesn't allow complex Nginx edits:
    1.  Edit `/home/master/applications/[app-name]/conf/nginx/server.conf` (if it exists) or similar custom include paths.
    2.  Or simply place the `location` blocks in the available configuration area.

## 6. Verification
Visit `https://dev.pavilionend.in/admin` and `https://dev.pavilionend.in/super-admin/admin/` to verify.
