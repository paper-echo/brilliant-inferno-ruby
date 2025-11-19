# How to Use SSM Parameter Store Manager

This guide will walk you through using the SSM Parameter Store Manager CLI tool step by step.

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.7+** installed
2. **AWS credentials configured** (via `aws configure`, environment variables, or IAM role)
3. **Appropriate IAM permissions** for SSM Parameter Store operations

## Initial Setup

### 1. Activate the Virtual Environment

Every time you open a new terminal, activate the virtual environment:

```bash
cd /Users/cristopherontiveros/Desktop/secret
source venv/bin/activate
```

You'll know it's activated when you see `(venv)` at the beginning of your terminal prompt.

### 2. Verify Installation

Check that the tool is working:

```bash
python ssm_manager.py --help
```

You should see a list of available commands.

## Common Use Cases

### Use Case 1: List and Update an Existing Parameter

**Scenario:** You want to see all your SSM parameters and update one of them.

**Steps:**

1. Run the list command:
   ```bash
   python ssm_manager.py list
   ```

2. The tool will fetch all parameters and display them in an interactive menu:
   ```
   Fetching parameters from SSM Parameter Store...
   ? Select a parameter to update (or create new):
   ❯ /app/config/database-url (String) - Database connection URL
     /app/config/api-key (SecureString) - API key for external service
     /app/config/feature-flag (String) - Feature toggle
     [Create New Parameter]
   ```

3. Use arrow keys to navigate and press Enter to select a parameter.

4. You'll see the current value:
   ```
   Updating parameter: /app/config/database-url
   Current value: postgresql://localhost:5432/mydb
   ```

5. Enter the new value (the current value is pre-filled):
   ```
   ? Enter new value: postgresql://localhost:5432/mydb
   ```

6. Confirm the update:
   ```
   ? Update this parameter? (y/n) y
   ✓ Successfully updated /app/config/database-url
   ```

### Use Case 2: Create a New Parameter

**Scenario:** You need to add a new configuration parameter to SSM.

**Method 1: From the List Menu**

1. Run `python ssm_manager.py list`
2. Select `[Create New Parameter]` from the menu
3. Follow the prompts

**Method 2: Direct Create Command**

1. Run the create command:
   ```bash
   python ssm_manager.py create
   ```

2. Enter the parameter name:
   ```
   ? Parameter name (e.g., /app/config/database-url): /app/config/new-setting
   ```

3. Enter the parameter value:
   ```
   ? Parameter value: my-secret-value
   ```

4. Select the parameter type:
   ```
   ? Parameter type:
   ❯ String
     StringList
     SecureString
   ```
   - **String**: Regular text value
   - **StringList**: Comma-separated list of values
   - **SecureString**: Encrypted value (recommended for secrets)

5. Optionally add a description:
   ```
   ? Description (optional): This is my new configuration setting
   ```

6. Confirm creation:
   ```
   ? Create this parameter? (y/n) y
   ✓ Successfully created /app/config/new-setting
   ```

### Use Case 3: Get a Parameter Value

**Scenario:** You want to quickly retrieve the value of a specific parameter.

**Steps:**

1. Run the get command with the parameter name:
   ```bash
   python ssm_manager.py get /app/config/database-url
   ```

2. The value will be printed to stdout:
   ```
   postgresql://localhost:5432/mydb
   ```

**Tip:** You can pipe this to other commands or save it to a file:
```bash
python ssm_manager.py get /app/config/database-url > db_url.txt
```

### Use Case 4: Working with Different AWS Regions

**Scenario:** Your parameters are in a specific AWS region.

**Steps:**

1. Use the `--region` flag:
   ```bash
   python ssm_manager.py --region us-west-2 list
   ```

2. Or for other commands:
   ```bash
   python ssm_manager.py --region eu-central-1 create
   python ssm_manager.py --region ap-southeast-1 get /app/config/key
   ```

## Command Reference

### `list` - List and Update Parameters

```bash
python ssm_manager.py list
python ssm_manager.py --region us-east-1 list
```

**What it does:**
- Fetches all parameters from SSM Parameter Store
- Displays them in an interactive menu
- Allows you to select and update any parameter
- Option to create a new parameter from the menu

### `create` - Create New Parameter

```bash
python ssm_manager.py create
python ssm_manager.py --region us-west-2 create
```

**What it does:**
- Interactive prompts to create a new parameter
- Asks for name, value, type, and optional description
- Validates input before creating

### `get` - Get Parameter Value

```bash
python ssm_manager.py get <parameter-name>
python ssm_manager.py --region eu-central-1 get /app/config/api-key
```

**What it does:**
- Retrieves and displays the value of a specific parameter
- Automatically decrypts SecureString parameters
- Exits with error code if parameter not found

### `--help` - Show Help

```bash
python ssm_manager.py --help
python ssm_manager.py list --help
```

## Tips and Best Practices

### 1. Parameter Naming Convention

Use hierarchical paths for better organization:
- ✅ Good: `/app/production/database-url`
- ✅ Good: `/app/staging/api-key`
- ❌ Avoid: `database-url` (no path structure)

### 2. Parameter Types

- **String**: Use for non-sensitive configuration (URLs, feature flags)
- **SecureString**: Use for secrets (passwords, API keys, tokens)
- **StringList**: Use for comma-separated values (e.g., `value1,value2,value3`)

### 3. Working with SecureString

SecureString parameters are automatically decrypted when retrieved. The tool handles encryption/decryption transparently.

### 4. Bulk Operations

For bulk operations, you might want to script this tool:
```bash
#!/bin/bash
source venv/bin/activate
python ssm_manager.py get /app/config/key1
python ssm_manager.py get /app/config/key2
```

### 5. Error Handling

If you see errors:
- **"Parameter not found"**: Check the parameter name spelling
- **"Access denied"**: Verify your AWS credentials and IAM permissions
- **"Region not found"**: Check the region name is valid

## Troubleshooting

### Issue: "No module named 'boto3'"

**Solution:** Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Issue: "Unable to locate credentials"

**Solution:** Configure AWS credentials:
```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Issue: "AccessDeniedException"

**Solution:** Your IAM user/role needs these permissions:
- `ssm:DescribeParameters`
- `ssm:GetParameter`
- `ssm:PutParameter`

### Issue: Interactive menu not showing properly

**Solution:** Make sure your terminal supports ANSI colors and is at least 80 characters wide.

## Examples

### Example 1: Update Database URL

```bash
$ source venv/bin/activate
$ python ssm_manager.py list
Fetching parameters from SSM Parameter Store...
? Select a parameter to update (or create new): /app/db/url
Updating parameter: /app/db/url
Current value: postgresql://old-host:5432/db
? Enter new value: postgresql://new-host:5432/db
? Update this parameter? (y/n) y
✓ Successfully updated /app/db/url
```

### Example 2: Create Secure API Key

```bash
$ python ssm_manager.py create
? Parameter name: /app/api/external-key
? Parameter value: sk_live_1234567890abcdef
? Parameter type: SecureString
? Description (optional): External API key for payment processing
? Create this parameter? (y/n) y
✓ Successfully created /app/api/external-key
```

### Example 3: Quick Value Retrieval

```bash
$ python ssm_manager.py get /app/config/version
1.2.3
```

## Next Steps

- Explore all your parameters with `python ssm_manager.py list`
- Create parameters for your application configuration
- Use SecureString for any sensitive values
- Organize parameters using hierarchical paths

For more information, see the main [README.md](README.md) file.

