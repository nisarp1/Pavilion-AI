# Adding Cloudways SSH Key to Your Git Provider

You have downloaded the SSH public key from Cloudways. To allow Cloudways to access your repository, you need to add this key to your Git provider (GitHub, GitLab, or Bitbucket).

## Prerequisite: Get the Key Content
1.  Locate the downloaded SSH key file on your computer (it often has a `.pub` extension or no extension).
2.  Open this file with a text editor (like Notepad, TextEdit, VS Code).
3.  **Copy the entire content**. It usually starts with `ssh-rsa` and ends with a comment or email.

---

## Option 1: GitHub

1.  Log in to your GitHub account.
2.  **For a specific repository (Recommended for security):**
    *   Go to your repository page.
    *   Click **Settings** (top tab).
    *   Click **Deploy keys** (left sidebar).
    *   Click **Add deploy key**.
    *   **Title**: Enter something like "Cloudways Production".
    *   **Key**: Paste the copied key content here.
    *   (Optional) Check "Allow write access" if you want Cloudways to be able to push changes (usually not needed for deployment).
    *   Click **Add key**.

3.  **For your entire account (Alternative):**
    *   Click your profile photo (top right) -> **Settings**.
    *   Click **SSH and GPG keys** (left sidebar).
    *   Click **New SSH key**.
    *   **Title**: "Cloudways Server".
    *   **Key Type**: Authentication Key.
    *   **Key**: Paste the content.
    *   Click **Add SSH key**.

---

## Option 2: GitLab

1.  Log in to GitLab.
2.  **For a specific repository:**
    *   Go to your project.
    *   Go to **Settings** -> **Repository**.
    *   Expand **Deploy keys**.
    *   **Title**: "Cloudways".
    *   **Key**: Paste the key content.
    *   Click **Add key**.

3.  **For your account:**
    *   Click your avatar -> **Preferences** (or Settings).
    *   Click **SSH Keys** (left sidebar).
    *   **Key**: Paste the content.
    *   **Title**: "Cloudways".
    *   Click **Add key**.

---

## Option 3: Bitbucket

1.  Log in to Bitbucket.
2.  **For a specific repository:**
    *   Go to your repository.
    *   Click **Repository settings**.
    *   Click **Access keys**.
    *   Click **Add key**.
    *   **Label**: "Cloudways".
    *   **Key**: Paste the content.
    *   Click **Add key**.

3.  **For your account:**
    *   Click your avatar -> **Personal settings**.
    *   Click **SSH keys**.
    *   Click **Add key**.
    *   Paste and save.

---

## Next Steps in Cloudways

1.  Go back to the **Deployment via Git** section in Cloudways.
2.  Paste your **Repository Address** (SSH format is best, e.g., `git@github.com:username/repo.git`).
3.  Click **Authenticate**.
4.  Select the **Branch** you want to deploy (e.g., `main` or `master`).
5.  Click **Start Deployment**.
