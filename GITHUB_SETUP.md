# GitHub Setup Guide

This guide will help you push your Causal Media/Marketing App to GitHub and prepare it for your portfolio.

## 📦 Initial Setup

### 1. Create a New GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the **+** icon in the top right → **New repository**
3. Fill in the details:
   - **Repository name**: `causal-marketing-app` (or your preferred name)
   - **Description**: "A Streamlit web application for causal inference in media and marketing using DoWhy"
   - **Visibility**: Public (for portfolio) or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **Create repository**

### 2. Initialize Git in Your Project

Open your terminal in the project directory and run:

```bash
cd /Users/caseyhess/datascience/causalapp

# Initialize git (if not already initialized)
git init

# Add all files
git add .

# Make your first commit
git commit -m "Initial commit: Causal Media/Marketing App with DoWhy"

# Rename default branch to main (if needed)
git branch -M main

# Add your GitHub repository as remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/causal-marketing-app.git

# Push to GitHub
git push -u origin main
```

### 3. Verify on GitHub

1. Refresh your GitHub repository page
2. You should see all your files including:
   - ✅ README.md
   - ✅ LICENSE
   - ✅ requirements.txt
   - ✅ app.py
   - ✅ utils/synthetic.py
   - ✅ example_data.csv
   - ✅ .gitignore
   - ✅ CONTRIBUTING.md
   - ✅ CHANGELOG.md

## 🎨 Enhance Your Repository

### Add Topics/Tags

On your GitHub repo page:
1. Click **⚙️ Settings** → **General**
2. Add topics/tags:
   - `streamlit`
   - `causal-inference`
   - `dowhy`
   - `data-science`
   - `marketing-analytics`
   - `python`
   - `data-visualization`

### Create a Repository Description

Edit the "About" section (top right):
- **Description**: "Streamlit web app for causal inference in media/marketing using DoWhy - estimate true ROI of marketing channels"
- **Website**: Add your live demo URL if you deploy it (Streamlit Cloud, Heroku, etc.)
- **Tags**: Same as topics above

### Add a Repository Social Preview

1. Go to **Settings** → **General** → **Social preview**
2. Upload a screenshot of your app (1280x640px recommended)
3. This will be the preview image when sharing your repo

### Enable GitHub Pages (Optional)

If you want to add documentation:
1. Go to **Settings** → **Pages**
2. Select source: Deploy from a branch
3. Choose `main` branch and `/docs` folder (if you create one)

## 📸 Add Screenshots

To make your README more attractive, take screenshots:

### How to Add Screenshots

1. Run your app: `streamlit run app.py`
2. Take screenshots of:
   - Main setup page with synthetic data
   - Analysis results with causal graph
   - Visualizations tab with plots
   - Refutations tab

3. Create a `screenshots` folder in your project:
   ```bash
   mkdir screenshots
   ```

4. Save screenshots as:
   - `screenshots/setup.png`
   - `screenshots/analysis.png`
   - `screenshots/visuals.png`
   - `screenshots/refutations.png`

5. Add them to README by updating the top section:
   ```markdown
   ## 📸 Screenshots
   
   ### Setup Tab
   ![Setup Interface](screenshots/setup.png)
   
   ### Analysis Results
   ![Analysis Results](screenshots/analysis.png)
   
   ### Visualizations
   ![Visualizations](screenshots/visuals.png)
   
   ### Refutation Tests
   ![Refutation Tests](screenshots/refutations.png)
   ```

6. Commit and push:
   ```bash
   git add screenshots/ README.md
   git commit -m "Add: screenshots for documentation"
   git push
   ```

## 🚀 Deploy to Streamlit Cloud (Free)

Make your app live and accessible:

### Prerequisites
- GitHub repository (done ✅)
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Steps

1. **Sign up for Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Authorize Streamlit to access your repositories

2. **Deploy your app**:
   - Click **New app**
   - Select your repository: `YOUR_USERNAME/causal-marketing-app`
   - Main file path: `app.py`
   - Click **Deploy**

3. **Wait for deployment** (2-3 minutes)
   - Streamlit Cloud will install dependencies from `requirements.txt`
   - Your app will be available at: `https://YOUR_USERNAME-causal-marketing-app-xxxxx.streamlit.app`

4. **Update your README**:
   Add a badge and link at the top:
   ```markdown
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR_APP_URL.streamlit.app)
   ```

5. **Update GitHub repo description** with your live app URL

## 📱 For Your Portfolio

### Update Your README Contact Section

Replace the placeholder contact information in README.md:

```markdown
## 📞 Contact & Support

- **Live Demo**: [View App](https://your-app.streamlit.app)
- **GitHub**: [github.com/yourusername/causal-marketing-app](https://github.com/yourusername/causal-marketing-app)
- **Portfolio**: [yourportfolio.com](https://yourportfolio.com)
- **LinkedIn**: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- **Email**: your.email@example.com
```

### Create a Portfolio Entry

Add to your portfolio website:

**Project Title**: Causal Media/Marketing Analytics App

**Description**: 
"Developed a full-stack web application for causal inference in marketing analytics using Python, Streamlit, and Microsoft's DoWhy library. Enables marketers to estimate true ROI of advertising channels by controlling for confounding factors like seasonality and pricing. Implements multiple estimation methods including propensity score matching and implements comprehensive robustness tests."

**Technologies**: 
- Python, Streamlit, DoWhy, Plotly, Pandas, NumPy, NetworkX
- Causal inference, DAGs, backdoor adjustment
- Interactive data visualization
- Statistical modeling

**Key Features**:
- Multiple data source support (CSV, Google Sheets, synthetic)
- Four causal estimation methods
- Interactive causal graph visualization
- Comprehensive refutation tests for validation
- Real-time analysis with confidence intervals

**Links**:
- [Live Demo](https://your-app.streamlit.app)
- [GitHub Repository](https://github.com/yourusername/causal-marketing-app)

## 🎯 LinkedIn Post Template

Share your project on LinkedIn:

```
🚀 Excited to share my latest project: A Causal Inference Web App for Marketing Analytics!

Ever wondered if your marketing campaigns truly cause sales increases, or if it's just correlation? 📊

I built a full-stack web application that helps marketers answer this question using causal inference - going beyond correlation to identify true cause-and-effect relationships.

🔍 Key Features:
✅ Interactive causal modeling with directed acyclic graphs (DAGs)
✅ Multiple estimation methods (propensity score matching, IPW, etc.)
✅ Comprehensive robustness testing
✅ Real-time visualizations with confidence intervals
✅ Built with Python, Streamlit, and Microsoft's DoWhy library

The app handles confounding factors like seasonality and pricing that often mislead traditional analytics, providing more accurate ROI estimates for marketing spend.

💡 Perfect for: Marketing analysts, data scientists, and anyone interested in causal inference!

👉 Try it out: [YOUR_APP_URL]
📂 Code: [GITHUB_URL]

#DataScience #CausalInference #Marketing #Analytics #Python #Streamlit #MachineLearning
```

## ✅ Final Checklist

Before sharing your repository:

- [ ] All files committed and pushed to GitHub
- [ ] README updated with your actual contact information
- [ ] Repository description and topics added
- [ ] LICENSE file present (MIT ✅)
- [ ] .gitignore configured (✅)
- [ ] requirements.txt complete (✅)
- [ ] Example data included (✅)
- [ ] Screenshots added (optional but recommended)
- [ ] Live demo deployed on Streamlit Cloud (optional)
- [ ] Portfolio website updated
- [ ] LinkedIn profile/post created

## 🔐 Security Notes

Your `.gitignore` already excludes:
- Virtual environments (.venv, venv)
- Python cache files (__pycache__)
- Local configuration files
- Personal data files (if added)

**Never commit**:
- API keys or secrets
- Personal data
- Large datasets (use Git LFS or external hosting)
- Credentials or passwords

## 📞 Need Help?

If you encounter issues:
1. Check GitHub's [documentation](https://docs.github.com)
2. Streamlit Cloud [docs](https://docs.streamlit.io/streamlit-community-cloud)
3. Open an issue in your repository

---

**Good luck with your portfolio! 🎉**

Remember to star your own repository and share it with the data science community!

