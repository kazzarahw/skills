#!/usr/bin/env python3
"""
Wiki Search Script for Cyber Skills Wiki

Provides fast, relevant search across wiki pages with scoring based on
title matches, tag matches, and content matches.

Usage:
    python wiki-search.py --wiki-dir /path/to/wiki --query "SQL injection"
    python wiki-search.py --wiki-dir /path/to/wiki --query "exploit" --max-results 10
    python wiki-search.py --wiki-dir /path/to/wiki --query "nmap" --tags "recon,scanning"
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json


@dataclass
class WikiPage:
    """Represents a wiki page with metadata."""
    path: str
    title: str
    tags: List[str] = field(default_factory=list)
    content: str = ""
    frontmatter: Dict = field(default_factory=dict)
    last_modified: float = 0.0


@dataclass
class SearchResult:
    """Represents a search result with score and metadata."""
    page: WikiPage
    score: float
    match_type: str  # "title", "tag", "content"
    matched_terms: List[str] = field(default_factory=list)
    snippet: str = ""


class WikiSearch:
    """Search implementation for the cyber skills wiki."""

    # Scoring weights
    TITLE_MATCH_SCORE = 3.0
    TAG_MATCH_SCORE = 2.0
    CONTENT_MATCH_SCORE = 1.0

    # Snippet settings
    SNIPPET_LENGTH = 200
    SNIPPET_CONTEXT = 50

    def __init__(self, wiki_dir: str):
        """
        Initialize the wiki search.

        Args:
            wiki_dir: Path to the wiki directory containing markdown files.
        """
        self.wiki_dir = Path(wiki_dir)
        self.pages: List[WikiPage] = []
        self.index_built = False

        if not self.wiki_dir.exists():
            raise FileNotFoundError(f"Wiki directory not found: {wiki_dir}")

    def _build_index(self) -> None:
        """
        Build the search index from wiki pages.

        Extracts frontmatter, tags, and content from all markdown files.
        """
        self.pages = []

        for md_file in self.wiki_dir.rglob("*.md"):
            try:
                page = self._parse_page(md_file)
                self.pages.append(page)
            except Exception as e:
                print(f"Warning: Could not parse {md_file}: {e}", file=sys.stderr)
                continue

        self.index_built = True

    def _parse_page(self, file_path: Path) -> WikiPage:
        """Parse a markdown file into a WikiPage."""
        content = file_path.read_text(encoding='utf-8')
        frontmatter = self._extract_frontmatter(content)

        # Extract title from frontmatter or first heading
        title = frontmatter.get('title', '')
        if not title:
            # Try to find first markdown heading
            heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if heading_match:
                title = heading_match.group(1).strip()
            else:
                title = file_path.stem.replace('-', ' ').replace('_', ' ').title()

        # Extract tags
        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]

        # Get last modified time
        last_modified = file_path.stat().st_mtime

        return WikiPage(
            path=str(file_path.relative_to(self.wiki_dir)),
            title=title,
            tags=tags,
            content=content,
            frontmatter=frontmatter,
            last_modified=last_modified,
        )

    def _extract_frontmatter(self, content: str) -> Dict:
        """
        Extract YAML frontmatter from markdown content.

        Args:
            content: Markdown file content.

        Returns:
            Dictionary of frontmatter key-value pairs.
        """
        frontmatter = {}

        # Match YAML frontmatter between --- markers
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return frontmatter

        yaml_content = match.group(1)

        # Simple YAML parsing (key: value pairs)
        current_key = None
        current_list = []

        for line in yaml_content.split('\n'):
            # Check for list item
            list_match = re.match(r'^\s+-\s+(.+)$', line)
            if list_match and current_key:
                current_list.append(list_match.group(1).strip())
                continue

            # Check for key: value
            kv_match = re.match(r'^(\w[\w-]*):\s*(.*)$', line)
            if kv_match:
                # Save previous list if exists
                if current_key and current_list:
                    frontmatter[current_key] = current_list
                    current_list = []

                key = kv_match.group(1)
                value = kv_match.group(2).strip()

                if value:
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    frontmatter[key] = value
                    current_key = None
                else:
                    # Value might be a list
                    current_key = key

        # Save last list if exists
        if current_key and current_list:
            frontmatter[current_key] = current_list

        return frontmatter

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms."""
        # Convert to lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r'[a-z0-9]+', text)
        return tokens

    def _calculate_score(self, page: WikiPage, query_tokens: List[str]) -> Tuple[float, str, List[str]]:
        """
        Calculate search score for a page.

        Args:
            page: WikiPage to score.
            query_tokens: Tokenized search query.

        Returns:
            Tuple of (score, match_type, matched_terms).
        """
        score = 0.0
        match_type = "content"
        matched_terms = []

        # Check title match
        title_tokens = self._tokenize(page.title)
        title_matches = [t for t in query_tokens if t in title_tokens]
        if title_matches:
            score += self.TITLE_MATCH_SCORE * len(title_matches)
            matched_terms.extend(title_matches)
            match_type = "title"

        # Check tag match
        tag_matches = []
        for tag in page.tags:
            tag_tokens = self._tokenize(tag)
            for qt in query_tokens:
                if qt in tag_tokens:
                    tag_matches.append(qt)
        if tag_matches:
            score += self.TAG_MATCH_SCORE * len(set(tag_matches))
            matched_terms.extend(tag_matches)
            if match_type == "content":
                match_type = "tag"

        # Check content match
        content_lower = page.content.lower()
        content_matches = [t for t in query_tokens if t in content_lower]
        if content_matches:
            score += self.CONTENT_MATCH_SCORE * len(content_matches)
            matched_terms.extend(content_matches)

        return score, match_type, list(set(matched_terms))

    def _generate_snippet(self, page: WikiPage, query_tokens: List[str]) -> str:
        """Generate a content snippet around the first match."""
        content = page.content
        content_lower = content.lower()

        # Find first match position
        first_match_pos = -1
        for token in query_tokens:
            pos = content_lower.find(token)
            if pos != -1 and (first_match_pos == -1 or pos < first_match_pos):
                first_match_pos = pos

        if first_match_pos == -1:
            # No match found, return beginning of content
            return content[:self.SNIPPET_LENGTH].strip()

        # Calculate snippet boundaries
        start = max(0, first_match_pos - self.SNIPPET_CONTEXT)
        end = min(len(content), first_match_pos + self.SNIPPET_LENGTH)

        snippet = content[start:end].strip()

        # Add ellipsis if needed
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Search the wiki for pages matching the query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of SearchResult objects sorted by score.
        """
        if not self.index_built:
            self._build_index()

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        results = []

        for page in self.pages:
            score, match_type, matched_terms = self._calculate_score(page, query_tokens)
            if score > 0:
                snippet = self._generate_snippet(page, query_tokens)
                results.append(SearchResult(
                    page=page,
                    score=score,
                    match_type=match_type,
                    matched_terms=matched_terms,
                    snippet=snippet,
                ))

        # Sort by score (descending)
        results.sort(key=lambda r: r.score, reverse=True)

        return results[:max_results]

    def search_by_tags(self, tags: List[str], max_results: int = 10) -> List[SearchResult]:
        """
        Search the wiki by tags.

        Args:
            tags: List of tags to search for.
            max_results: Maximum number of results to return.

        Returns:
            List of SearchResult objects.
        """
        if not self.index_built:
            self._build_index()

        results = []
        for page in self.pages:
            matching_tags = [t for t in page.tags if any(
                qt in self._tokenize(t) for qt in tags
            )]
            if matching_tags:
                score = self.TAG_MATCH_SCORE * len(matching_tags)
                results.append(SearchResult(
                    page=page,
                    score=score,
                    match_type="tag",
                    matched_terms=matching_tags,
                    snippet="",
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:max_results]

    def get_all_tags(self) -> List[Tuple[str, int]]:
        """Get all tags with their frequency."""
        if not self.index_built:
            self._build_index()

        tag_counts = {}
        for page in self.pages:
            for tag in page.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    def get_stats(self) -> Dict:
        """Get wiki statistics."""
        if not self.index_built:
            self._build_index()

        return {
            "total_pages": len(self.pages),
            "total_tags": len(self.get_all_tags()),
            "indexed": self.index_built,
        }


def format_result(result: SearchResult, index: int) -> str:
    """Format a search result for display."""
    lines = [
        f"\n[{index}] {result.page.title}",
        f"    Path: {result.page.path}",
        f"    Score: {result.score:.1f} ({result.match_type} match)",
    ]

    if result.matched_terms:
        lines.append(f"    Matched: {', '.join(result.matched_terms)}")

    if result.page.tags:
        lines.append(f"    Tags: {', '.join(result.page.tags)}")

    if result.snippet:
        lines.append(f"    Snippet: {result.snippet[:150]}...")

    return "\n".join(lines)


def main():
    """Main entry point for the wiki search script."""
    parser = argparse.ArgumentParser(
        description="Search the cyber skills wiki."
    )
    parser.add_argument(
        "--wiki-dir", "-w",
        required=True,
        help="Path to the wiki directory"
    )
    parser.add_argument(
        "--query", "-q",
        help="Search query"
    )
    parser.add_argument(
        "--tags", "-t",
        help="Search by tags (comma-separated)"
    )
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show wiki statistics"
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="List all available tags"
    )

    args = parser.parse_args()

    try:
        wiki = WikiSearch(args.wiki_dir)

        # Show stats
        if args.stats:
            stats = wiki.get_stats()
            print("Wiki Statistics:")
            print(f"  Total pages: {stats['total_pages']}")
            print(f"  Total tags: {stats['total_tags']}")
            print(f"  Indexed: {stats['indexed']}")
            return

        # List tags
        if args.list_tags:
            tags = wiki.get_all_tags()
            print("Available Tags:")
            for tag, count in tags:
                print(f"  {tag}: {count} pages")
            return

        # Search by tags
        if args.tags:
            tag_list = [t.strip() for t in args.tags.split(",")]
            results = wiki.search_by_tags(tag_list, args.max_results)

            if args.format == "json":
                output = [{
                    "title": r.page.title,
                    "path": r.page.path,
                    "score": r.score,
                    "tags": r.page.tags,
                } for r in results]
                print(json.dumps(output, indent=2))
            else:
                print(f"Found {len(results)} results for tags: {', '.join(tag_list)}")
                for i, result in enumerate(results, 1):
                    print(format_result(result, i))
            return

        # Search by query
        if not args.query:
            parser.error("Either --query, --tags, --stats, or --list-tags is required")

        results = wiki.search(args.query, args.max_results)

        if args.format == "json":
            output = [{
                "title": r.page.title,
                "path": r.page.path,
                "score": r.score,
                "match_type": r.match_type,
                "matched_terms": r.matched_terms,
                "tags": r.page.tags,
                "snippet": r.snippet,
            } for r in results]
            print(json.dumps(output, indent=2))
        else:
            print(f"Found {len(results)} results for: {args.query}")
            for i, result in enumerate(results, 1):
                print(format_result(result, i))

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
