# Jenkins Pipeline Fixes

## Issues Fixed

### 1. "Bad substitution" Error
**Problem:** Jenkins was using `/bin/sh` which doesn't support bash-specific syntax like `${PIPESTATUS[0]}`.

**Solution:** 
- Removed bash-specific syntax
- Capture command output first, then send to Elasticsearch
- Use Groovy string interpolation instead of shell pipes

### 2. send_raw_logs.py Usage Error
**Problem:** The script was being called incorrectly - it expected 3 arguments for `output` command but only got 2.

**Solution:**
- Updated `send_raw_logs.py` to accept 2 arguments for `output` command (reads from stdin when no file provided)
- Changed pipeline to use Python module import instead of command-line calls for better error handling

### 3. Post Section Error
**Problem:** Same "Bad substitution" error in the post section due to variable interpolation issues.

**Solution:**
- Extract variables to Groovy variables first
- Use proper string interpolation with triple-quoted strings

## Changes Made

### cicd/Jenkinsfile
- **Terraform Init:** Capture output first, then send via Python module
- **Terraform Plan:** Capture output first, then send via Python module  
- **Terraform Apply:** Capture output first, then send via Python module
- **Post Section:** Extract variables before using in shell script

### utils/send_raw_logs.py
- Fixed argument parsing for `output` command to accept 2 arguments (reads from stdin)
- Updated usage message

## Testing

After these fixes, the pipeline should:
1. ✅ Run Terraform init successfully
2. ✅ Send init logs to Elasticsearch
3. ✅ Run Terraform plan successfully
4. ✅ Send plan logs to Elasticsearch
5. ✅ Run Terraform apply successfully
6. ✅ Send apply logs to Elasticsearch
7. ✅ Complete post actions without errors

## Next Steps

1. Commit and push the updated `Jenkinsfile` and `send_raw_logs.py`
2. Re-run the Jenkins pipeline
3. Verify logs appear in Elasticsearch

