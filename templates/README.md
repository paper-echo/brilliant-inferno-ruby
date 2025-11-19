# SSM Parameter Templates

This directory contains JSON template files for creating SSM parameters with pre-populated values.

## Template Format

Each template file should be a JSON file with the following structure:

```json
{
  "name": "/app/config/parameter-name",
  "value": "default-value-here",
  "type": "SecureString",
  "description": "Description of what this parameter is for"
}
```

## Fields

- **name** (required): The default parameter name/path
- **value** (required): The default value for the parameter
- **type** (optional): Parameter type - `String`, `StringList`, or `SecureString` (default: `String`)
- **description** (optional): Description of the parameter

## Usage

When you select "Create from Template" in the SSM Manager, you can choose from templates in this directory. The template values will pre-populate the form, but you can edit them before saving.

## Example Templates

- `database-connection.json` - Template for database connection strings
- `api-key.json` - Template for API keys

## Creating New Templates

Simply create a new `.json` file in this directory following the format above. The file name (without extension) will be used as the template name in the selection menu.

