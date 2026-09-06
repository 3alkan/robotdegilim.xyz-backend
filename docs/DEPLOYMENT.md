# Deployment Guide

This project is configured to deploy to [Fly.io](https://fly.io) using a fully automated GitHub Actions (CI/CD) pipeline. This means you should **never** deploy from your local machine. Instead, pushing to the `main` branch on GitHub will automatically build and release the application.

This backend uses **Fly Process Groups** to run the FastAPI Server and the Background Worker as completely separate, isolated virtual machines from the same Docker image.

---

## 🚀 Initial Setup (One-Time Only)

If you are setting this up for the first time on a new Fly.io account, follow these steps to wire up the GitHub Actions pipeline.

### 1. Initialize the Fly App Locally
First, install the Fly CLI (`flyctl`) and log in. Then, initialize the app to generate your `fly.toml` configuration file:
```bash
fly launch --no-deploy
```
> **IMPORTANT:** Fly will detect the existing `fly.toml` in this repository and ask: *"An existing fly.toml file was found... Would you like to copy its configuration to the new app?"* 
> 
> You must press **`y` (Yes)**. 
> 
> This is crucial because it copies our custom `[processes]` architecture and port settings. Fly will then generate a new App Name for your account, but keep our exact backend architecture intact! If it asks to tweak settings, you can press `n` (No) since the copied configuration is already perfect.

### 2. Set Production Secrets
Our application relies entirely on AWS S3 for its database and queues. Instead of typing them out manually, you can instantly import all your local secrets directly from your `.env` file:
```bash
cat .env | fly secrets import
```

### 3. Generate a Fly API Token
To allow GitHub Actions to deploy on your behalf, generate a secure deployment token:
```bash
fly tokens create deploy -x 999999h
```
Copy the long token output string.

### 4. Add the Token to GitHub Secrets
1. Go to your repository on GitHub.com.
2. Click **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret**.
4. Name the secret exactly `FLY_API_TOKEN`.
5. Paste the token from Step 3 into the value field and save.



## 🪄 Pushing to Production

Once the one-time setup is complete, deploying is completely automated. 

1. Write your code and test it locally.
2. Commit your changes.
3. Push to the `main` branch:
```bash
git push origin main
```

That's it! You can go to the **Actions** tab on your GitHub repository to watch the deployment logs as GitHub builds your Docker image and pushes it to Fly.io.
