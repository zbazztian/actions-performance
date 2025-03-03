import base64
import yaml
import requests
import os
from datetime import datetime
from difflib import SequenceMatcher


def similarity(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()


if not os.getenv('GITHUB_TOKEN'):
    print("Error: The environment variable 'GITHUB_TOKEN' is not set.")
    exit(1)

API = "https://api.github.com"
VERSION_HDR = {"X-GitHub-Api-Version": "2022-11-28"}
ACCEPT_HDR = {"Accept": "application/vnd.github+json"}
AUTH_HDR = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}

headers = {
    **AUTH_HDR,
    **ACCEPT_HDR,
    **VERSION_HDR
}

# get the audit log which contains past workflow runs
response = requests.get(f"{API}/orgs/octodemo/audit-log", headers=headers, params={
    # we exclude dependabot worfklow runs, because they have synthetic workflow scripts that do not exist
    "phrase": "action:workflows.completed_workflow_run -actor:dependabot[bot]",
    "per_page": 100  # in production you would use pagination, for this example script we just look at the last 100 entries
})

if response.status_code == 200:   
    log_entries = response.json()

    for log_entry in log_entries:
        event = log_entry['event']
        if event == 'dynamic':
            # skip dynamic events, because they have synthetic workflow scripts that do not exist
            continue

        workflow_run_id = log_entry['workflow_run_id']
        repo = log_entry['repo']
        rev = log_entry['head_sha']

        # get information about the workflow
        response = requests.get(f'{API}/repos/{repo}/actions/runs/{workflow_run_id}', headers=headers)

        if response.status_code == 200:
            run_data = response.json()
            workflow_path = run_data['path']

            # get the workflow file content
            response = requests.get(f'{API}/repos/{repo}/contents/{workflow_path}', headers=headers, params={"ref": rev})

            if response.status_code == 200:                
                workflow_base64 = response.json()['content']
                workflow_yaml = base64.b64decode(workflow_base64).decode('utf-8')
                workflow = yaml.safe_load(workflow_yaml)
                jobs_def = workflow['jobs']

                # retrieve the performance data for all the jobs
                response = requests.get(f'{API}/repos/{repo}/actions/runs/{workflow_run_id}/jobs', headers=headers)

                if response.status_code == 200:
                    jobs_perf = response.json()['jobs']

                    for job_perf in jobs_perf:
                        job_title = job_perf['name']
                        job_steps_perf = job_perf['steps']

                        if not job_steps_perf:
                            # No performance data available, because no steps were executed
                            continue

                        # Iterate through the jobs and find the one that best matches the job_title
                        # Job titles can contain unresolved variables, so this is not a perfect match
                        # We could also use other, potentially structural criteria (number of steps etc.) to find
                        # the job and to make this more accurate
                        job_steps_def = None
                        sim = -1

                        for job_name, job in jobs_def.items():
                            s = similarity(job.get('name', job_name), job_title)
                            if s > sim:
                                sim = s   
                                job_steps_def = job.get('steps', [])
                        
                        if not job_steps_def:
                            # Empty job list. Skipping.
                            continue

                        # Remove the first item of jobs_steps_perf, since it is for the job setup
                        # and only keep the first n items of job_steps_perf, where n is the number of items in job_steps_def.
                        # This is because the performance data contains post run steps.
                        job_steps_perf = job_steps_perf[1:len(job_steps_def) + 1]

                        # Iterate through all job_steps_def and check if there is a "uses" key, if so, print out its value
                        info = []
                        for step_def, step_perf in zip(job_steps_def, job_steps_perf):
                            if 'uses' in step_def:
                                action = step_def['uses']
                                started_at = datetime.strptime(step_perf['started_at'], '%Y-%m-%dT%H:%M:%SZ')
                                completed_at = datetime.strptime(step_perf['completed_at'], '%Y-%m-%dT%H:%M:%SZ')
                                # Calculate the duration in seconds
                                duration = (completed_at - started_at).total_seconds()
                                info.append(f'    {action}:  {duration} seconds')
                        
                        if info:
                            print(f'Performance data for job "{job_title}" in workflow https://github.com/{repo}/tree/{rev}/{workflow_path}')
                            print('\n'.join(info))
                            print()

                else:
                    print(f"Failed to retrieve job data: {response.status_code}")
            else:
                print(f"Failed to retrieve workflow file: {response.status_code}")
        else:
            print(f"Failed to retrieve workflow run data: {response.status_code}")
else:
    print(f"Failed to retrieve audit log data: {response.status_code}. Does your token have the necessary permissions?")
