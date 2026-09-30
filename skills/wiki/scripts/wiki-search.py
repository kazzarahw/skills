#!/usr/bin/env python3
"""
wiki-search.py — Search the security wiki by title, tag, and content.

Supports fuzzy matching, relevance ranking, and filtering by page type,
tag, and date range.

Usage:
    python wiki-search.py <wiki_path> [options]

Options:
    --query, -q         Search query string
    --tag, -t           Filter by tag (comma-separated)
    --type, -T          Filter by page type
    --date-from         Filter by start date (YYYY-MM-DD)
    --date-to           Filter by end date (YYYY-MM-DD)
    --status, -s        Filter by status
    --domain, -d        Filter by domain (web2, web3, cross-domain)
    --limit, -n         Maximum number of results (default: 20)
    --format, -f        Output format: text, json (default: text)
    --fuzzy, -F         Enable fuzzy matching (default: True)
    --fuzzy-threshold   Fuzzy match threshold 0.0-1.0 (default: 0.6)
    --no-fuzzy          Disable fuzzy matching
    --search-raw        Also search the raw/ directory
    --verbose, -v       Verbose output
    --help, -h          Show this help message

Examples:
    python wiki-search.py /path/to/wiki -q "SQL injection"
    python wiki-search.py /path/to/wiki -t web2,critical -T concept
    python wiki-search.py /path/to/wiki -q "reentrancy" -d web3 -f json
    python wiki-search.py /path/to/wiki -q "nmap" --search-raw
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set, Tuple


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class WikiPage:
    """Represents a wiki page with metadata and content."""
    title: str
    file_path: str
    page_type: str
    tags: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    created: str = ""
    updated: str = ""
    confidence: str = ""
    provenance: str = ""
    status: str = ""
    engagement: str = ""
    client: str = ""
    severity: str = ""
    domain: str = ""
    chain: str = ""
    tools: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    content: str = ""
    raw_content: str = ""


@dataclass
class SearchResult:
    """Represents a search result with relevance score."""
    page: WikiPage
    score: float
    matched_fields: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


# ============================================================================
# Frontmatter Parser
# ============================================================================

def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """Parse YAML frontmatter from markdown content.
    
    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_text = parts[1].strip()
    body = parts[2].strip()
    
    # Simple YAML parser for basic types
    fm = {}
    current_key = None
    current_list = None
    
    for line in frontmatter_text.split('\n'):
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue
        
        # List item
        if line.strip().startswith('- '):
            if current_key and current_list is not None:
                value = line.strip()[2:].strip().strip('"').strip("'")
                current_list.append(value)
            continue
        
        # Key-value pair
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            
            # Check for inline list format: [item1, item2, ...]
            if value.startswith('[') and value.endswith(']'):
                # Parse inline list
                list_content = value[1:-1].strip()
                if list_content:
                    items = [item.strip().strip('"').strip("'") for item in list_content.split(',')]
                    fm[key] = items
                else:
                    fm[key] = []
                current_key = None
                current_list = None
            # Start of a list
            elif value == '':
                current_key = key
                current_list = []
                fm[key] = current_list
            else:
                # Remove quotes
                value = value.strip('"').strip("'")
                
                # Parse dates
                if key in ('created', 'updated'):
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        pass
                
                fm[key] = value
                current_key = None
                current_list = None
    
    return fm, body


# ============================================================================
# Wiki Page Loader
# ============================================================================

def load_wiki_pages(wiki_path: str) -> List[WikiPage]:
    """Load all wiki pages from the wiki directory.
    
    Args:
        wiki_path: Path to the wiki directory
        
    Returns:
        List of WikiPage objects
    """
    pages = []
    wiki_dir = Path(wiki_path)
    
    if not wiki_dir.exists():
        print(f"Error: Wiki path does not exist: {wiki_path}", file=sys.stderr)
        return pages
    
    # Search for markdown files in all subdirectories
    for md_file in wiki_dir.rglob('*.md'):
        # Skip Index.md and SCHEMA.md
        if md_file.name in ('Index.md', 'SCHEMA.md'):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(content)
            
            page = WikiPage(
                title=fm.get('title', md_file.stem),
                file_path=str(md_file.relative_to(wiki_dir)),
                page_type=fm.get('type', 'unknown'),
                tags=fm.get('tags', []),
                sources=fm.get('sources', []),
                created=fm.get('created', ''),
                updated=fm.get('updated', ''),
                confidence=fm.get('confidence', ''),
                provenance=fm.get('provenance', ''),
                status=fm.get('status', ''),
                engagement=fm.get('engagement', ''),
                client=fm.get('client', ''),
                severity=fm.get('severity', ''),
                domain=fm.get('domain', ''),
                chain=fm.get('chain', ''),
                tools=fm.get('tools', []),
                related=fm.get('related', []),
                content=body,
                raw_content=content,
            )
            pages.append(page)
        except Exception as e:
            print(f"Warning: Failed to parse {md_file}: {e}", file=sys.stderr)
    
    return pages


# ============================================================================
# Fuzzy Matching
# ============================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_match(query: str, text: str, threshold: float = 0.6) -> Tuple[bool, float]:
    """Check if query fuzzy matches text.
    
    Returns:
        Tuple of (matched, score)
    """
    query_lower = query.lower()
    text_lower = text.lower()
    
    # Exact match
    if query_lower in text_lower:
        return True, 1.0
    
    # Word-level matching
    query_words = query_lower.split()
    text_words = text_lower.split()
    
    if not query_words or not text_words:
        return False, 0.0
    
    # Check if all query words have a fuzzy match in text
    total_score = 0.0
    for qw in query_words:
        best_score = 0.0
        for tw in text_words:
            # Exact word match
            if qw == tw:
                best_score = 1.0
                break
            # Substring match
            elif qw in tw or tw in qw:
                best_score = max(best_score, 0.8)
            # Levenshtein similarity
            else:
                max_len = max(len(qw), len(tw))
                if max_len > 0:
                    dist = levenshtein_distance(qw, tw)
                    similarity = 1.0 - (dist / max_len)
                    best_score = max(best_score, similarity)
        total_score += best_score
    
    avg_score = total_score / len(query_words)
    return avg_score >= threshold, avg_score


# ============================================================================
# Search Engine
# ============================================================================

class WikiSearchEngine:
    """Search engine for the security wiki."""
    
    # Field weights for relevance scoring
    FIELD_WEIGHTS = {
        'title': 10.0,
        'tags': 8.0,
        'content': 5.0,
        'type': 3.0,
        'client': 4.0,
        'engagement': 3.0,
        'severity': 2.0,
        'domain': 2.0,
        'tools': 3.0,
        'sources': 2.0,
    }
    
    def __init__(self, pages: List[WikiPage], fuzzy_threshold: float = 0.6):
        self.pages = pages
        self.fuzzy_threshold = fuzzy_threshold
    
    def search(
        self,
        query: str = "",
        tags: Optional[List[str]] = None,
        page_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        domain: Optional[str] = None,
        fuzzy: bool = True,
        limit: int = 20,
    ) -> List[SearchResult]:
        """Search the wiki pages.
        
        Args:
            query: Search query string
            tags: Filter by tags
            page_type: Filter by page type
            date_from: Filter by start date
            date_to: Filter by end date
            status: Filter by status
            domain: Filter by domain
            fuzzy: Enable fuzzy matching
            limit: Maximum results
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        results = []
        
        for page in self.pages:
            # Apply filters
            if tags and not any(t in page.tags for t in tags):
                continue
            if page_type and page.page_type != page_type:
                continue
            if status and page.status != status:
                continue
            if domain and page.domain != domain:
                continue
            if date_from and page.created and page.created < date_from:
                continue
            if date_to and page.created and page.created > date_to:
                continue
            
            # Calculate relevance score
            score, matched_fields, highlights = self._calculate_score(
                page, query, fuzzy
            )
            
            if score > 0:
                results.append(SearchResult(
                    page=page,
                    score=score,
                    matched_fields=matched_fields,
                    highlights=highlights,
                ))
        
        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results[:limit]
    
    def _calculate_score(
        self, page: WikiPage, query: str, fuzzy: bool
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate relevance score for a page against a query."""
        if not query:
            return 1.0, [], []
        
        score = 0.0
        matched_fields = []
        highlights = []
        
        query_lower = query.lower()
        
        # Title match (highest weight)
        if fuzzy:
            matched, title_score = fuzzy_match(query, page.title, self.fuzzy_threshold)
            if matched:
                score += title_score * self.FIELD_WEIGHTS['title']
                matched_fields.append('title')
                highlights.append(f"Title: {page.title}")
        else:
            if query_lower in page.title.lower():
                score += self.FIELD_WEIGHTS['title']
                matched_fields.append('title')
                highlights.append(f"Title: {page.title}")
        
        # Tag match
        for tag in page.tags:
            if fuzzy:
                matched, tag_score = fuzzy_match(query, tag, self.fuzzy_threshold)
                if matched:
                    score += tag_score * self.FIELD_WEIGHTS['tags']
                    if 'tags' not in matched_fields:
                        matched_fields.append('tags')
                    highlights.append(f"Tag: {tag}")
            else:
                if query_lower in tag.lower():
                    score += self.FIELD_WEIGHTS['tags']
                    if 'tags' not in matched_fields:
                        matched_fields.append('tags')
                    highlights.append(f"Tag: {tag}")
        
        # Content match
        if fuzzy:
            # Check content in chunks for fuzzy matching
            content_lower = page.content.lower()
            if query_lower in content_lower:
                score += self.FIELD_WEIGHTS['content']
                matched_fields.append('content')
                # Extract context around match
                idx = content_lower.find(query_lower)
                start = max(0, idx - 50)
                end = min(len(page.content), idx + len(query) + 50)
                snippet = page.content[start:end].replace('\n', ' ')
                highlights.append(f"Content: ...{snippet}...")
            else:
                # Try fuzzy matching on content words
                content_words = set(re.findall(r'\b\w+\b', content_lower))
                query_words = query_lower.split()
                fuzzy_matches = 0
                for qw in query_words:
                    for cw in content_words:
                        if fuzzy_match(qw, cw, self.fuzzy_threshold)[0]:
                            fuzzy_matches += 1
                            break
                if fuzzy_matches > 0:
                    content_score = fuzzy_matches / len(query_words)
                    score += content_score * self.FIELD_WEIGHTS['content']
                    matched_fields.append('content')
        else:
            if query_lower in page.content.lower():
                score += self.FIELD_WEIGHTS['content']
                matched_fields.append('content')
                idx = page.content.lower().find(query_lower)
                start = max(0, idx - 50)
                end = min(len(page.content), idx + len(query) + 50)
                snippet = page.content[start:end].replace('\n', ' ')
                highlights.append(f"Content: ...{snippet}...")
        
        # Type match
        if query_lower in page.page_type.lower():
            score += self.FIELD_WEIGHTS['type']
            matched_fields.append('type')
        
        # Client match
        if page.client and query_lower in page.client.lower():
            score += self.FIELD_WEIGHTS['client']
            matched_fields.append('client')
            highlights.append(f"Client: {page.client}")
        
        # Engagement match
        if page.engagement and query_lower in page.engagement.lower():
            score += self.FIELD_WEIGHTS['engagement']
            matched_fields.append('engagement')
            highlights.append(f"Engagement: {page.engagement}")
        
        # Severity match
        if page.severity and query_lower in page.severity.lower():
            score += self.FIELD_WEIGHTS['severity']
            matched_fields.append('severity')
        
        # Domain match
        if page.domain and query_lower in page.domain.lower():
            score += self.FIELD_WEIGHTS['domain']
            matched_fields.append('domain')
        
        # Tool match
        for tool in page.tools:
            if query_lower in tool.lower():
                score += self.FIELD_WEIGHTS['tools']
                if 'tools' not in matched_fields:
                    matched_fields.append('tools')
                highlights.append(f"Tool: {tool}")
        
        # Source match
        for source in page.sources:
            if query_lower in source.lower():
                score += self.FIELD_WEIGHTS['sources']
                if 'sources' not in matched_fields:
                    matched_fields.append('sources')
                highlights.append(f"Source: {source}")
        
        return score, matched_fields, highlights


# ============================================================================
# Output Formatters
# ============================================================================

def format_text(results: List[SearchResult], verbose: bool = False) -> str:
    """Format search results as text."""
    if not results:
        return "No results found."
    
    lines = []
    lines.append(f"Found {len(results)} result(s):\n")
    
    for i, result in enumerate(results, 1):
        page = result.page
        lines.append(f"[{i}] {page.title}")
        lines.append(f"    Type: {page.page_type} | Status: {page.status} | Score: {result.score:.2f}")
        
        if page.tags:
            lines.append(f"    Tags: {', '.join(page.tags)}")
        if page.client:
            lines.append(f"    Client: {page.client}")
        if page.severity:
            lines.append(f"    Severity: {page.severity}")
        if page.domain:
            lines.append(f"    Domain: {page.domain}")
        if page.created:
            lines.append(f"    Created: {page.created}")
        
        if verbose:
            lines.append(f"    File: {page.file_path}")
            lines.append(f"    Matched: {', '.join(result.matched_fields)}")
            if result.highlights:
                lines.append("    Highlights:")
                for h in result.highlights:
                    lines.append(f"      - {h}")
        
        lines.append("")
    
    return '\n'.join(lines)


def format_json(results: List[SearchResult]) -> str:
    """Format search results as JSON."""
    output = []
    for result in results:
        page = result.page
        output.append({
            'title': page.title,
            'file_path': page.file_path,
            'type': page.page_type,
            'tags': page.tags,
            'status': page.status,
            'score': round(result.score, 2),
            'matched_fields': result.matched_fields,
            'highlights': result.highlights,
            'client': page.client,
            'severity': page.severity,
            'domain': page.domain,
            'created': page.created,
            'updated': page.updated,
            'confidence': page.confidence,
            'provenance': page.provenance,
            'engagement': page.engagement,
        })
    return json.dumps(output, indent=2)


# ============================================================================
# Raw Directory Search
# ============================================================================

def search_raw_directory(raw_dir: Path, query: str, fuzzy: bool = True, threshold: float = 0.6) -> List[dict]:
    """Search the raw/ directory for files matching the query.
    
    Args:
        raw_dir: Path to the raw directory
        query: Search query string
        fuzzy: Enable fuzzy matching
        threshold: Fuzzy match threshold
        
    Returns:
        List of result dictionaries with file_path, score, and highlights
    """
    if not query:
        return []
    
    results = []
    query_lower = query.lower()
    
    for md_file in raw_dir.rglob('*'):
        if not md_file.is_file():
            continue
        
        # Skip binary files
        if md_file.suffix in ('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.gz', '.gpg'):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        
        score = 0.0
        highlights = []
        
        # Check filename
        if query_lower in md_file.name.lower():
            score += 5.0
            highlights.append(f"Filename: {md_file.name}")
        
        # Check content
        content_lower = content.lower()
        if query_lower in content_lower:
            score += 10.0
            # Extract context around match
            idx = content_lower.find(query_lower)
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query) + 50)
            snippet = content[start:end].replace('\n', ' ')
            highlights.append(f"Content: ...{snippet}...")
        
        # Fuzzy matching on content
        if fuzzy and score == 0:
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            query_words = query_lower.split()
            fuzzy_matches = 0
            for qw in query_words:
                for cw in content_words:
                    if fuzzy_match(qw, cw, threshold)[0]:
                        fuzzy_matches += 1
                        break
            if fuzzy_matches > 0:
                score = (fuzzy_matches / len(query_words)) * 5.0
        
        if score > 0:
            results.append({
                'file_path': str(md_file.relative_to(raw_dir.parent)),
                'score': round(score, 2),
                'highlights': highlights,
            })
    
    # Sort by score descending
    results.sort(key=lambda r: r['score'], reverse=True)
    return results


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Search the security wiki by title, tag, and content.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('wiki_path', help='Path to the wiki directory')
    parser.add_argument('-q', '--query', default='', help='Search query string')
    parser.add_argument('-t', '--tag', help='Filter by tag (comma-separated)')
    parser.add_argument('-T', '--type', help='Filter by page type')
    parser.add_argument('--date-from', help='Filter by start date (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='Filter by end date (YYYY-MM-DD)')
    parser.add_argument('-s', '--status', help='Filter by status')
    parser.add_argument('-d', '--domain', help='Filter by domain (web2, web3, cross-domain)')
    parser.add_argument('-n', '--limit', type=int, default=20, help='Maximum results')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('-F', '--fuzzy', action='store_true', default=True, help='Enable fuzzy matching')
    parser.add_argument('--fuzzy-threshold', type=float, default=0.6, help='Fuzzy match threshold')
    parser.add_argument('--no-fuzzy', action='store_true', help='Disable fuzzy matching')
    parser.add_argument('--search-raw', action='store_true', help='Also search the raw/ directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Load pages
    pages = load_wiki_pages(args.wiki_path)
    
    if not pages:
        print("No wiki pages found.", file=sys.stderr)
        sys.exit(1)
    
    # Parse tags
    tags = None
    if args.tag:
        tags = [t.strip() for t in args.tag.split(',')]
    
    # Determine fuzzy setting
    fuzzy = not args.no_fuzzy
    
    # Search
    engine = WikiSearchEngine(pages, fuzzy_threshold=args.fuzzy_threshold)
    results = engine.search(
        query=args.query,
        tags=tags,
        page_type=args.type,
        date_from=args.date_from,
        date_to=args.date_to,
        status=args.status,
        domain=args.domain,
        fuzzy=fuzzy,
        limit=args.limit,
    )
    
    # Search raw directory if requested
    if args.search_raw:
        raw_dir = Path(args.wiki_path).parent / 'raw'
        if raw_dir.exists():
            raw_results = search_raw_directory(raw_dir, args.query, fuzzy, args.fuzzy_threshold)
            if raw_results:
                if args.format == 'json':
                    # Merge raw results into JSON output
                    json_output = json.loads(format_json(results))
                    json_output.extend(raw_results)
                    print(json.dumps(json_output, indent=2))
                else:
                    print(format_text(results, verbose=args.verbose))
                    print(f"\n--- Raw Directory Results ({len(raw_results)} files) ---\n")
                    for r in raw_results:
                        print(f"  {r['file_path']} (score: {r['score']:.2f})")
                        if args.verbose and r.get('highlights'):
                            for h in r['highlights']:
                                print(f"    - {h}")
                    return
            else:
                if args.format != 'json':
                    print("No raw directory results found.")
        else:
            if args.format != 'json':
                print(f"Raw directory not found: {raw_dir}")
    
    # Output
    if args.format == 'json':
        print(format_json(results))
    else:
        print(format_text(results, verbose=args.verbose))


if __name__ == '__main__':
    main()
