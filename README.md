# Setup Development Environment

To set up the development environment, follow these steps:

1. **Deactivate and Remove Existing Virtual Environment (if applicable)**:
   ```bash
   deactivate
   rm -rf .venv
   ```

2. **Create and Activate a New Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the Base Ingenious Package**:
   Run the following command to install the `ingenious` package without dependencies:
   ```bash
   pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git#egg=ingenious --force-reinstall
   ```


   This folder includes custom extensions such as models, services, and templates required for extending the base `ingenious` package.

4. **Create a `.gitignore` File**:
   Generate a `.gitignore` file to exclude unnecessary files and directories from version control:
   ```bash
      echo "
   .DS_Store
    /.venv
    /.chainlit
    /.idea
    /.cache
    /env_mkdocs/
    /tmp/context.md
    /tmp/*.db
    /dist/
    /functional_test_outputs/
   __pycache__" > .gitignore
   ```


### 5. **Create Profile and Configure Environment Variables**

Set up the `APPSETTING_INGENIOUS_CONFIG` and `APPSETTING_INGENIOUS_PROFILE` environment variables.


### 6. **Add/Create Template Folders (If not provided)**
   ```bash
   ingen_cli generate-template-folders
   ```

   Check the `ingenious_extensions` and `tmp` folder in your project root directory. Ensure it contains the following structure:
   ```
   tmp/
   ├── context.md
   ingenious_extensions/
   ├── local_files/
   ├── models/
   ├── services/
   ├── templates/
   └── tests/
   ```

### 7. **Run Tests**
Execute the test batch using the following command:
```bash
ingen_cli run-test-batch
```


### 8. **AI Test Harness**

```bash
python ingenious_extensions/tests/run_flask_app.py
```

### 9. **CLI Test Harness**

```bash
python ingenious_extensions/tests/run_ingen_cli.py
```

You are now ready to begin development using the `ingenious` package!

##this is a commit test
