# Jenkins Pipeline Setup Guide

## Fixing the Git SCM Error

If you see an error like:
```
fatal: couldn't find remote ref refs/heads/master
```

This happens because Jenkins is trying to checkout from Git, but the files are already mounted as volumes.

## Solution: Configure Pipeline Script Directly

### Option 1: Use Pipeline Script (Recommended for Demo)

1. Go to Jenkins → **New Item**
2. Name it `infrastructure-pipeline`
3. Select **Pipeline** (not "Pipeline script from SCM")
4. Click **OK**
5. Scroll down to **Pipeline** section
6. Select **Pipeline script**
7. Copy the entire contents of `cicd/Jenkinsfile` into the script text area
8. Click **Save**

This way, Jenkins will use the files from the mounted volume (`/var/jenkins_home/workspace`) and won't try to checkout from Git.

### Option 2: Disable SCM Checkout

If you want to keep using "Pipeline script from SCM":

1. Edit your pipeline job
2. In **Pipeline** section, under **Additional Behaviours**
3. Add **Skip Default Checkout** behavior
4. This will skip the Git checkout and use mounted files instead

### Option 3: Use Local Git Repository

If you want to use Git SCM properly:

1. Initialize a git repo in your workspace:
   ```bash
   cd /path/to/elastic-hashicorp-searchable-infra-demo
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Configure Jenkins job:
   - **Pipeline script from SCM**
   - **SCM:** Git
   - **Repository URL:** `file:///var/jenkins_home/workspace`
   - **Script Path:** `cicd/Jenkinsfile`

## Updated Jenkinsfile

The Jenkinsfile has been updated to handle SCM checkout gracefully - it will try to checkout, but won't fail if it can't (allowing it to work with mounted volumes).

## Quick Fix for Current Error

If you're seeing the error right now:

1. Edit your pipeline job
2. Change from **Pipeline script from SCM** to **Pipeline script**
3. Copy the contents of `cicd/Jenkinsfile` into the script text area
4. Save and run again

The pipeline will now use the files from the mounted volume and won't try to checkout from Git.

