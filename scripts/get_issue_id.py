import os
import re
import json
import requests

# TOKEN = 'your token'

def get_issue_id(token, owner, repo, pr_id):
    print(owner, repo, pr_id)
    URL = 'https://api.github.com/graphql'
    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json',
    }
    payload = {
        "query": f'query {{ repository(owner: "{owner}", name: "{repo}") {{ pullRequest(number: {pr_id}) {{ closingIssuesReferences(first: 10) {{ nodes {{ number title url }} }} }} }} }}'
    }

    response = requests.post(URL, json=payload, headers=headers)
    # print(response.status_code)
    # print(response.text)

    if response.status_code != 200:
        return []

    res = response.json()
    issues = res['data']['repository']['pullRequest']['closingIssuesReferences']['nodes']

    # for issue in issues:
    #     print('Number:', issue['number'])
    #     print('Title :', issue['title'])
    #     print('URL   :', issue['url'])


    return issues  # issue_id, issue_title, issue_url


def main():
    json_files = [
        'autocoderover_sonnet_solution_leak.json',
        'swe-agent-1.0-solution_leak.json',
        'openhands_codeact-solution_leak.json',
    ]
    
    for file in json_files:
        print(file)
        with open(file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            pass
        elif isinstance(data, dict):
            data = data['results']
        else:
            print(type(data))
            exit()
        print(type(data))
        print(len(data))
        for i in range(len(data)):
            id = data[i]['instance_id']
            # print(id)
            pr_id, remaining = id.split('-')[-1], "-".join(id.split('-')[:-1])
            owner, repo = remaining.split('__')
            # print(owner, repo, pr_id)
            data[i]['url'] = f'https://github.com/{owner}/{repo}/pull/{pr_id}'

            # issues = get_issue_id(TOKEN, owner, repo, pr_id)
            # data[i]['issues'] = issues


        output_file = "".join(file.split('.')[:-1]) + ".new.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        # break

if __name__ == '__main__':
    main()

