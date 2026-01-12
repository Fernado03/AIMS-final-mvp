# AIMS Deployment Guide

Follow these steps to deploy your AI Medical Scribe to the cloud.

## Phase 1: MongoDB Atlas (Database)
1.  **Create Cluster**: Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas), sign up, and create a free "Shared" cluster.
2.  **Create User**: In "Database Access", create a database user (e.g., `admin`) and password.
3.  **Network Access**: In "Network Access", add IP Address `0.0.0.0/0` (Allow access from anywhere) to allow Render to connect.
4.  **Get Connection String**:
    -   Click "Connect" on your cluster.
    -   Select "Drivers" -> "Python" -> Version "3.6 or later".
    -   Copy the connection string (e.g., `mongodb+srv://admin:<password>@cluster0...`).
5.  **Local Config**: Paste this into your local `.env` file as `MONGO_URI` (replace `<password>` with your actual password).

## Phase 2: Push Code
Your local changes (including the new deployment config) have been committed.
1.  Push them to your remote repository (GitHub/GitLab):
    ```bash
    git push origin main
    ```

## Phase 3: Render (Backend)
1.  **Create Web Service**: Go to [Render Dashboard](https://dashboard.render.com/), click "New +", and select "Web Service".
2.  **Connect Repo**: Select your `AI-medical-scribe` repository.
3.  **Configuration**:
    -   **Name**: `aims-backend` (or similar)
    -   **Root Directory**: Leave empty (defaults to root).
    -   **Runtime**: Python 3
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn backend.app:app`
4.  **Environment Variables**: Scroll down to "Environment Variables" and add:
    -   `GOOGLE_API_KEY`: (Your Gemini API Key)
    -   `MONGO_URI`: (The MongoDB connection string from Phase 1)
5.  **Deploy**: Click "Create Web Service". Wait for it to go live.
6.  **Copy URL**: Once deployed, copy the service URL (e.g., `https://aims-backend.onrender.com`).

## Phase 4: Vercel (Frontend)
1.  **Import Project**: Go to [Vercel Dashboard](https://vercel.com/dashboard), click "Add New...", and select "Project".
2.  **Select Repo**: Import your `AI-medical-scribe` repository.
3.  **Framework Preset**: Select "Other" (or let it auto-detect).
4.  **Root Directory**: **IMPORTANT**: Click "Edit" and select `frontend` folder.
5.  **Deploy**: Click "Deploy".

## Phase 5: Connect Frontend to Backend
The frontend currently points to `localhost`. You need to point it to your live Render backend.
1.  **Edit Config**: On your local computer, open `frontend/config.js`.
2.  **Update URL**: Change `API_BASE_URL` to your **Render Backend URL** (from Phase 3).
    ```javascript
    const config = {
        API_BASE_URL: "https://your-app-name.onrender.com" // Update this!
    };
    ```
3.  **Push Update**:
    ```bash
    git add frontend/config.js
    git commit -m "Update API URL for production"
    git push origin main
    ```
4.  **Redeploy**: Vercel will automatically redeploy the frontend with the new configuration.

## Done!
Visit your Vercel URL to start using the app.
