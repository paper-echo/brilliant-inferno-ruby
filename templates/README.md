# SSM Parameter Templates

This directory contains JSON template files for creating SSM parameters with pre-populated values.

## Template Format

Each template file should be a JSON file with the following structure:

```json
{
  "value": "default-value-here"
}
```

**Note:** Only the `value` field is used from templates. The `name`, `type`, and `description` fields (if present) are ignored and will be entered manually during parameter creation.

## Fields

- **value** (required): The default value for the parameter that will pre-populate the value field

**Optional fields (for reference only, not used by the tool):**
- `name` - Ignored, entered manually
- `type` - Ignored, selected manually  
- `description` - Ignored, entered manually

## Usage

When you select "Create from Template" in the SSM Manager:
1. Choose a template from the list
2. The template's `value` will pre-fill the value field
3. You'll be prompted to enter:
   - Parameter name (e.g., `/app/config/database-url`)
   - Parameter type (String, StringList, or SecureString)
   - Description (optional)
4. You can edit the pre-filled value before saving

## Example Templates

- `database-connection.json` - Template for database connection strings
- `api-key.json` - Template for API keys

## Creating New Templates

Simply create a new `.json` file in this directory following the format above. The file name (without extension) will be used as the template name in the selection menu.

