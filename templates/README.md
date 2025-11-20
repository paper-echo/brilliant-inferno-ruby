# SSM Parameter Templates

This directory contains JSON template files for creating SSM parameters with pre-populated values.

## Template Format

Each template file should be a JSON file. The **entire JSON object** will be serialized as a JSON string and used as the parameter value.

Example template:

```json
{
  "username": "username",
  "password": "password",
  "account_type": "email",
  "mfa_enabled": true,
  "mfa_backup": "your-mfa-secret-here",
  "notes": "Email username"
}
```

This will be converted to a JSON string and used as the SSM parameter value:
```
{"username": "username", "password": "password", "account_type": "email", "mfa_enabled": true, "mfa_backup": "your-mfa-secret-here", "notes": "Email username"}
```

**Note:** The entire template JSON becomes the parameter value. The parameter `name`, `type`, and `description` are entered manually during parameter creation.

## Usage

When you select "Create from Template" in the SSM Manager:
1. Choose a template from the list
2. The entire template JSON will be serialized and pre-fill the value field
3. You'll be prompted to enter:
   - Parameter name (e.g., `/app/config/database-url`)
   - Parameter type (String, StringList, or SecureString)
   - Description (optional)
4. You can edit the pre-filled JSON string value before saving

## Example Templates

- `database-connection.json` - Template for database connection strings
- `api-key.json` - Template for API keys

## Creating New Templates

Simply create a new `.json` file in this directory following the format above. The file name (without extension) will be used as the template name in the selection menu.

