# Switching to MySQL on Cloudways

Since PostgreSQL is not available on your server, we are switching to MySQL (MariaDB).

## 1. Push Changes to Git
I have updated your `settings.py` and `requirements.txt` locally. You need to commit and push these changes.

```bash
git add .
git commit -m "Switch to MySQL support"
git push origin main
```

## 2. Pull Changes on Cloudways
Go to the Cloudways Dashboard -> **Deployment via Git** -> Click **Pull**.

## 3. Update Server Configuration (SSH)

Log in to your server via SSH and run these commands:

### A. Install MySQL Client
You need to install the system library for MySQL first.
*(Note: Cloudways usually has `default-libmysqlclient-dev` installed. If the pip install fails, we might need a workaround, but try this first).*

```bash
cd applications/hhqskhwyah/public_html/backend
source venv/bin/activate
pip install -r requirements.txt
```

### B. Update .env File
Edit your `.env` file to use MySQL.

```bash
nano .env
```

**Change these lines:**
```env
DB_ENGINE=mysql
DB_PORT=3306
DB_HOST=127.0.0.1
```
*(Keep DB_NAME, DB_USER, and DB_PASSWORD as they are).*

### C. Run Migrations
```bash
python manage.py migrate
```

If this works, you are good to go!
