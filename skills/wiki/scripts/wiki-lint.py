#!/usr/bin/env python3
"""
wiki-lint.py — Automated lint checks for the security wiki.

Validates wikilinks, detects orphans, flags stale claims, detects duplicates,
verifies frontmatter, checks Index coverage, and outputs a lint report with
severity levels.

Usage:
    python wiki-lint.py <wiki_path> [options]

Options:
    --check, -c         Run specific check (comma-separated)
    --format, -f        Output format: text, json, markdown (default: text)
    --severity, -s      Minimum severity to report: critical, warning, info
    --fix               Attempt to auto-fix issues where possible
    --output, -o        Output file (default: stdout)
    --verbose, -v       Verbose output
    --help, -h          Show this help message

Examples:
    python wiki-lint.py /path/to/wiki
    python wiki-lint.py /path/to/wiki --check link-validation,orphan-detection
    python wiki-lint.py /path/to/wiki -f json -o lint-report.json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Set, Tuple


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class LintIssue:
    """Represents a lint issue."""
    check: str
    severity: str  # critical, warning, info
    page: str
    message: str
    line: Optional[int] = None
    suggestion: str = ""
    details: str = ""


@dataclass
class LintReport:
    """Represents a lint report."""
    wiki_path: str
    timestamp: str
    total_pages: int
    issues: List[LintIssue] = field(default_factory=list)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'critical')
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'warning')
    
    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'info')
    
    @property
    def exit_code(self) -> int:
        if self.critical_count > 0:
            return 2
        elif self.warning_count > 0:
            return 1
        return 0


# ============================================================================
# Frontmatter Parser
# ============================================================================

def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_text = parts[1].strip()
    body = parts[2].strip()
    
    fm = {}
    current_key = None
    current_list = None
    
    for line in frontmatter_text.split('\n'):
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue
        
        if line.strip().startswith('- '):
            if current_key and current_list is not None:
                value = line.strip()[2:].strip().strip('"').strip("'")
                current_list.append(value)
            continue
        
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
            elif value == '':
                current_key = key
                current_list = []
                fm[key] = current_list
            else:
                value = value.strip('"').strip("'")
                fm[key] = value
                current_key = None
                current_list = None
    
    return fm, body


# ============================================================================
# Wiki Page Loader
# ============================================================================

@dataclass
class WikiPage:
    """Represents a wiki page."""
    title: str
    file_path: str
    page_type: str = "unknown"
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


def load_wiki_pages(wiki_path: str) -> List[WikiPage]:
    """Load all wiki pages from the wiki directory."""
    pages = []
    wiki_dir = Path(wiki_path)
    
    if not wiki_dir.exists():
        print(f"Error: Wiki path does not exist: {wiki_path}", file=sys.stderr)
        return pages
    
    for md_file in wiki_dir.rglob('*.md'):
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
# Lint Checks
# ============================================================================

class LintChecker:
    """Runs lint checks on wiki pages."""
    
    # Valid values for frontmatter fields
    VALID_TYPES = {'entity', 'concept', 'synthesis', 'trail', 'timeline', 'overview', 'contradiction'}
    VALID_CONFIDENCE = {'high', 'medium', 'low'}
    VALID_PROVENANCE = {'tool-proven', 'model-asserted', 'unreviewed'}
    VALID_STATUS = {'active', 'invalidated', 'draft', 'archived'}
    VALID_SEVERITY = {'critical', 'high', 'medium', 'low', 'informational'}
    VALID_DOMAIN = {'web2', 'web3', 'cross-domain'}
    VALID_CHAIN = {'ethereum', 'solana', 'bitcoin', 'cosmos', 'multi-chain', 'n/a'}
    
    # Valid tags loaded from taxonomy file
    VALID_TAGS = set()
    
    @classmethod
    def load_valid_tags(cls, wiki_path: str = None):
        """Load valid tags from the taxonomy file."""
        # Try to find taxonomy file relative to script location
        script_dir = Path(__file__).parent
        taxonomy_paths = [
            script_dir.parent / 'references' / 'tagging-taxonomy.md',
            Path(wiki_path).parent / 'references' / 'tagging-taxonomy.md' if wiki_path else None,
        ]
        
        for taxonomy_path in taxonomy_paths:
            if taxonomy_path and taxonomy_path.exists():
                try:
                    content = taxonomy_path.read_text(encoding='utf-8')
                    # Extract tags from markdown tables (backtick-quoted items in first column)
                    tags = set()
                    for match in re.finditer(r'^\|\s*`([^`]+)`\s*\|', content, re.MULTILINE):
                        tag = match.group(1).strip()
                        if tag and not tag.startswith('-') and tag != 'Tag':
                            tags.add(tag)
                    # Also extract from inline code in tag lists
                    for match in re.finditer(r'`([a-z][a-z0-9-]*)`', content):
                        tag = match.group(1).strip()
                        if tag and len(tag) > 1 and not tag.startswith('tool-'):
                            tags.add(tag)
                    cls.VALID_TAGS = tags
                    return
                except Exception:
                    pass
        
        # Fallback to basic tags if taxonomy not found
        cls.VALID_TAGS = {
            'web2', 'web3', 'cross-domain', 'recon', 'audit', 'exploit',
            'forensics', 'report', 'verify', 'owasp-top10', 'swc-registry',
            'cve', 'cve-critical', 'cve-high', 'custom', 'zero-day', 'n-day',
            'injection', 'broken-auth', 'sensitive-data-exposure', 'xxe',
            'broken-access-control', 'security-misconfig', 'xss',
            'insecure-deserialization', 'vulnerable-components', 'insufficient-logging',
            'reentrancy', 'access-control', 'arithmetic', 'unprotected-ether',
            'delegatecall', 'tx-origin', 'timestamp-dependence', 'short-address',
            'default-visibility', 'critical', 'high', 'medium', 'low',
            'informational', 'active', 'invalidated', 'draft', 'archived',
            'ethereum', 'solana', 'bitcoin', 'cosmos', 'multi-chain', 'n/a',
            'defi', 'nft', 'dao', 'bridge', 'lending', 'amm', 'staking',
            'governance', 'oracle', 'wallet', 'tool-nmap', 'tool-nuclei',
            'tool-burp', 'tool-metasploit', 'tool-slither', 'tool-mythril',
            'tool-foundry', 'tool-hardhat', 'tool-echidna', 'tool-manticore',
            'active-directory', 'analysis', 'attack-path', 'chain',
            'marketplace', 'protocol', 'target', 'timeline', 'engagement',
            'overview', 'attack-surface',
        }
    
    def __init__(self, pages: List[WikiPage], wiki_path: str):
        self.pages = pages
        self.wiki_path = wiki_path
        self.issues: List[LintIssue] = []
        self.page_titles = {p.title for p in pages}
        self.incoming_links = defaultdict(list)
        self._build_link_graph()
    
    def _build_link_graph(self):
        """Build incoming link graph."""
        for page in self.pages:
            links = self._extract_wikilinks(page.content)
            for link_target in links:
                self.incoming_links[link_target].append(page.title)
    
    def _extract_wikilinks(self, content: str) -> List[str]:
        """Extract wikilink targets from content."""
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        return [m.group(1).strip() for m in re.finditer(pattern, content)]
    
    def _add_issue(self, check: str, severity: str, page: str, message: str,
                   line: Optional[int] = None, suggestion: str = "", details: str = ""):
        """Add a lint issue."""
        self.issues.append(LintIssue(
            check=check,
            severity=severity,
            page=page,
            message=message,
            line=line,
            suggestion=suggestion,
            details=details,
        ))
    
    # -------------------------------------------------------------------------
    # Check 1: Link Validation
    # -------------------------------------------------------------------------
    
    def check_link_validation(self):
        """Validate all wikilinks resolve to existing pages."""
        for page in self.pages:
            links = re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', page.content)
            for match in links:
                target = match.group(1).strip()
                
                if target not in self.page_titles:
                    # Check if it's an invalidated page
                    invalidated = [p for p in self.pages if p.title == target and p.status == 'invalidated']
                    
                    if invalidated:
                        self._add_issue(
                            check='link-validation',
                            severity='warning',
                            page=page.file_path,
                            message=f'Link to invalidated page: [[{target}]]',
                            suggestion=f'Update link to reference the superseding page',
                        )
                    else:
                        self._add_issue(
                            check='link-validation',
                            severity='critical',
                            page=page.file_path,
                            message=f'Broken link: [[{target}]]',
                            suggestion=f'Create page "{target}" or update link',
                        )
    
    # -------------------------------------------------------------------------
    # Check 2: Orphan Detection
    # -------------------------------------------------------------------------
    
    def check_orphan_detection(self):
        """Detect pages with no incoming links."""
        for page in self.pages:
            if page.title == 'Index':
                continue
            
            incoming = self.incoming_links.get(page.title, [])
            if len(incoming) == 0:
                severity = 'info' if page.status in ('draft', 'invalidated') else 'warning'
                self._add_issue(
                    check='orphan-detection',
                    severity=severity,
                    page=page.file_path,
                    message=f'Orphan page: no incoming links',
                    suggestion='Add link from Index.md or related page',
                )
    
    # -------------------------------------------------------------------------
    # Check 3: Stale Claim Detection
    # -------------------------------------------------------------------------
    
    def check_stale_claims(self):
        """Flag claims contradicted by newer evidence."""
        for page in self.pages:
            # Check for invalidated pages still referenced by active pages
            if page.status == 'invalidated':
                for other_page in self.pages:
                    if other_page.status == 'active':
                        links = self._extract_wikilinks(other_page.content)
                        if page.title in links:
                            self._add_issue(
                                check='stale-claims',
                                severity='warning',
                                page=other_page.file_path,
                                message=f'References invalidated page: [[{page.title}]]',
                                suggestion='Update reference to current page',
                            )
            
            # Check for outdated tool versions
            for tool in page.tools:
                # Parse tool name and version
                tool_match = re.match(r'^([a-zA-Z0-9_-]+)\s+v?(\d+\.\d+(?:\.\d+)?)', tool)
                if tool_match:
                    tool_name = tool_match.group(1).lower()
                    tool_version = tool_match.group(2)
                    
                    # Known current versions (simplified - in production, query a database)
                    current_versions = {
                        'nmap': '7.95',
                        'nuclei': '3.3.0',
                        'burp': '2024.1',
                        'metasploit': '6.4.0',
                        'slither': '0.10.0',
                        'mythril': '0.23.0',
                        'foundry': '0.2.0',
                        'hardhat': '2.22.0',
                        'echidna': '2.2.0',
                        'manticore': '0.3.0',
                    }
                    
                    if tool_name in current_versions:
                        current = current_versions[tool_name]
                        # Simple version comparison (major.minor)
                        try:
                            tool_parts = [int(x) for x in tool_version.split('.')]
                            current_parts = [int(x) for x in current.split('.')]
                            
                            # Check if tool is more than 2 major versions behind
                            if len(tool_parts) >= 1 and len(current_parts) >= 1:
                                major_diff = current_parts[0] - tool_parts[0]
                                if major_diff >= 2:
                                    self._add_issue(
                                        check='stale-claims',
                                        severity='info',
                                        page=page.file_path,
                                        message=f'Outdated tool: {tool_name} {tool_version} (current: {current})',
                                        suggestion=f'Update tool version in frontmatter to {current}',
                                    )
                        except (ValueError, IndexError):
                            pass
            
            # Check for pages not updated in >90 days
            if page.updated and page.status == 'active':
                try:
                    updated_date = datetime.strptime(page.updated, '%Y-%m-%d')
                    days_since = (datetime.now() - updated_date).days
                    if days_since > 90:
                        self._add_issue(
                            check='stale-claims',
                            severity='info',
                            page=page.file_path,
                            message=f'Page not updated in {days_since} days',
                            suggestion='Review and update page content',
                        )
                except ValueError:
                    pass
    
    # -------------------------------------------------------------------------
    # Check 4: Duplicate Detection
    # -------------------------------------------------------------------------
    
    def check_duplicates(self):
        """Detect duplicate content (similar titles, overlapping tags)."""
        from difflib import SequenceMatcher
        
        for i, page_a in enumerate(self.pages):
            for page_b in self.pages[i+1:]:
                # Title similarity
                title_ratio = SequenceMatcher(None, page_a.title.lower(), page_b.title.lower()).ratio()
                
                if title_ratio > 0.9:
                    self._add_issue(
                        check='duplicates',
                        severity='critical',
                        page=page_b.file_path,
                        message=f'Duplicate title: "{page_a.title}" and "{page_b.title}" (similarity: {title_ratio:.0%})',
                        suggestion='Merge pages or differentiate titles',
                    )
                elif title_ratio > 0.8:
                    # Check tag overlap
                    tags_a = set(page_a.tags)
                    tags_b = set(page_b.tags)
                    if tags_a and tags_b:
                        overlap = len(tags_a & tags_b) / len(tags_a | tags_b)
                        if overlap > 0.7:
                            self._add_issue(
                                check='duplicates',
                                severity='warning',
                                page=page_b.file_path,
                                message=f'Potential duplicate: "{page_a.title}" and "{page_b.title}" (title: {title_ratio:.0%}, tags: {overlap:.0%})',
                                suggestion='Review and merge if duplicate',
                            )
                
                # Check for identical titles (case-insensitive)
                if page_a.title.lower() == page_b.title.lower() and page_a.title != page_b.title:
                    self._add_issue(
                        check='duplicates',
                        severity='critical',
                        page=page_b.file_path,
                        message=f'Identical titles (case-insensitive): "{page_a.title}" and "{page_b.title}"',
                        suggestion='Rename one page',
                    )
    
    # -------------------------------------------------------------------------
    # Check 5: Frontmatter Completeness
    # -------------------------------------------------------------------------
    
    def check_frontmatter(self):
        """Verify all required frontmatter fields are present and valid."""
        required_fields = {
            'title': str,
            'type': str,
            'tags': list,
            'sources': list,
            'created': str,
            'updated': str,
            'confidence': str,
            'provenance': str,
            'status': str,
        }
        
        for page in self.pages:
            fm, _ = parse_frontmatter(page.raw_content)
            
            # Check required fields
            for field_name, field_type in required_fields.items():
                if field_name not in fm:
                    self._add_issue(
                        check='frontmatter',
                        severity='critical',
                        page=page.file_path,
                        message=f'Missing required field: {field_name}',
                        suggestion=f'Add {field_name} to frontmatter',
                    )
            
            # Validate enum values
            if page.page_type not in self.VALID_TYPES:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid type: {page.page_type}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_TYPES))}',
                )
            
            if page.confidence and page.confidence not in self.VALID_CONFIDENCE:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid confidence: {page.confidence}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_CONFIDENCE))}',
                )
            
            if page.provenance and page.provenance not in self.VALID_PROVENANCE:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid provenance: {page.provenance}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_PROVENANCE))}',
                )
            
            if page.status and page.status not in self.VALID_STATUS:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid status: {page.status}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_STATUS))}',
                )
            
            if page.severity and page.severity not in self.VALID_SEVERITY:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid severity: {page.severity}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_SEVERITY))}',
                )
            
            if page.domain and page.domain not in self.VALID_DOMAIN:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid domain: {page.domain}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_DOMAIN))}',
                )
            
            if page.chain and page.chain not in self.VALID_CHAIN:
                self._add_issue(
                    check='frontmatter',
                    severity='critical',
                    page=page.file_path,
                    message=f'Invalid chain: {page.chain}',
                    suggestion=f'Use one of: {", ".join(sorted(self.VALID_CHAIN))}',
                )
            
            # Validate dates
            for date_field in ('created', 'updated'):
                date_val = getattr(page, date_field)
                if date_val:
                    try:
                        datetime.strptime(date_val, '%Y-%m-%d')
                    except ValueError:
                        self._add_issue(
                            check='frontmatter',
                            severity='critical',
                            page=page.file_path,
                            message=f'Invalid date format for {date_field}: {date_val}',
                            suggestion='Use ISO 8601 format (YYYY-MM-DD)',
                        )
            
            # Check updated >= created
            if page.created and page.updated:
                try:
                    created_date = datetime.strptime(page.created, '%Y-%m-%d')
                    updated_date = datetime.strptime(page.updated, '%Y-%m-%d')
                    if updated_date < created_date:
                        self._add_issue(
                            check='frontmatter',
                            severity='critical',
                            page=page.file_path,
                            message=f'updated date is before created date',
                            suggestion='Fix date values',
                        )
                except ValueError:
                    pass
            
            # Check dates not in future
            today = datetime.now().strftime('%Y-%m-%d')
            if page.created and page.created > today:
                self._add_issue(
                    check='frontmatter',
                    severity='warning',
                    page=page.file_path,
                    message=f'Created date is in the future: {page.created}',
                    suggestion='Fix date value',
                )
    
    # -------------------------------------------------------------------------
    # Check 6: Index Coverage
    # -------------------------------------------------------------------------
    
    def check_index_coverage(self):
        """Check all pages are listed in Index.md."""
        index_path = Path(self.wiki_path) / 'Index.md'
        
        if not index_path.exists():
            self._add_issue(
                check='index-coverage',
                severity='critical',
                page='Index.md',
                message='Index.md not found',
                suggestion='Create Index.md as the master navigation hub',
            )
            return
        
        index_content = index_path.read_text(encoding='utf-8')
        index_links = set(self._extract_wikilinks(index_content))
        
        for page in self.pages:
            if page.title == 'Index':
                continue
            
            if page.title not in index_links:
                self._add_issue(
                    check='index-coverage',
                    severity='critical',
                    page=page.file_path,
                    message=f'Page not listed in Index.md',
                    suggestion=f'Add [[{page.title}]] to Index.md',
                )
        
        # Check for broken links in Index.md
        for link in index_links:
            if link not in self.page_titles:
                self._add_issue(
                    check='index-coverage',
                    severity='critical',
                    page='Index.md',
                    message=f'Index.md links to non-existent page: [[{link}]]',
                    suggestion='Remove or fix the link',
                )
    
    # -------------------------------------------------------------------------
    # Check 7: Provenance Completeness
    # -------------------------------------------------------------------------
    
    def check_provenance(self):
        """Check all claims have provenance labels."""
        for page in self.pages:
            # Check for unreviewed pages older than 30 days
            if page.provenance == 'unreviewed' and page.created:
                try:
                    created_date = datetime.strptime(page.created, '%Y-%m-%d')
                    days_since = (datetime.now() - created_date).days
                    if days_since > 30:
                        self._add_issue(
                            check='provenance',
                            severity='warning',
                            page=page.file_path,
                            message=f'Unreviewed page older than 30 days ({days_since} days)',
                            suggestion='Review and update provenance level',
                        )
                except ValueError:
                    pass
            
            # Check for upgradeable model-asserted claims
            if page.provenance == 'model-asserted':
                # Check if sources contain tool outputs
                has_tool_evidence = any(
                    'raw/' in source or 'tool' in source.lower()
                    for source in page.sources
                )
                if has_tool_evidence:
                    self._add_issue(
                        check='provenance',
                        severity='info',
                        page=page.file_path,
                        message='Model-asserted page has tool evidence available',
                        suggestion='Consider upgrading to tool-proven',
                    )
    
    # -------------------------------------------------------------------------
    # Check 8: Tag Validity
    # -------------------------------------------------------------------------
    
    def check_tag_validity(self):
        """Check all tags are in the approved taxonomy."""
        for page in self.pages:
            for tag in page.tags:
                if tag not in self.VALID_TAGS:
                    # Check for similar tags
                    similar = [t for t in self.VALID_TAGS if tag.lower() in t.lower() or t.lower() in tag.lower()]
                    suggestion = f'Did you mean: {", ".join(similar[:3])}?' if similar else 'Use a tag from the taxonomy'
                    
                    self._add_issue(
                        check='tag-validity',
                        severity='critical',
                        page=page.file_path,
                        message=f'Invalid tag: {tag}',
                        suggestion=suggestion,
                    )
            
            # Check for missing domain tag
            if not page.domain:
                self._add_issue(
                    check='tag-validity',
                    severity='warning',
                    page=page.file_path,
                    message='Missing domain tag',
                    suggestion='Add domain: web2, web3, or cross-domain',
                )
            
            # Check for missing severity tag on findings
            if page.page_type in ('concept', 'synthesis') and not page.severity:
                self._add_issue(
                    check='tag-validity',
                    severity='warning',
                    page=page.file_path,
                    message='Missing severity tag',
                    suggestion='Add severity: critical, high, medium, low, or informational',
                )
    
    # -------------------------------------------------------------------------
    # Check 9: Page Type Validity
    # -------------------------------------------------------------------------
    
    def check_page_type_validity(self):
        """Check page type matches content structure."""
        type_indicators = {
            'entity': ['Summary', 'Attributes', 'Findings'],
            'concept': ['Definition', 'Impact', 'Mitigation'],
            'synthesis': ['Question', 'Answer', 'Evidence'],
            'trail': ['Entry Point', 'Attack Chain', 'Impact'],
            'timeline': ['Metadata', 'Phase', 'Findings'],
            'overview': ['Surface', 'Findings', 'Paths'],
            'contradiction': ['Conflict', 'Source A', 'Source B', 'Resolution'],
        }
        
        for page in self.pages:
            if page.page_type not in type_indicators:
                continue
            
            expected_sections = type_indicators[page.page_type]
            headings = re.findall(r'^#{1,3}\s+(.+)$', page.content, re.MULTILINE)
            headings_lower = [h.lower() for h in headings]
            
            missing = []
            for section in expected_sections:
                if not any(section.lower() in h for h in headings_lower):
                    missing.append(section)
            
            if missing:
                self._add_issue(
                    check='page-type-validity',
                    severity='warning',
                    page=page.file_path,
                    message=f'Missing expected sections for {page.page_type}: {", ".join(missing)}',
                    suggestion='Add missing sections or verify page type',
                )
    
    # -------------------------------------------------------------------------
    # Check 10: Cross-Domain Contamination
    # -------------------------------------------------------------------------
    
    def check_cross_domain_contamination(self):
        """Check web2/web3 findings are properly separated."""
        web2_terms = ['sql injection', 'xss', 'csrf', 'active directory', 'ldap', 'kerberos', 'phishing', 'malware']
        web3_terms = ['smart contract', 'solidity', 'evm', 'flash loan', 'oracle', 'reentrancy', 'bytecode']
        
        for page in self.pages:
            content_lower = page.content.lower()
            
            # Remove wikilink targets from content to avoid false positives from link text
            # e.g., [[DeFi Protocol Security]] should not trigger web3 term detection
            content_without_links = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', '', content_lower)
            
            if page.domain == 'web2':
                web3_matches = [term for term in web3_terms if term in content_without_links]
                if web3_matches and 'cross-domain' not in page.tags:
                    self._add_issue(
                        check='cross-domain-contamination',
                        severity='critical',
                        page=page.file_path,
                        message=f'Web2 page contains web3 terms: {", ".join(web3_matches)}',
                        suggestion='Add cross-domain tag or remove web3 references',
                    )
            
            elif page.domain == 'web3':
                web2_matches = [term for term in web2_terms if term in content_without_links]
                if web2_matches and 'cross-domain' not in page.tags:
                    self._add_issue(
                        check='cross-domain-contamination',
                        severity='critical',
                        page=page.file_path,
                        message=f'Web3 page contains web2 terms: {", ".join(web2_matches)}',
                        suggestion='Add cross-domain tag or remove web2 references',
                    )
    
    # -------------------------------------------------------------------------
    # Run All Checks
    # -------------------------------------------------------------------------
    
    def run_all_checks(self, specific_checks: Optional[List[str]] = None):
        """Run all or specific lint checks."""
        all_checks = {
            'link-validation': self.check_link_validation,
            'orphan-detection': self.check_orphan_detection,
            'stale-claims': self.check_stale_claims,
            'duplicates': self.check_duplicates,
            'frontmatter': self.check_frontmatter,
            'index-coverage': self.check_index_coverage,
            'provenance': self.check_provenance,
            'tag-validity': self.check_tag_validity,
            'page-type-validity': self.check_page_type_validity,
            'cross-domain-contamination': self.check_cross_domain_contamination,
        }
        
        if specific_checks:
            for check_name in specific_checks:
                if check_name in all_checks:
                    all_checks[check_name]()
                else:
                    print(f"Warning: Unknown check: {check_name}", file=sys.stderr)
        else:
            for check_func in all_checks.values():
                check_func()
        
        return self.issues


# ============================================================================
# Output Formatters
# ============================================================================

def format_text(report: LintReport, verbose: bool = False) -> str:
    """Format lint report as text."""
    lines = []
    lines.append("=" * 70)
    lines.append("WIKI LINT REPORT")
    lines.append("=" * 70)
    lines.append(f"Wiki Path: {report.wiki_path}")
    lines.append(f"Timestamp: {report.timestamp}")
    lines.append(f"Total Pages: {report.total_pages}")
    lines.append(f"Total Issues: {len(report.issues)}")
    lines.append(f"  Critical: {report.critical_count}")
    lines.append(f"  Warning: {report.warning_count}")
    lines.append(f"  Info: {report.info_count}")
    lines.append("=" * 70)
    lines.append("")
    
    if not report.issues:
        lines.append("All checks passed!")
        return '\n'.join(lines)
    
    # Group by severity
    for severity in ('critical', 'warning', 'info'):
        severity_issues = [i for i in report.issues if i.severity == severity]
        if not severity_issues:
            continue
        
        lines.append(f"\n{severity.upper()} ISSUES ({len(severity_issues)})")
        lines.append("-" * 70)
        
        for issue in severity_issues:
            lines.append(f"\n[{issue.check}] {issue.page}")
            lines.append(f"  Message: {issue.message}")
            if issue.suggestion:
                lines.append(f"  Suggestion: {issue.suggestion}")
            if verbose and issue.details:
                lines.append(f"  Details: {issue.details}")
    
    lines.append("\n" + "=" * 70)
    lines.append(f"Exit Code: {report.exit_code}")
    lines.append("=" * 70)
    
    return '\n'.join(lines)


def format_json(report: LintReport) -> str:
    """Format lint report as JSON."""
    output = {
        'wiki_path': report.wiki_path,
        'timestamp': report.timestamp,
        'total_pages': report.total_pages,
        'summary': {
            'total_issues': len(report.issues),
            'critical': report.critical_count,
            'warning': report.warning_count,
            'info': report.info_count,
        },
        'issues': [asdict(i) for i in report.issues],
        'exit_code': report.exit_code,
    }
    return json.dumps(output, indent=2)


def format_markdown(report: LintReport) -> str:
    """Format lint report as markdown."""
    lines = []
    lines.append("# Wiki Lint Report")
    lines.append("")
    lines.append(f"**Wiki Path:** {report.wiki_path}")
    lines.append(f"**Timestamp:** {report.timestamp}")
    lines.append(f"**Total Pages:** {report.total_pages}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Critical | {report.critical_count} |")
    lines.append(f"| Warning | {report.warning_count} |")
    lines.append(f"| Info | {report.info_count} |")
    lines.append(f"| **Total** | **{len(report.issues)}** |")
    lines.append("")
    
    if not report.issues:
        lines.append("All checks passed!")
        return '\n'.join(lines)
    
    # Group by check
    by_check = defaultdict(list)
    for issue in report.issues:
        by_check[issue.check].append(issue)
    
    for check_name, issues in sorted(by_check.items()):
        lines.append(f"## {check_name}")
        lines.append("")
        
        for issue in issues:
            severity_emoji = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}[issue.severity]
            lines.append(f"### {severity_emoji} {issue.page}")
            lines.append("")
            lines.append(f"**Message:** {issue.message}")
            lines.append("")
            if issue.suggestion:
                lines.append(f"**Suggestion:** {issue.suggestion}")
                lines.append("")
    
    lines.append("---")
    lines.append(f"**Exit Code:** {report.exit_code}")
    
    return '\n'.join(lines)


# ============================================================================
# Main
# ============================================================================

def auto_fix_issues(issues: List[LintIssue], wiki_path: str) -> List[LintIssue]:
    """Attempt to auto-fix issues where possible."""
    fixed = []
    remaining = []
    
    for issue in issues:
        if issue.check == 'link-validation' and issue.severity == 'critical':
            # Try to fix broken links by finding similar page titles
            # Extract the broken link target from the message
            match = re.search(r'Broken link: \[\[([^\]]+)\]\]', issue.message)
            if match:
                broken_target = match.group(1)
                # Find similar pages
                pages = load_wiki_pages(wiki_path)
                page_titles = [p.title for p in pages]
                
                # Look for exact match (case-insensitive)
                for title in page_titles:
                    if title.lower() == broken_target.lower():
                        # Found a case mismatch - could fix
                        remaining.append(issue)
                        break
                else:
                    # No fix available
                    remaining.append(issue)
            else:
                remaining.append(issue)
        elif issue.check == 'frontmatter':
            # Frontmatter issues require manual intervention
            remaining.append(issue)
        elif issue.check == 'tag-validity':
            # Tag issues require manual intervention (need to update taxonomy or page)
            remaining.append(issue)
        else:
            remaining.append(issue)
    
    return remaining


def main():
    parser = argparse.ArgumentParser(
        description='Automated lint checks for the security wiki.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('wiki_path', help='Path to the wiki directory')
    parser.add_argument('-c', '--check', help='Run specific check (comma-separated)')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'markdown'], default='text', help='Output format')
    parser.add_argument('-s', '--severity', choices=['critical', 'warning', 'info'], default='info', help='Minimum severity to report')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Load valid tags from taxonomy
    LintChecker.load_valid_tags(args.wiki_path)
    
    # Load pages
    pages = load_wiki_pages(args.wiki_path)
    
    if not pages:
        print("No wiki pages found.", file=sys.stderr)
        sys.exit(1)
    
    # Run lint checks
    checker = LintChecker(pages, args.wiki_path)
    
    specific_checks = None
    if args.check:
        specific_checks = [c.strip() for c in args.check.split(',')]
    
    issues = checker.run_all_checks(specific_checks)
    
    # Filter by severity
    severity_levels = {'critical': 0, 'warning': 1, 'info': 2}
    min_level = severity_levels.get(args.severity, 2)
    issues = [i for i in issues if severity_levels.get(i.severity, 2) <= min_level]
    
    # Auto-fix if requested
    if args.fix:
        print("Attempting to auto-fix issues...", file=sys.stderr)
        issues = auto_fix_issues(issues, args.wiki_path)
        print(f"Auto-fix complete. {len(issues)} issues remain.", file=sys.stderr)
    
    # Create report
    report = LintReport(
        wiki_path=args.wiki_path,
        timestamp=datetime.now().isoformat(),
        total_pages=len(pages),
        issues=issues,
    )
    
    # Format output
    if args.format == 'json':
        output = format_json(report)
    elif args.format == 'markdown':
        output = format_markdown(report)
    else:
        output = format_text(report, verbose=args.verbose)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    sys.exit(report.exit_code)


if __name__ == '__main__':
    main()
