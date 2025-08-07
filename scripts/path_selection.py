import json
from pathlib import Path

# def select_uncovered_path(coverage_report_path, src_path, test_path):

src_path = '../astropy/astropy/io/fits/connect.py'
coverage_report_path = '../astropy/coverage.json'

with open(coverage_report_path, 'r') as f:
    cov_report = json.load(f)
    # Get index of relevant file
    cov_files = list(cov_report['files'].keys())
    for file in cov_files:
        path_cov = file.replace('/', '__')
        path_src = str(Path(src_path).resolve()).replace('/', '__')
        if path_cov in path_src:
            key_file = file
            break
    missed_lines = cov_report['files'][key_file]['missing_lines']
    missed_branches = cov_report['files'][key_file]['missing_branches']

print(missed_lines)
print(missed_branches)

methodDict = get_mut_paths(src_path)

for method, paths in methodDict.items():
    if method != 'is_fits': continue
    candidate_paths = []
    for path in paths:
        cnt_missed_lines = 0
        cnt_missed_branches = 0
        for line in missed_lines:
            for edge in path:
                if line >= edge[0] and line <= edge[1]:
                    cnt_missed_lines+=1
        for a,b in pairwise(path):
            for branch in missed_branches:
                if a[0]<=branch[0] and a[1]>=branch[0] and b[0]<=branch[1] and b[1]>=branch[1]:
                    cnt_missed_branches += 1
        missed_score = cnt_missed_lines + cnt_missed_branches
        if missed_score <= 0: continue
        # if selected_count >= MAX_SELECTED_CONST: continue
        candidate_paths.append(path)
    print(candidate_paths)
