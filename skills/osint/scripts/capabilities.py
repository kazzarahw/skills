#!/usr/bin/env python3
"""Deterministic capability probe for the osint skill.

Answers one question in under a second — what can this environment actually do —
so the agent never assumes a key or a binary it does not have, and never stops
because one is missing.

SECRETS ARE NEVER PRINTED. This script reports only whether a variable is
``set`` or ``unset`` and whether a binary is ``present`` or ``missing``. It
never prints a value, a length, a prefix, or a hash of a value. Nothing in the
output can be used to reconstruct a credential.

Standard library only, Python 3.8+. No network calls.

Usage:
    capabilities.py                 human table grouped by section
    capabilities.py --json          machine-readable object
    capabilities.py --check NAME    one token on stdout: set|unset|present|missing|unknown
    capabilities.py --env-file .env also treat keys from a .env file as configured
"""

import argparse
import json
import os
import shutil
import sys


class _Parser(argparse.ArgumentParser):
    """argparse exits 2 on a bad flag, which would collide with "a gate refused".

    Keeping usage errors at 1 is what makes exit 2 mean exactly one thing: the script looked at
    your data and declined. An agent that cannot tell a mistyped flag from a detected credential
    will eventually report one as the other.
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(1)

from pathlib import Path

# Bins without which an investigation cannot proceed at all.
TIER0_TOOLS = ("python3", "curl", "dig", "whois")

# Display order for the human table.
ENV_GROUP_ORDER = (
    "search",
    "infrastructure",
    "threat-intel",
    "breach",
    "blockchain",
    "phone",
    "corporate",
    "social",
    "media",
    "egress",
)

TOOL_GROUP_ORDER = (
    "shell",
    "dns",
    "crypto",
    "media",
    "username",
    "phone",
    "recon",
    "osint",
)

# One entry per environment variable the skill can use.
#   name    variable name, reported verbatim
#   group   which workflow family it belongs to
#   service vendor or product it configures
#   tier    1 = free key or free account, 2 = paid only
#   url     vendor account or docs page; "" when the variable is not a vendor
#           credential and has no account page
ENV_VARS = [
    # --- search ---------------------------------------------------------
    {"name": "SERPER_API_KEY", "group": "search", "service": "Serper",
     "tier": 1, "url": "https://serper.dev/"},
    {"name": "SERPAPI_API_KEY", "group": "search", "service": "SerpApi",
     "tier": 1, "url": "https://serpapi.com/"},
    {"name": "BRAVE_API_KEY", "group": "search", "service": "Brave Search",
     "tier": 1, "url": "https://api-dashboard.search.brave.com/"},
    {"name": "TAVILY_API_KEY", "group": "search", "service": "Tavily",
     "tier": 1, "url": "https://app.tavily.com/"},
    {"name": "EXA_API_KEY", "group": "search", "service": "Exa",
     "tier": 1, "url": "https://dashboard.exa.ai/"},
    {"name": "GOOGLE_CSE_API_KEY", "group": "search", "service": "Google Programmable Search",
     "tier": 1, "url": "https://developers.google.com/custom-search/v1/overview"},
    {"name": "GOOGLE_CSE_ID", "group": "search", "service": "Google Programmable Search",
     "tier": 1, "url": "https://developers.google.com/custom-search/v1/overview"},
    # Bing Search API was decommissioned 2025-08-11 and signup is closed, so it is
    # deliberately absent: https://learn.microsoft.com/en-us/lifecycle/announcements/bing-search-api-retirement
    # --- infrastructure -------------------------------------------------
    {"name": "SHODAN_API_KEY", "group": "infrastructure", "service": "Shodan",
     "tier": 1, "url": "https://account.shodan.io/"},
    {"name": "CENSYS_API_ID", "group": "infrastructure", "service": "Censys",
     "tier": 1, "url": "https://search.censys.io/account/api"},
    {"name": "CENSYS_API_SECRET", "group": "infrastructure", "service": "Censys",
     "tier": 1, "url": "https://search.censys.io/account/api"},
    {"name": "FOFA_KEY", "group": "infrastructure", "service": "FOFA",
     "tier": 2, "url": "https://fofa.info/"},
    {"name": "NETLAS_API_KEY", "group": "infrastructure", "service": "Netlas",
     "tier": 1, "url": "https://app.netlas.io/"},
    {"name": "IPINFO_TOKEN", "group": "infrastructure", "service": "ipinfo",
     "tier": 1, "url": "https://ipinfo.io/account/token"},
    {"name": "SECURITYTRAILS_KEY", "group": "infrastructure", "service": "SecurityTrails",
     "tier": 1, "url": "https://securitytrails.com/app/api"},
    {"name": "HUNTERIO_API_KEY", "group": "infrastructure", "service": "Hunter.io",
     "tier": 1, "url": "https://hunter.io/api_keys/new"},
    {"name": "BUILDWITH_API_KEY", "group": "infrastructure", "service": "BuildWith",
     "tier": 2, "url": "https://buildwith.com/"},
    {"name": "URLSCAN_API_KEY", "group": "infrastructure", "service": "urlscan.io",
     "tier": 1, "url": "https://urlscan.io/account/apikey/"},
    {"name": "CRIMINALIP_API_KEY", "group": "infrastructure", "service": "Criminal IP",
     "tier": 1, "url": "https://www.criminalip.io/"},
    {"name": "LEAKIX_API_KEY", "group": "infrastructure", "service": "LeakIX",
     "tier": 1, "url": "https://leakix.net/"},
    {"name": "ABUSECHECK_API_KEY", "group": "infrastructure", "service": "abuse.ch",
     "tier": 1, "url": "https://abuse.ch/"},
    # --- threat intel ---------------------------------------------------
    {"name": "VIRUSTOTAL_API_KEY", "group": "threat-intel", "service": "VirusTotal",
     "tier": 1, "url": "https://www.virustotal.com/gui/my-apikey"},
    {"name": "ABUSEIPDB_API_KEY", "group": "threat-intel", "service": "AbuseIPDB",
     "tier": 1, "url": "https://www.abuseipdb.com/account/api"},
    {"name": "GREYNOISE_API_KEY", "group": "threat-intel", "service": "GreyNoise",
     "tier": 1, "url": "https://viz.greynoise.io/account/api-key"},
    {"name": "OTX_API_KEY", "group": "threat-intel", "service": "AlienVault OTX",
     "tier": 1, "url": "https://otx.alienvault.com/"},
    {"name": "PULSEDIVE_API_KEY", "group": "threat-intel", "service": "Pulsedive",
     "tier": 1, "url": "https://pulsedive.com/"},
    # --- breach ---------------------------------------------------------
    {"name": "HIBP_API_KEY", "group": "breach", "service": "Have I Been Pwned",
     "tier": 2, "url": "https://haveibeenpwned.com/API/Key"},
    {"name": "LEAKCHECK_API_KEY", "group": "breach", "service": "LeakCheck",
     "tier": 1, "url": "https://leakcheck.io/"},
    # LeakCheck's own Python wrapper documents LEAKCHECK_APIKEY (no underscore before KEY);
    # the ecosystem convention is LEAKCHECK_API_KEY. Both are accepted, because a user
    # who sets the vendor's name must not see the probe report the credential as absent.
    {"name": "LEAKCHECK_APIKEY", "group": "breach", "service": "LeakCheck (vendor spelling)",
     "tier": 1, "url": "https://leakcheck.io/"},
    {"name": "INTELX_API_KEY", "group": "breach", "service": "Intelligence X",
     "tier": 1, "url": "https://intelx.io/account?tab=developer"},
    {"name": "SNUSBASE_API_KEY", "group": "breach", "service": "Snusbase",
     "tier": 1, "url": "https://snusbase.com/"},
    {"name": "DEHASHED_API_KEY", "group": "breach", "service": "DeHashed",
     "tier": 2, "url": "https://dehashed.com/"},
    {"name": "HUDSONROCK_API_KEY", "group": "breach", "service": "Hudson Rock",
     "tier": 1, "url": "https://www.hudsonrock.com/threat-intelligence-cybersecurity-tools"},
    # --- blockchain -----------------------------------------------------
    {"name": "ETHERSCAN_API_KEY", "group": "blockchain", "service": "Etherscan",
     "tier": 1, "url": "https://etherscan.io/myapikey"},
    {"name": "BLOCKCHAIR_API_KEY", "group": "blockchain", "service": "Blockchair",
     "tier": 1, "url": "https://blockchair.com/api"},
    {"name": "MEMPOOLSPACE_API_KEY", "group": "blockchain", "service": "mempool.space",
     "tier": 1, "url": "https://mempool.space/api"},
    {"name": "ARKHAM_API_KEY", "group": "blockchain", "service": "Arkham Intelligence",
     "tier": 1, "url": "https://intel.arkm.com/"},
    {"name": "DUNE_API_KEY", "group": "blockchain", "service": "Dune Analytics",
     "tier": 1, "url": "https://dune.com/account/api-keys"},
    {"name": "ETHPLORER_API_KEY", "group": "blockchain", "service": "Ethplorer",
     "tier": 1, "url": "https://ethplorer.io/"},
    {"name": "BITQUERY_API_KEY", "group": "blockchain", "service": "Bitquery",
     "tier": 1, "url": "https://bitquery.io/"},
    # --- phone ----------------------------------------------------------
    {"name": "NUMVERIFY_API_KEY", "group": "phone", "service": "Numverify",
     "tier": 1, "url": "https://numverify.com/product"},
    {"name": "ABSTRACT_API_KEY", "group": "phone", "service": "Abstract API",
     "tier": 1, "url": "https://www.abstractapi.com/"},
    {"name": "TWILIO_ACCOUNT_SID", "group": "phone", "service": "Twilio",
     "tier": 2, "url": "https://console.twilio.com/"},
    {"name": "TWILIO_AUTH_TOKEN", "group": "phone", "service": "Twilio",
     "tier": 2, "url": "https://console.twilio.com/"},
    {"name": "OPENCNAM_API_KEY", "group": "phone", "service": "OpenCNAM",
     "tier": 1, "url": "https://www.opencnam.com/"},
    # --- corporate ------------------------------------------------------
    {"name": "OPENCORPORATES_API_TOKEN", "group": "corporate", "service": "OpenCorporates",
     "tier": 2, "url": "https://api.opencorporates.com/"},
    {"name": "OPENSANCTIONS_API_KEY", "group": "corporate", "service": "OpenSanctions",
     "tier": 1, "url": "https://www.opensanctions.org/api/"},
    {"name": "ALEPH_CLIENT_ID", "group": "corporate", "service": "Aleph (OCCRP)",
     "tier": 1, "url": "https://aleph.occrp.org/"},
    {"name": "ALEPH_CLIENT_SECRET", "group": "corporate", "service": "Aleph (OCCRP)",
     "tier": 1, "url": "https://aleph.occrp.org/"},
    {"name": "COMPANIES_HOUSE_API_KEY", "group": "corporate", "service": "Companies House",
     "tier": 1, "url": "https://find-and-update.company-information.service.gov.uk/"},
    {"name": "USPTO_API_KEY", "group": "corporate", "service": "USPTO Open Data Portal",
     "tier": 1, "url": "https://data.uspto.gov/"},
    # --- social ---------------------------------------------------------
    {"name": "GITHUB_TOKEN", "group": "social", "service": "GitHub",
     "tier": 1, "url": "https://github.com/settings/tokens"},
    {"name": "GITLAB_TOKEN", "group": "social", "service": "GitLab",
     "tier": 1, "url": "https://gitlab.com/-/user_settings/personal_access_tokens"},
    {"name": "TWITTER_BEARER_TOKEN", "group": "social", "service": "X (Twitter) API",
     "tier": 2, "url": "https://developer.x.com/en/portal/dashboard"},
    {"name": "REDDIT_CLIENT_ID", "group": "social", "service": "Reddit",
     "tier": 1, "url": "https://www.reddit.com/prefs/apps"},
    {"name": "REDDIT_CLIENT_SECRET", "group": "social", "service": "Reddit",
     "tier": 1, "url": "https://www.reddit.com/prefs/apps"},
    {"name": "MASTODON_ACCESS_TOKEN", "group": "social", "service": "Mastodon",
     "tier": 1, "url": "https://mastodon.social/settings/applications"},
    {"name": "YOUTUBE_API_KEY", "group": "social", "service": "YouTube Data API",
     "tier": 1, "url": "https://console.cloud.google.com/apis/credentials"},
    {"name": "TELEGRAM_BOT_TOKEN", "group": "social", "service": "Telegram",
     "tier": 1, "url": "https://core.telegram.org/bots"},
    # --- media ----------------------------------------------------------
    {"name": "GOOGLE_MAPS_API_KEY", "group": "media", "service": "Google Maps Platform",
     "tier": 2, "url": "https://console.cloud.google.com/apis/credentials"},
    {"name": "MAPBOX_TOKEN", "group": "media", "service": "Mapbox",
     "tier": 1, "url": "https://account.mapbox.com/access-tokens/"},
    {"name": "GEOAPIFY_API_KEY", "group": "media", "service": "Geoapify",
     "tier": 1, "url": "https://www.geoapify.com/"},
    {"name": "TINEYE_API_KEY", "group": "media", "service": "TinEye",
     "tier": 2, "url": "https://tineye.com/api"},
    {"name": "OPENAI_API_KEY", "group": "media", "service": "OpenAI",
     "tier": 2, "url": "https://platform.openai.com/api-keys"},
    {"name": "ANTHROPIC_API_KEY", "group": "media", "service": "Anthropic",
     "tier": 2, "url": "https://console.anthropic.com/settings/keys"},
    {"name": "MLT_ACCESS_TOKEN", "group": "media", "service": "MLT",
     "tier": 1, "url": ""},
    # --- egress ---------------------------------------------------------
    {"name": "HTTP_PROXY", "group": "egress", "service": "egress proxy",
     "tier": 1, "url": ""},
    {"name": "HTTPS_PROXY", "group": "egress", "service": "egress proxy",
     "tier": 1, "url": ""},
    {"name": "ALL_PROXY", "group": "egress", "service": "egress proxy",
     "tier": 1, "url": ""},
    {"name": "NO_PROXY", "group": "egress", "service": "egress proxy",
     "tier": 1, "url": ""},
]

# One entry per local binary. `bin` is what shutil.which looks up on PATH.
#   bin     executable name
#   group   workflow family
#   purpose one line on what it buys you
#   install the real command to obtain it
LOCAL_TOOLS = [
    {"bin": "python3", "group": "shell", "purpose": "Run this skill's scripts and one-off parsing",
     "install": "apt install python3"},
    {"bin": "curl", "group": "shell", "purpose": "Fetch URLs, headers, and page bodies",
     "install": "apt install curl"},
    {"bin": "jq", "group": "shell", "purpose": "Parse JSON responses without writing a parser",
     "install": "apt install jq"},
    {"bin": "git", "group": "shell", "purpose": "Clone repositories and read public commit history",
     "install": "apt install git"},
    {"bin": "tor", "group": "shell", "purpose": "Route requests through Tor to separate research identity",
     "install": "apt install tor"},
    {"bin": "dig", "group": "dns", "purpose": "DNS records, delegation, and reverse lookups",
     "install": "apt install dnsutils"},
    {"bin": "whois", "group": "dns", "purpose": "Registry, registrar, and nameserver attribution",
     "install": "apt install whois"},
    {"bin": "openssl", "group": "crypto", "purpose": "Certificate chains, TLS inspection, digests",
     "install": "apt install openssl"},
    {"bin": "sha256sum", "group": "crypto", "purpose": "Hash a downloaded file for the evidence log",
     "install": "apt install coreutils"},
    {"bin": "exiftool", "group": "media", "purpose": "Read and strip image metadata including EXIF GPS",
     "install": "apt install libimage-exiftool-perl"},
    {"bin": "yt-dlp", "group": "media", "purpose": "Video and audio metadata, subtitles, comments",
     "install": "pip install yt-dlp"},
    {"bin": "ffprobe", "group": "media", "purpose": "Probe duration, streams, and resolution",
     "install": "apt install ffmpeg"},
    {"bin": "ffmpeg", "group": "media", "purpose": "Cut clips, convert formats, extract frames and audio",
     "install": "apt install ffmpeg"},
    {"bin": "sherlock", "group": "username", "purpose": "Username enumeration across 500+ sites",
     "install": "pip install sherlock-project"},
    {"bin": "maigret", "group": "username", "purpose": "Username enumeration with profile content",
     "install": "pip install maigret"},
    {"bin": "phoneinfoga", "group": "phone", "purpose": "Scan a number for carrier, line type, and location",
     "install": "go install github.com/sundowndev/phoneinfoga@latest"},
    {"bin": "subfinder", "group": "recon", "purpose": "Subdomain enumeration from passive sources",
     "install": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"},
    {"bin": "amass", "group": "recon", "purpose": "In-depth DNS and subdomain enumeration",
     "install": "go install github.com/owasp-amass/amass/v4/...@master"},
    {"bin": "gau", "group": "recon", "purpose": "Pull known URLs from Common Crawl, Wayback, and OTX",
     "install": "go install github.com/lc/gau/v2/cmd/gau@latest"},
    {"bin": "assetfinder", "group": "recon", "purpose": "Subdomain enumeration from passive sources",
     "install": "go install github.com/tomnomnom/assetfinder@latest"},
    {"bin": "httpx", "group": "recon",
     "purpose": "Probe hosts for liveness, titles, and tech — ProjectDiscovery build, verify with `httpx -version`",
     "install": "go install github.com/projectdiscovery/httpx/cmd/httpx@latest"},
    {"bin": "dnsx", "group": "recon", "purpose": "Fast DNS resolution and record enumeration",
     "install": "go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest"},
    {"bin": "massdns", "group": "recon", "purpose": "High-performance DNS brute force",
     "install": "apt install massdns"},
    {"bin": "waybackurls", "group": "recon", "purpose": "Fetch Wayback Machine URLs for a domain",
     "install": "go install github.com/tomnomnom/waybackurls@latest"},
    {"bin": "gf", "group": "recon", "purpose": "Grep pattern filters over waybackurls output",
     "install": "go install github.com/tomnomnom/gf@latest"},
    {"bin": "spiderfoot", "group": "osint", "purpose": "Automated multi-module OSINT correlation",
     "install": "pip install spiderfoot"},
    {"bin": "recon-ng", "group": "osint", "purpose": "Modular OSINT framework",
     "install": "pip install recon-ng"},
    {"bin": "theharvester", "group": "osint", "purpose": "Harvest emails, hosts, and IPs from search engines",
     "install": "pip install theHarvester"},
    {"bin": "holehe", "group": "osint", "purpose": "Check an email's registration across 120+ sites",
     "install": "pip install holehe"},
    {"bin": "ghunt", "group": "osint", "purpose": "Social media OSINT from a username or phone number",
     "install": "pip install ghunt"},
    {"bin": "infoga", "group": "osint", "purpose": "Extract email address information from a domain",
     "install": "go install github.com/soxoj/infoga@latest"},
]

NOT_STATED = "— NOT STATED —"


# --------------------------------------------------------------------------
# Capability group (a): environment variables
# --------------------------------------------------------------------------

def parse_env_file(path):
    """Read a .env-style file into a name -> value map.

    Ignores blank lines, comment lines, and `export ` prefixes, and strips
    surrounding quotes. Values are used only to decide set versus unset and
    are never returned to the caller for display.
    """
    values = {}
    try:
        with open(str(path), "r", encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError:
        return values

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or key[0].isdigit():
            continue
        if not all(char.isalnum() or char == "_" for char in key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1].strip()
        values[key] = value
    return values


def is_configured(name, environ, file_vars):
    """True when a variable holds a usable value in the environment or the env file.

    An empty string counts as unset: an exported-but-blank key is not a working
    credential, and reporting it as set would send the agent down a dead path.
    """
    return bool(environ.get(name)) or bool(file_vars.get(name))


def build_env_rows(environ, file_vars):
    """One status row per known variable. Carries status only, never a value."""
    rows = []
    for entry in ENV_VARS:
        rows.append({
            "name": entry["name"],
            "group": entry["group"],
            "service": entry["service"],
            "tier": entry["tier"],
            "url": entry.get("url", ""),
            "status": "set" if is_configured(entry["name"], environ, file_vars) else "unset",
        })
    return rows


# --------------------------------------------------------------------------
# Capability group (b): local tools
# --------------------------------------------------------------------------

def build_tool_rows():
    """One status row per known binary, plus the install command for misses."""
    rows = []
    for entry in LOCAL_TOOLS:
        resolved = shutil.which(entry["bin"])
        rows.append({
            "bin": entry["bin"],
            "group": entry["group"],
            "purpose": entry["purpose"],
            "install": entry["install"],
            "path": resolved or "",
            "status": "present" if resolved else "missing",
        })
    return rows


def tier0_status(tool_rows):
    """Whether the shell essentials are all present — the investigation can start."""
    present = {row["bin"] for row in tool_rows if row["status"] == "present"}
    missing = [name for name in TIER0_TOOLS if name not in present]
    return (not missing), missing


# --------------------------------------------------------------------------
# Roll-up
# --------------------------------------------------------------------------

def build_summary(env_rows, tool_rows, tier0):
    """Per-group set/unset counts — the number the agent actually reasons about."""
    env_counts = {}
    for row in env_rows:
        bucket = env_counts.setdefault(row["group"], {"set": 0, "unset": 0, "total": 0})
        bucket[row["status"]] += 1
        bucket["total"] += 1

    tool_counts = {}
    for row in tool_rows:
        bucket = tool_counts.setdefault(row["group"], {"present": 0, "missing": 0, "total": 0})
        bucket[row["status"]] += 1
        bucket["total"] += 1

    env_set = sum(b["set"] for b in env_counts.values())
    env_total = len(env_rows)
    tool_present = sum(b["present"] for b in tool_counts.values())
    tool_total = len(tool_rows)

    return {
        "line": (
            "env {}/{} set across {} groups; tools {}/{} present across {} groups; tier0 {}".format(
                env_set, env_total, len(env_counts),
                tool_present, tool_total, len(tool_counts),
                "yes" if tier0 else "no",
            )
        ),
        "env": env_counts,
        "tools": tool_counts,
        "totals": {
            "env_set": env_set,
            "env_total": env_total,
            "tools_present": tool_present,
            "tools_total": tool_total,
        },
    }


# --------------------------------------------------------------------------
# Lookup for --check
# --------------------------------------------------------------------------

def check_status(name, env_rows, tool_rows):
    """Resolve one capability name to a single status token.

    Environment variables win over binaries on an exact match, because variable
    names are uppercase and distinct from every binary name the skill probes.
    """
    needle = name.strip()
    if not needle:
        return "unknown"
    lowered = needle.lower()
    for row in env_rows:
        if row["name"].lower() == lowered:
            return row["status"]
    for row in tool_rows:
        if row["bin"].lower() == lowered:
            return row["status"]
    return "unknown"


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def ordered_groups(rows, order, group_key):
    """Groups present in the data, in the requested display order, then any extras."""
    seen = {row[group_key] for row in rows}
    groups = [group for group in order if group in seen]
    groups.extend(sorted(seen - set(groups)))
    return groups


def render_human(env_rows, tool_rows, tier0, summary, env_file):
    lines = ["OSINT capability probe — " + summary["line"]]

    if env_file:
        lines.append("env file: " + str(env_file))
    lines.append("")

    lines.append("ENVIRONMENT VARIABLES")
    for group in ordered_groups(env_rows, ENV_GROUP_ORDER, "group"):
        bucket = summary["env"][group]
        lines.append("  {}  {}/{} set".format(group, bucket["set"], bucket["total"]))
        for row in (r for r in env_rows if r["group"] == group):
            mark = "x" if row["status"] == "set" else " "
            lines.append("    [{}] {:<32} t{}  {:<26} {}".format(
                mark, row["name"], row["tier"], row["service"], row["url"]))
        lines.append("")

    lines.append("LOCAL TOOLS")
    for group in ordered_groups(tool_rows, TOOL_GROUP_ORDER, "group"):
        bucket = summary["tools"][group]
        lines.append("  {}  {}/{} present".format(group, bucket["present"], bucket["total"]))
        for row in (r for r in tool_rows if r["group"] == group):
            if row["status"] == "present":
                lines.append("    [x] {:<14} {:<14} {}".format(
                    row["bin"], row["group"], row["purpose"]))
            else:
                lines.append("    [ ] {:<14} {:<14} {}".format(
                    row["bin"], row["group"], row["purpose"]))
                lines.append("        install: " + row["install"])
        lines.append("")

    if tier0:
        lines.append("tier0 essentials present — passive collection can start.")
    else:
        lines.append("tier0 essentials MISSING — an investigation may be blocked.")
    lines.append("No secret values are reported by this script, only set/unset.")
    return "\n".join(lines).rstrip() + "\n"


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def build_parser():
    parser = _Parser(
        prog="capabilities.py",
        description="Report which API keys and local tools this environment actually has. "
                    "Never prints a secret value.",
    
        epilog="Exit codes: 0 success | 1 usage error | 2 gate refused | 3 environment error.",)
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="print a machine-readable object")
    parser.add_argument("--check", metavar="NAME",
                        help="print one status token for a single variable or binary: "
                             "set, unset, present, missing, or unknown")
    parser.add_argument("--env-file", metavar="PATH", dest="env_file",
                        help="also treat keys from a .env-style file as configured")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    file_vars = {}
    env_file = None
    if args.env_file:
        env_file = Path(args.env_file).expanduser()
        if not env_file.is_file():
            print("warning: env file not found: {}".format(env_file), file=sys.stderr)
        file_vars = parse_env_file(env_file)

    env_rows = build_env_rows(os.environ, file_vars)
    tool_rows = build_tool_rows()
    tier0, tier0_missing = tier0_status(tool_rows)
    summary = build_summary(env_rows, tool_rows, tier0)

    if args.check is not None:
        print(check_status(args.check, env_rows, tool_rows))
        return 0

    if args.as_json:
        print(json.dumps({
            "schema": "osint.capabilities/1",
            "tier0": tier0,
            "tier0_missing": tier0_missing,
            "env_file": str(env_file) if env_file else None,
            "env": env_rows,
            "tools": tool_rows,
            "summary": summary,
        }, indent=2, sort_keys=False))
        return 0

    sys.stdout.write(render_human(env_rows, tool_rows, tier0, summary, env_file))
    return 0


if __name__ == "__main__":
    sys.exit(main())
