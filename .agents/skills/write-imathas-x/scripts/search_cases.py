# /// script
# requires-python = ">=3.10"
# ///

import os
import argparse
import re
from pathlib import Path

def parse_frontmatter(content):
    """Simple parser for YAML frontmatter at the top of markdown files."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL | re.MULTILINE)
    if not match:
        return {}, content
    
    yaml_str = match.group(1)
    body = match.group(2)
    
    # Very simple manual parse to avoid PyYAML dependency
    data = {}
    for line in yaml_str.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # Clean up quotes and brackets
            val = val.strip('"').strip("'").strip('[').strip(']')
            if ',' in val:
                data[key] = [t.strip().strip('"').strip("'") for t in val.split(',')]
            else:
                data[key] = val
    return data, body

def main():
    parser = argparse.ArgumentParser(description="Lookup Golden Cases from Markdown Repository.")
    parser.add_argument("keyword", help="Search keyword (e.g.: fraction, root, format, ...)")
    parser.add_argument("--cases-dir", default=".agents/skills/write-imathas-x/topics", help="Directory containing markdown cases and cheatsheets")
    args = parser.parse_args()

    cases_dir = Path(args.cases_dir)
    if not cases_dir.exists():
        # Fallback to local directory structure
        potential_dir = Path(__file__).parents[1] / "topics"
        if potential_dir.exists():
            cases_dir = potential_dir
        else:
            print(f"ERROR: Resources directory not found at {cases_dir}")
            return

    keyword_lower = args.keyword.lower()
    results = []

    for md_file in cases_dir.rglob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            metadata, body = parse_frontmatter(content)
            
            # Search in tags, topic, or file content
            tags = metadata.get('tags', [])
            if not isinstance(tags, list):
                tags = [tags]
            
            tags_lower = [str(t).lower() for t in tags]
            topic_lower = str(metadata.get('topic', '')).lower()
            
            if keyword_lower in tags_lower or keyword_lower in topic_lower or keyword_lower in body.lower():
                results.append((metadata, body, md_file.name))

    print("=" * 60)
    print(f" 🎯 GOLDEN CASES LOOKUP RESULTS FOR: '{args.keyword}'")
    print("=" * 60)

    if not results:
        print("\nNo matching results found. Please try another keyword.")
    else:
        for idx, (meta, body, fname) in enumerate(results, 1):
            print(f"\n[{idx}] TOPIC: {meta.get('topic')} (Source: {fname})")
            tags = meta.get('tags', [])
            if isinstance(tags, list):
                print(f"🏷️ TAGS: {', '.join(tags)}")
            else:
                print(f"🏷️ TAGS: {tags}")
            print("\n- " + "-" * 20)
            print(body.strip())
            print("-" * 20)

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
