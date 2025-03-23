# chunked-flow

• It is an asynchronous, chunk-based data processing system.<br>
• The system fetches records in batches from a database.<br>
• Each batch of data is transformed into a structured format.<br>
• The data is then GZIP-compressed and uploaded to an Amazon S3 bucket.<br>
• A corresponding metadata file is also generated and stored on S3, detailing which files were uploaded.<br>
• Overall flow:

1. Establish a database connection.
2. Retrieve records in chunks.
3. Build a processed payload.
4. Compress and upload the payload to S3.
5. Create and upload a metadata file summarizing the uploads.

• The project includes concurrency handling, ensuring multiple chunks can be processed in parallel (up to a defined limit).


## Getting started

### Install dependencies using [UV](https://docs.astral.sh/uv/getting-started/) :
```sh
uv sync
 ```

### Activate environment:
```sh
source .venv/bin/activate
```
### Create ``.env`` file (or rename and modify ``.env.example``) in project root and set environment variables
```sh
cp .env.example .env
```

### To run lint:
```sh
uv run ruff check .
```

### To run formatter:
```sh
uv run ruff format .
```

### To run tests:
```sh
uv run pytest
```

### To run project
```sh
uv run src/chunk/main/main.py
```


### Pre-Commit Hooks

To ensure code quality and consistency, we use pre-commit hooks.
Once installed, navigate to your repository's root directory and run:
```sh
uv run pre-commit install
```
This will install the hooks specified in the .pre-commit-config.yaml file. From then on, pre-commit will run automatically on every commit, checking for formatting, linting, and other issues. If you want to run pre-commit manually, you can use the command:
```sh
uv run pre-commit run --all-files
```
