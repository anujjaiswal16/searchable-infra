# Jenkins Pipeline Setup Guide

## Fixing Git SCM Errors

If you see errors like:
```
fatal: couldn't find remote ref refs/heads/master
fatal: not in a git directory
```

This happens because Jenkins is configured to use "Pipeline script from SCM" but:
- The workspace isn't a git repository, OR
- The git repository doesn't have the expected branch

## Solution: Configure Pipeline Script Directly (RECOMMENDED)

### Option 1: Use Pipeline Script (Recommended for Demo)

**This is the easiest solution and recommended for demos.**

1. Go to Jenkins → **Manage Jenkins** → **Manage Plugins**
2. Make sure "Pipeline" plugin is installed
3. Go to Jenkins → **New Item**
4. Name it `infrastructure-pipeline`
5. Select **Pipeline** (NOT "Pipeline script from SCM")
6. Click **OK**
7. Scroll down to **Pipeline** section
8. Under **Definition**, select **Pipeline script**
9. Copy the entire contents of `cicd/Jenkinsfile` into the script text area
10. Click **Save**

**Important:** This way, Jenkins will:
- Use the files from the mounted volume (`/var/jenkins_home/workspace`)
- NOT try to checkout from Git
- Work immediately without any Git setup

### Option 2: Disable SCM Checkout (Alternative)

If you want to keep using "Pipeline script from SCM":

1. Edit your pipeline job (`infrastructure-pipeline`)
2. Scroll to **Pipeline** section
3. Under **Additional Behaviours** → **Add** → **Advanced clone behaviours**
4. Check **Skip Default Checkout**
5. Click **Save**

This will skip the Git checkout and use mounted files instead.

**Note:** Option 1 (Pipeline script) is simpler and recommended.

### Option 3: Initialize Git Repository (If you must use SCM)

If you really want to use "Pipeline script from SCM":

1. Initialize a git repo in your workspace:
   ```bash
   cd /path/to/elastic-hashicorp-searchable-infra-demo
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main  # or master, depending on your default
   ```

2. Configure Jenkins job:
   - **Pipeline script from SCM**
   - **SCM:** Git
   - **Repository URL:** `file:///var/jenkins_home/workspace` (for local) or your GitHub URL
   - **Branches to build:** `*/main` (or `*/master`)
   - **Script Path:** `cicd/Jenkinsfile`

**Note:** This is more complex and not recommended for demos. Use Option 1 instead.

## Updated Jenkinsfile

The Jenkinsfile has been updated to handle SCM checkout gracefully - it will try to checkout, but won't fail if it can't (allowing it to work with mounted volumes).

## Quick Fix for Current Error

If you're seeing the error right now:

1. Edit your pipeline job
2. Change from **Pipeline script from SCM** to **Pipeline script**
3. Copy the contents of `cicd/Jenkinsfile` into the script text area
4. Save and run again

The pipeline will now use the files from the mounted volume and won't try to checkout from Git.

