#!/usr/bin/env python3
"""Read-only adoption inventory. No native builds, dispatch, or GitHub mutation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import urllib.request

BASE = 'e86c15ca0479240a0045ebc80c83973137b58c60'
REPO = 'techrote/radiCADSAC'
OUT = Path('.mc-inventory')
OUT.mkdir(exist_ok=True)

def get(path):
    req = urllib.request.Request('https://api.github.com/repos/' + REPO + '/' + path,
        headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

def pages(path):
    data = []
    page = 1
    while True:
        part = get(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
        if not isinstance(part, list):
            raise ValueError('Expected paginated list: ' + path)
        data.extend(part)
        if len(part) < 100:
            return data
        page += 1

main = get('git/ref/heads/main')['object']['sha']
if main != BASE:
    raise SystemExit('Baseline moved; reconcile before adoption: ' + main)
issues = pages('issues?state=all')
comments = {}
for item in issues:
    if item['comments']:
        comments[str(item['number'])] = pages(f"issues/{item['number']}/comments")
summary = {'baseline': BASE, 'main': main, 'issues_and_prs': issues,
           'comments': comments, 'milestones': pages('milestones?state=all'),
           'labels': pages('labels'), 'rulesets': pages('rulesets'),
           'branches': pages('branches'), 'workflow_runs': get('actions/runs?per_page=30')}
(OUT / 'github-state.json').write_text(json.dumps(summary, indent=2) + '\n')
subprocess.run(['git', 'archive', '--format=tar.gz', '--output=' + str(OUT / 'baseline.tar.gz'), BASE], check=True)
files = subprocess.check_output(['git', 'ls-tree', '-r', '--full-tree', BASE], text=True)
(OUT / 'tree.txt').write_text(files)
print('Baseline', BASE)
print('Open issues/PRs', [(i['number'], i['title']) for i in issues if i['state'] == 'open'])
print('Milestones', [(m['number'], m['title'], m['state']) for m in summary['milestones']])
print('Labels', [x['name'] for x in summary['labels']])
print('Comments', {k: len(v) for k, v in comments.items()})
print('Read-only archive', hashlib.sha256((OUT / 'baseline.tar.gz').read_bytes()).hexdigest())
print('No native geometry, production bootstrap, issue changes, workflow dispatch, or runner changes executed.')
