# SSM Parameter Store Manager

A command-line tool to interactively manage AWS SSM Parameter Store parameters.

## Features

- 📋 List all parameters from SSM Parameter Store
- ✏️ Select and update parameters interactively
- ➕ Create new parameters with interactive prompts
- 🔍 Get specific parameter values

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials (one of the following):
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - IAM role (if running on EC2)

## Usage

**Note:** Make sure your virtual environment is activated (`source venv/bin/activate`) before running commands.

### List and Update Parameters

List all parameters and interactively select one to update:

```bash
python3 ssm_manager.py list
```

This will:
1. Fetch all parameters from SSM Parameter Store
2. Display them in an interactive menu
3. Allow you to select one to update
4. Prompt for the new value
5. Optionally create a new parameter from the menu

### Create New Parameter

Create a new parameter interactively:

```bash
python3 ssm_manager.py create
```

Or use the script directly:
```bash
./ssm_manager.py create
```

This will prompt you for:
- Parameter name (e.g., `/app/config/database-url`)
- Parameter value
- Parameter type (String, StringList, SecureString)
- Optional description

### Get Parameter Value

Get the value of a specific parameter:

```bash
python3 ssm_manager.py get /path/to/parameter
```

### Options

- `--region`: Specify AWS region (default: uses AWS config)

Example:
```bash
python3 ssm_manager.py --region us-east-1 list
```

## Examples

```bash
# List and update parameters
python3 ssm_manager.py list

# Create a new secure parameter
python3 ssm_manager.py create

# Get a parameter value
python3 ssm_manager.py get /app/database/password
```

## Requirements

- Python 3.7+
- AWS credentials configured
- Appropriate IAM permissions for SSM Parameter Store

## IAM Permissions

Your AWS credentials need the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:DescribeParameters",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:PutParameter"
      ],
      "Resource": "*"
    }
  ]
}
```

