#!/usr/bin/env python3
"""
Verification script to display collected Claude Code SDK content from Redis
"""

import os
from redis import Redis
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()


def main():
    """Display all collected URLs and metadata"""
    try:
        # Connect to Redis
        redis_client = Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            ssl=True,
            decode_responses=True
        )

        print("="*70)
        print("CLAUDE CODE SDK COLLECTION - VERIFICATION")
        print("="*70)

        # Get stats
        stats = redis_client.hgetall("claude-sdk:stats")
        if stats:
            print("\nCollection Statistics:")
            print(f"  Last Collection: {stats.get('last_collection', 'N/A')}")
            print(f"  Total Collections: {stats.get('total_collections', 'N/A')}")
            print(f"  Last Added Count: {stats.get('last_added_count', 'N/A')}")

        # Get all URLs
        urls = redis_client.smembers("claude-sdk:urls")
        print(f"\nTotal Unique URLs: {len(urls)}")
        print("\nCollected URLs:")
        print("-"*70)

        # Get timeline for chronological order
        timeline = redis_client.zrange("claude-sdk:urls:timeline", 0, -1, withscores=True)

        for idx, (url_hash, timestamp) in enumerate(timeline, 1):
            # Get the URL
            url = redis_client.get(f"claude-sdk:url:{url_hash}")

            # Get metadata
            metadata_key = f"claude-sdk:url:{url_hash}:metadata"
            metadata = redis_client.hgetall(metadata_key)

            print(f"\n{idx}. URL: {url}")
            if metadata:
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   Source: {metadata.get('source', 'N/A')}")
                print(f"   Description: {metadata.get('description', 'N/A')}")
                print(f"   Collected: {metadata.get('collected_at', 'N/A')}")
                print(f"   Search Query: {metadata.get('search_query', 'N/A')}")

        print("\n" + "="*70)
        print(f"[OK] Verification completed - {len(urls)} URLs in database")
        print("="*70)

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        raise


if __name__ == '__main__':
    main()
