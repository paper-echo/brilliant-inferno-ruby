# SSM Parameter Store Manager

A command-line tool to interactively manage AWS SSM Parameter Store parameters.

## Features

- 📋 List all parameters from SSM Parameter Store
- 👁️ View parameter details (name, type, value, description)
- ✏️ Update parameters interactively
- ➕ Create new parameters with interactive prompts
- 📝 Create parameters from templates
- 🗑️ Delete parameters (with confirmation)
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

### List, View, and Update Parameters

List all parameters and interactively select one to view or update:

```bash
python3 ssm_manager.py list
```

This will:
1. Fetch all parameters from SSM Parameter Store
2. Display them in an interactive menu
3. When you select a parameter, choose to **View** or **Update**:
   - **View**: Display parameter details (name, type, value, description, last modified)
   - **Update**: Modify the parameter value
4. Additional menu options:
   - `[Create New Parameter]` - Create a new parameter
   - `[Delete Parameter]` - Delete a parameter
   - `[Quit]` - Exit the tool

### Create New Parameter

Create a new parameter interactively:

```bash
python3 ssm_manager.py create
```

You'll be prompted to choose:
- **Create New**: Create from scratch
- **Create from Template**: Use a pre-configured template

#### Create New
This will prompt you for:
- Parameter name (e.g., `/app/config/database-url`)
- Parameter value
- Parameter type (String, StringList, SecureString)
- Optional description

#### Create from Template
1. Select a template from the `templates/` directory
2. The template's `value` will pre-fill the value field
3. Enter the parameter name, type, and description manually
4. Edit the pre-filled value if needed
5. Review summary and confirm creation

**Templates**: Templates only contain the `value` field. The `name`, `type`, and `description` are entered manually during creation. See `templates/README.md` for format details.

### Get Parameter Value

Get the value of a specific parameter:

```bash
python3 ssm_manager.py get /path/to/parameter
```

### Delete Parameter

Delete a specific parameter:

```bash
# With confirmation prompt
python3 ssm_manager.py delete /path/to/parameter

# Without confirmation (force)
python3 ssm_manager.py delete /path/to/parameter --force
```

You can also delete parameters interactively from the list menu by selecting `[Delete Parameter]`.

### Options

- `--region`: Specify AWS region (default: uses AWS config)

Example:
```bash
python3 ssm_manager.py --region us-east-1 list
```

## Examples

```bash
# List parameters and interact with them (view/update/delete)
python3 ssm_manager.py list

# Create a new parameter (from scratch or template)
python3 ssm_manager.py create

# Get a parameter value
python3 ssm_manager.py get /app/database/password

# Delete a parameter (with confirmation)
python3 ssm_manager.py delete /app/old-config

# Delete a parameter (without confirmation)
python3 ssm_manager.py delete /app/old-config --force

# Use a specific AWS region
python3 ssm_manager.py --region us-west-2 list
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
        "ssm:PutParameter",
        "ssm:DeleteParameter"
      ],
      "Resource": "*"
    }
  ]
}
```

## Templates

The tool supports creating parameters from templates stored in the `templates/` directory. Each template is a JSON file that contains only the `value` field:

```json
{
  "value": "default-value-here"
}
```

**Note:** Only the `value` field is used from templates. The `name`, `type`, and `description` are entered manually during parameter creation.

See `templates/README.md` for more details on creating and using templates.

