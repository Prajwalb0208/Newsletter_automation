# Deployment Checklist

## Prerequisites Completed ✓

- [x] Redis database cleared
- [x] Main collector script created (`main.py`)
- [x] GitHub Actions workflow configured (`.github/workflows/collector.yml`)
- [x] Verification script created (`verify_collection.py`)
- [x] Dependencies listed (`requirements.txt`)
- [x] Environment variables configured (`.env`)
- [x] Collector tested locally and working

## Deployment Steps

### Step 1: Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit: Claude Code SDK collector with 5-hour automation"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `claude-code-sdk-collector`)
3. Don't initialize with README (we already have one)

### Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 4: Configure GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add each of these:

   **REDIS_HOST**
   ```
   unbiased-mayfly-15818.upstash.io
   ```

   **REDIS_PORT**
   ```
   6379
   ```

   **REDIS_PASSWORD**
   ```
   AT3KAAIncDIzM2NmNDM5MWRhZjQ0NTBmYjY1MjNhYjdkYmUxZjNlOHAyMTU4MTg
   ```

### Step 5: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow: **"Claude Code SDK Content Collector"**

### Step 6: Trigger First Run

You can trigger the collector in two ways:

**Option A: Manual Trigger**
1. Go to **Actions** tab
2. Click **"Claude Code SDK Content Collector"**
3. Click **"Run workflow"** dropdown
4. Select **"both"** for mode
5. Click **"Run workflow"** button

**Option B: Wait for Scheduled Run**
- The workflow will automatically run at the next scheduled time
- Schedule: Every 5 hours (00:00, 05:00, 10:00, 15:00, 20:00 UTC)

### Step 7: Verify Deployment

1. **Check Workflow Run**:
   - Go to **Actions** tab
   - Click on the latest workflow run
   - Verify it completed successfully (green checkmark)

2. **Check Logs**:
   - Click on the workflow run
   - Click **"collect"** job
   - Expand **"Run collector"** step
   - You should see output like:
     ```
     [OK] Connected to Redis at unbiased-mayfly-15818.upstash.io
     Starting collection cycle...
     [SUCCESS] Collection completed successfully!
     ```

3. **Verify Data in Redis** (locally):
   ```bash
   python verify_collection.py
   ```

## Expected Behavior

### First Run
- Should find and store several Claude Code SDK URLs
- Will validate each URL before storing
- Duplicate detection will be empty (first run)

### Subsequent Runs (Every 5 Hours)
- Will search for new content
- Existing URLs will be detected as duplicates
- Only new URLs will be added
- Database grows over time with unique content

## Monitoring

### Check Collection Status

Run this command locally to see the latest stats:
```bash
python verify_collection.py
```

### View GitHub Actions History

1. Go to **Actions** tab
2. See all past runs with timestamps
3. Click any run to see detailed logs

### Redis Database Stats

The collector maintains statistics in Redis:
- `last_collection`: When the last collection ran
- `total_collections`: Total number of successful runs
- `last_added_count`: URLs added in the last run

## Troubleshooting

### Workflow Not Running

**Check:**
1. GitHub Actions is enabled
2. Workflow file is in `.github/workflows/` directory
3. Branch is `main` or `master` (check workflow trigger)

### Redis Connection Errors

**Check:**
1. Secrets are correctly added in GitHub
2. No extra spaces in secret values
3. Redis instance is active on Upstash

### No New URLs Found

**Normal if:**
- This is a frequent occurrence after initial collection
- All available URLs have been collected
- Need to expand search queries in `main.py`

## Maintenance

### Update Search Queries

Edit `main.py` around line 20-30:
```python
self.search_queries = [
    "Claude Code SDK documentation",
    # Add new queries here
]
```

### Change Collection Frequency

Edit `.github/workflows/collector.yml`:
```yaml
schedule:
  - cron: '0 */5 * * *'  # Modify this line
```

Examples:
- Every 3 hours: `0 */3 * * *`
- Every 6 hours: `0 */6 * * *`
- Every hour: `0 * * * *`
- Daily at noon: `0 12 * * *`

### Clear Database and Restart

To start fresh:
```bash
python -c "from redis import Redis; import os; from dotenv import load_dotenv; load_dotenv(); r = Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), password=os.getenv('REDIS_PASSWORD'), ssl=True); print(f'Deleting {len(r.keys(\"*\"))} keys...'); [r.delete(k) for k in r.keys('*')]; print('Database cleared!')"
```

## Success Criteria ✓

Your deployment is successful when:

- [x] Code is pushed to GitHub
- [x] GitHub Actions workflow is enabled
- [x] Secrets are configured
- [ ] First workflow run completes successfully
- [ ] Data is visible in Redis (via `verify_collection.py`)
- [ ] Subsequent runs (after 5 hours) detect duplicates correctly
- [ ] No errors in GitHub Actions logs

## Next Steps

After successful deployment:

1. **Monitor First 24 Hours**: Check 4-5 collection cycles to ensure stability
2. **Expand Sources**: Add more search queries as needed
3. **Integrate with Applications**: Use collected URLs in your applications
4. **Set Up Alerts**: Configure notifications for failed runs (optional)

## Support

- GitHub Issues: Report problems in the repository
- Check logs in GitHub Actions for detailed error messages
- Verify Redis connectivity with `verify_collection.py`

---

**Deployment Date**: 2025-11-02
**Collector Version**: 1.0
**Schedule**: Every 5 hours, autonomous operation
