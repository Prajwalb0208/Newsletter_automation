# Claude Code SDK Content Collector

Automated collector that fetches Claude Code SDK articles and newsletters every 5 hours and stores them in Redis without human intervention.

## Overview

This project automatically collects and curates content about Claude Code SDK from various sources:
- Official documentation
- Tutorials and guides
- API references
- Articles and newsletters

The collector runs autonomously via GitHub Actions every 5 hours, preventing duplicates and maintaining a clean database of unique URLs.

## Features

- **Automated Collection**: Runs every 5 hours via GitHub Actions
- **Duplicate Prevention**: Smart URL normalization and hash-based deduplication
- **Quality Control**: Validates URL accessibility before storage
- **Redis Storage**: Efficient storage using Upstash Redis
- **Multiple Data Structures**: URLs stored in Sets, Sorted Sets, and Hashes for optimal access
- **Comprehensive Metadata**: Stores title, description, source, and collection timestamp
- **Error Handling**: Robust error handling with detailed logging

## Architecture

```
┌─────────────────┐
│ GitHub Actions  │  (Triggers every 5 hours)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   main.py       │  (Collector script)
│                 │
│ • Web search    │
│ • URL validation│
│ • Deduplication │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Upstash Redis   │  (Data storage)
│                 │
│ • URLs set      │
│ • Metadata hash │
│ • Timeline      │
└─────────────────┘
```

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Subagent_newsletter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file with your Redis credentials:
```env
REDIS_HOST=your-redis-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

4. Run the collector manually:
```bash
python main.py --mode both
```

5. Verify the collection:
```bash
python verify_collection.py
```

## GitHub Actions Deployment

The collector is configured to run automatically via GitHub Actions every 5 hours.

### Setup Steps

1. **Add Repository Secrets**:
   Go to your GitHub repository → Settings → Secrets and variables → Actions

   Add the following secrets:
   - `REDIS_HOST`: Your Upstash Redis host
   - `REDIS_PORT`: Redis port (usually 6379)
   - `REDIS_PASSWORD`: Your Redis password

2. **Enable GitHub Actions**:
   - Go to the "Actions" tab in your repository
   - Enable workflows if prompted

3. **Verify Workflow**:
   - The workflow is located at `.github/workflows/collector.yml`
   - It runs automatically every 5 hours: `0 */5 * * *`
   - You can also trigger it manually via "Actions" → "Claude Code SDK Content Collector" → "Run workflow"

### Workflow Schedule

The collector runs at these times (UTC):
- 00:00, 05:00, 10:00, 15:00, 20:00

You can modify the schedule in `.github/workflows/collector.yml`:
```yaml
schedule:
  - cron: '0 */5 * * *'  # Every 5 hours
```

## Redis Data Structure

### Keys

1. **claude-sdk:urls** (Set)
   - Contains all unique normalized URLs

2. **claude-sdk:url:{hash}** (String)
   - Maps URL hash to full URL

3. **claude-sdk:url:{hash}:metadata** (Hash)
   - Stores metadata for each URL:
     - `url`: Normalized URL
     - `title`: Article/page title
     - `description`: Brief description
     - `source`: Content source
     - `search_query`: Query that found the URL
     - `collected_at`: ISO timestamp
     - `hash`: URL hash

4. **claude-sdk:urls:timeline** (Sorted Set)
   - URLs ordered by collection timestamp

5. **claude-sdk:stats** (Hash)
   - Collection statistics:
     - `last_collection`: Last run timestamp
     - `total_collections`: Total number of runs
     - `last_added_count`: URLs added in last run

## Usage

### Manual Collection

Run the collector manually:
```bash
python main.py --mode both
```

Options:
- `--mode newsletters`: Collect only newsletters
- `--mode articles`: Collect only articles
- `--mode both`: Collect both (default)

### Verify Collection

View all collected URLs and metadata:
```bash
python verify_collection.py
```

### Clear Database

To start fresh (clears all data):
```python
python -c "from redis import Redis; import os; from dotenv import load_dotenv; load_dotenv(); r = Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), password=os.getenv('REDIS_PASSWORD'), ssl=True); [r.delete(k) for k in r.keys('*')]"
```

## Configuration

### Search Queries

Edit the `search_queries` list in `main.py` to customize search terms:
```python
self.search_queries = [
    "Claude Code SDK documentation",
    "Claude Code SDK tutorial",
    # Add more queries...
]
```

### Collection Frequency

Modify the cron schedule in `.github/workflows/collector.yml`:
```yaml
schedule:
  - cron: '0 */5 * * *'  # Change the interval here
```

## Monitoring

### View GitHub Actions Logs

1. Go to your repository → Actions
2. Click on "Claude Code SDK Content Collector"
3. Select a workflow run to view logs

### Check Collection Stats

Run the verification script to see statistics:
```bash
python verify_collection.py
```

## Troubleshooting

### Connection Issues

If you see Redis connection errors:
1. Verify your `.env` file has correct credentials
2. Check Upstash dashboard for Redis status
3. Ensure SSL is enabled (port 6379 with SSL)

### No New URLs Found

This is normal if:
- Recent collection already found all available URLs
- Search queries need expansion
- Sources are temporarily unavailable

### Duplicate Detection

The system normalizes URLs by:
- Converting to lowercase
- Removing 'www.' prefix
- Forcing HTTPS
- Removing URL fragments
- Using SHA256 hash for comparison

## Development

### Project Structure

```
.
├── main.py                    # Main collector script
├── verify_collection.py       # Verification utility
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (local)
├── .github/
│   └── workflows/
│       └── collector.yml      # GitHub Actions workflow
└── .claude/
    └── agents/
        └── ai-newsletter-collector.md  # Agent definition
```

### Adding New Features

1. Modify `main.py` to add new functionality
2. Test locally with `python main.py`
3. Commit and push to trigger automated deployment

## License

[Your License Here]

## Support

For issues or questions, please open an issue in the GitHub repository.
