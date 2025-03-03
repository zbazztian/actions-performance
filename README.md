# Measure GitHub Actions Performance

This script fetches information from an organization's audit log about past GitHub Actions workflow runs. For each workflow run, it lists the jobs that were executed and for each of these it obtains the timing information for its steps. It also downloads the workflow's yaml definition file, parses it and maps the steps defined therein to the runtime step information obtained from the API. This allows measuring the time it took to execute each Action (indicated by the `uses` keyword in a step's definition).


## Requirements

1. Python 3
2. `pipenv` package manager
3. A `GITHUB_TOKEN` environment variable with a token that has access to read an organization's audit log as well as to all repositories contained in the organization.

## Install the dependencies

```shell
pipenv install
```


## Running the script
```shell
> export GITHUB_TOKEN="YOUR TOKEN HERE"
> ./run.sh
Performance data for job "Analyze (cpp)" in workflow https://github.com/octodemo/codeql-simple-demo/tree/44913721b174229158283fbbe1dc4e5ff78ab7e5/.github/workflows/codeql-analysis.yml
    actions/checkout@v3:  1.0 seconds
    github/codeql-action/init@v2:  41.0 seconds
    github/codeql-action/autobuild@v2:  19.0 seconds
    github/codeql-action/analyze@v2:  27.0 seconds

Performance data for job "Analyze (java)" in workflow https://github.com/octodemo/codeql-simple-demo/tree/44913721b174229158283fbbe1dc4e5ff78ab7e5/.github/workflows/codeql-analysis.yml
    actions/checkout@v3:  1.0 seconds
    github/codeql-action/init@v2:  40.0 seconds
    github/codeql-action/autobuild@v2:  22.0 seconds
    github/codeql-action/analyze@v2:  55.0 seconds

Performance data for job "poll (12.x)" in workflow https://github.com/octodemo/audit-log-polling-service/tree/4b551f57d119e8156f07625a68c587fe7570c884/.github/workflows/audit-log-export-service.js.yml
    actions/checkout@v2:  1.0 seconds
    actions/setup-node@v1:  4.0 seconds
    EndBug/add-and-commit@v5:  0.0 seconds

Performance data for job "stale" in workflow https://github.com/octodemo/filmgirl-stale/tree/41dca33ef0a23b1fd7bcd5104f804d317acf00b3/.github/workflows/stale.yml
    actions/stale@v5:  1.0 seconds

...
```

