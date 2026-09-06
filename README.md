# robotdegilim.xyz - Backend

The core backend API and asynchronous data scraping engine for **robotdegilim.xyz**.

## 📚 Developer Onboarding

New to the project? Please read our comprehensive setup guide to get your local environment configured and running in under 5 minutes:

👉 **[Getting Started Guide](docs/GETTING_STARTED.md)**

Once your local environment is running, check out our CI/CD pipeline guide to understand how this backend is shipped to production automatically:

👉 **[Deployment Guide](docs/DEPLOYMENT.md)**

## 🛠️ Tech Stack

This project is built for speed and reliability, using modern industry standards:
- **Framework:** FastAPI (Python)
- **Package Manager:** uv
- **Scraping Engine:** BeautifulSoup4 + curl_cffi (Anti-bot bypass)
- **State & Queues:** AWS S3 (Serverless Architecture)
- **Deployment:** Fly.io (Isolated Process Groups)
