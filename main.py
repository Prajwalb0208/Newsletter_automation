#!/usr/bin/env python3
"""
AI Newsletter Collector - Claude Code SDK Focus
Automated collector for Claude Code SDK articles and newsletters
Runs every 5 hours and stores results in Redis
"""

import os
import sys
import hashlib
import argparse
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from typing import List, Dict, Set
import requests
from redis import Redis
from dotenv import load_dotenv
import time
import json

# Load environment variables
load_dotenv()


class ClaudeCodeSDKCollector:
    """Collector specialized for Claude Code SDK content"""

    def __init__(self):
        self.redis_client = self._init_redis()
        self.search_queries = [
            "Claude Code SDK documentation",
            "Claude Code SDK tutorial",
            "Claude Code SDK guide",
            "Claude Code SDK API",
            "Claude Code SDK examples",
            "Anthropic Claude Code SDK",
            "Claude Code SDK newsletter",
            "Claude Code SDK articles"
        ]
        self.collected_urls = []
        self.duplicates_filtered = 0
        self.new_urls_added = 0
        self.errors = []

    def _init_redis(self) -> Redis:
        """Initialize Redis connection with Upstash"""
        try:
            redis_host = os.getenv('REDIS_HOST')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')

            if not all([redis_host, redis_password]):
                raise ValueError("Redis credentials not found in environment")

            client = Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                ssl=True,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )

            # Test connection
            client.ping()
            print(f"[OK] Connected to Redis at {redis_host}")
            return client

        except Exception as e:
            print(f"[ERROR] Redis connection failed: {e}")
            raise

    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent duplicate detection"""
        try:
            parsed = urlparse(url)

            # Remove www prefix
            netloc = parsed.netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]

            # Force https
            scheme = 'https'

            # Remove trailing slash from path
            path = parsed.path.rstrip('/')

            # Remove common tracking parameters
            # For now, we'll keep all query parameters but could filter later

            normalized = urlunparse((
                scheme,
                netloc,
                path,
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))

            return normalized

        except Exception as e:
            self.errors.append(f"URL normalization error: {e}")
            return url

    def get_url_hash(self, url: str) -> str:
        """Generate consistent hash for URL"""
        normalized = self.normalize_url(url)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def is_duplicate(self, url: str) -> bool:
        """Check if URL already exists in Redis"""
        try:
            url_hash = self.get_url_hash(url)
            key = f"claude-sdk:url:{url_hash}"
            exists = self.redis_client.exists(key)

            # Also check the main set
            normalized = self.normalize_url(url)
            in_set = self.redis_client.sismember("claude-sdk:urls", normalized)

            return exists or in_set

        except Exception as e:
            self.errors.append(f"Duplicate check error: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """Validate URL accessibility and relevance"""
        try:
            # Quick HEAD request to check if URL is accessible
            response = requests.head(
                url,
                timeout=10,
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ClaudeCodeSDKCollector/1.0)'}
            )

            if response.status_code == 405:  # HEAD not allowed, try GET
                response = requests.get(url, timeout=10, stream=True)
                response.close()

            return response.status_code < 400

        except Exception as e:
            self.errors.append(f"URL validation error for {url}: {e}")
            return False

    def store_url(self, url: str, metadata: Dict) -> bool:
        """Store URL and metadata in Redis"""
        try:
            normalized_url = self.normalize_url(url)
            url_hash = self.get_url_hash(url)

            # Store in multiple structures for efficient access
            # 1. Main set of URLs
            self.redis_client.sadd("claude-sdk:urls", normalized_url)

            # 2. Metadata hash
            metadata_key = f"claude-sdk:url:{url_hash}:metadata"
            metadata['url'] = normalized_url
            metadata['collected_at'] = datetime.utcnow().isoformat()
            metadata['hash'] = url_hash

            self.redis_client.hset(metadata_key, mapping=metadata)

            # 3. Sorted set by timestamp for chronological access
            timestamp = int(datetime.utcnow().timestamp())
            self.redis_client.zadd("claude-sdk:urls:timeline", {url_hash: timestamp})

            # 4. Store URL by hash for quick lookup
            self.redis_client.set(f"claude-sdk:url:{url_hash}", normalized_url)

            self.new_urls_added += 1
            return True

        except Exception as e:
            self.errors.append(f"Storage error: {e}")
            return False

    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Simulated web search for Claude Code SDK content.
        In production, this would integrate with actual search APIs or scraping.
        """
        # This is a placeholder - in real implementation, you'd use:
        # - Google Custom Search API
        # - Bing Search API
        # - Web scraping of known AI newsletter sites
        # - RSS feeds from tech blogs

        print(f"  Searching for: '{query}'")

        # For demonstration, returning some known Claude Code SDK resources
        sample_results = [
            {
                'url': 'https://docs.claude.com/claude-code/sdk/introduction',
                'title': 'Claude Code SDK Introduction',
                'description': 'Official documentation for Claude Code SDK',
                'source': 'Anthropic Docs'
            },
            {
                'url': 'https://docs.claude.com/claude-code/sdk/getting-started',
                'title': 'Getting Started with Claude Code SDK',
                'description': 'Quick start guide for Claude Code SDK',
                'source': 'Anthropic Docs'
            },
            {
                'url': 'https://docs.claude.com/claude-code/sdk/api-reference',
                'title': 'Claude Code SDK API Reference',
                'description': 'Complete API reference for Claude Code SDK',
                'source': 'Anthropic Docs'
            },
            {
                'url': 'https://github.com/anthropics/claude-code-sdk',
                'title': 'Claude Code SDK - GitHub',
                'description': 'Official Claude Code SDK repository',
                'source': 'GitHub'
            },
            {
                'url': 'https://www.anthropic.com/news/claude-code-sdk',
                'title': 'Announcing Claude Code SDK',
                'description': 'Official announcement of Claude Code SDK',
                'source': 'Anthropic News'
            }
        ]

        # In production, you'd return actual search results here
        # For now, return sample results with some variation
        return sample_results[:max_results]

    def collect_from_sources(self, mode: str = 'both') -> None:
        """Main collection logic"""
        print(f"\nStarting collection cycle at {datetime.utcnow().isoformat()}")
        print(f"Mode: {mode}")
        print(f"Target: Claude Code SDK content\n")

        sources_queried = 0
        urls_discovered = 0

        # Execute searches
        for query in self.search_queries:
            sources_queried += 1

            try:
                results = self.search_web(query, max_results=5)

                for result in results:
                    url = result.get('url')
                    if not url:
                        continue

                    urls_discovered += 1

                    # Check for duplicates
                    if self.is_duplicate(url):
                        print(f"  [SKIP] Duplicate: {url}")
                        self.duplicates_filtered += 1
                        continue

                    # Validate URL (check if accessible)
                    print(f"  [NEW] New URL found: {url}")
                    if self.validate_url(url):
                        # Store in Redis
                        metadata = {
                            'title': result.get('title', ''),
                            'description': result.get('description', ''),
                            'source': result.get('source', ''),
                            'search_query': query
                        }

                        if self.store_url(url, metadata):
                            print(f"    [OK] Stored successfully")
                            self.collected_urls.append(url)
                        else:
                            print(f"    [ERROR] Storage failed")
                    else:
                        print(f"    [ERROR] Validation failed")

            except Exception as e:
                self.errors.append(f"Search error for '{query}': {e}")
                print(f"  [ERROR] Search failed: {e}")

            # Brief delay between searches
            time.sleep(1)

        # Print summary
        self.print_summary(sources_queried, urls_discovered)

    def print_summary(self, sources_queried: int, urls_discovered: int) -> None:
        """Print collection summary"""
        print("\n" + "="*60)
        print("COLLECTION CYCLE SUMMARY")
        print("="*60)
        print(f"Timestamp:           {datetime.utcnow().isoformat()}")
        print(f"Target:              Claude Code SDK")
        print(f"Sources Queried:     {sources_queried}")
        print(f"URLs Discovered:     {urls_discovered}")
        print(f"Duplicates Filtered: {self.duplicates_filtered}")
        print(f"New URLs Added:      {self.new_urls_added}")

        try:
            total_urls = self.redis_client.scard("claude-sdk:urls")
            print(f"Total URLs in DB:    {total_urls}")
        except:
            print(f"Total URLs in DB:    Unknown (Redis error)")

        print(f"Redis Connection:    [ACTIVE]")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")
        else:
            print("\nErrors:              None")

        print("="*60)

        # Update collection metadata
        try:
            self.redis_client.hset("claude-sdk:stats", mapping={
                'last_collection': datetime.utcnow().isoformat(),
                'total_collections': self.redis_client.hincrby("claude-sdk:stats", 'total_collections', 1),
                'last_added_count': self.new_urls_added
            })
        except Exception as e:
            print(f"Failed to update stats: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Claude Code SDK Newsletter & Article Collector'
    )
    parser.add_argument(
        '--mode',
        choices=['newsletters', 'articles', 'both'],
        default='both',
        help='Collection mode (default: both)'
    )

    args = parser.parse_args()

    try:
        collector = ClaudeCodeSDKCollector()
        collector.collect_from_sources(mode=args.mode)

        print("\n[SUCCESS] Collection completed successfully!")
        sys.exit(0)

    except Exception as e:
        print(f"\n[FAILED] Collection failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
