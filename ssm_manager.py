#!/usr/bin/env python3
"""
SSM Parameter Store Manager - A CLI tool to manage AWS SSM parameters.
"""

import boto3
import click
import questionary
from typing import List, Dict, Optional
import sys
import json
import os
from pathlib import Path


class SSMManager:
    def __init__(self, region: Optional[str] = None):
        """Initialize SSM client."""
        self.ssm = boto3.client('ssm', region_name=region) if region else boto3.client('ssm')
    
    def list_parameters(self, path_prefix: str = '/') -> List[Dict]:
        """Fetch all parameters from SSM Parameter Store."""
        parameters = []
        paginator = self.ssm.get_paginator('describe_parameters')
        
        try:
            for page in paginator.paginate(ParameterFilters=[]):
                for param in page['Parameters']:
                    parameters.append({
                        'Name': param['Name'],
                        'Type': param.get('Type', 'String'),
                        'LastModifiedDate': param.get('LastModifiedDate', 'N/A'),
                        'Description': param.get('Description', '')
                    })
        except Exception as e:
            click.echo(f"Error fetching parameters: {e}", err=True)
            sys.exit(1)
        
        return parameters
    
    def get_parameter_value(self, name: str, decrypt: bool = True) -> Optional[str]:
        """Get the value of a specific parameter."""
        try:
            response = self.ssm.get_parameter(Name=name, WithDecryption=decrypt)
            return response['Parameter']['Value']
        except self.ssm.exceptions.ParameterNotFound:
            return None
        except Exception as e:
            click.echo(f"Error getting parameter value: {e}", err=True)
            return None
    
    def update_parameter(self, name: str, value: str, parameter_type: str = 'String', description: Optional[str] = None) -> bool:
        """Update an existing parameter."""
        try:
            kwargs = {
                'Name': name,
                'Value': value,
                'Type': parameter_type,
                'Overwrite': True
            }
            if description:
                kwargs['Description'] = description
            
            self.ssm.put_parameter(**kwargs)
            return True
        except Exception as e:
            click.echo(f"Error updating parameter: {e}", err=True)
            return False
    
    def create_parameter(self, name: str, value: str, parameter_type: str = 'String', description: Optional[str] = None) -> bool:
        """Create a new parameter."""
        try:
            kwargs = {
                'Name': name,
                'Value': value,
                'Type': parameter_type
            }
            if description:
                kwargs['Description'] = description
            
            self.ssm.put_parameter(**kwargs)
            return True
        except self.ssm.exceptions.ParameterAlreadyExists:
            click.echo(f"Parameter {name} already exists. Use update command instead.", err=True)
            return False
        except Exception as e:
            click.echo(f"Error creating parameter: {e}", err=True)
            return False
    
    def delete_parameter(self, name: str) -> bool:
        """Delete a parameter."""
        try:
            self.ssm.delete_parameter(Name=name)
            return True
        except self.ssm.exceptions.ParameterNotFound:
            click.echo(f"Parameter {name} not found.", err=True)
            return False
        except Exception as e:
            click.echo(f"Error deleting parameter: {e}", err=True)
            return False


@click.group()
@click.option('--region', help='AWS region (default: uses AWS config)')
@click.pass_context
def cli(ctx, region):
    """SSM Parameter Store Manager - Manage AWS SSM parameters interactively."""
    ctx.ensure_object(dict)
    ctx.obj['manager'] = SSMManager(region=region)


@cli.command()
@click.pass_context
def list(ctx):
    """List all SSM parameters and select one to view or update."""
    manager = ctx.obj['manager']
    
    click.echo("Fetching parameters from SSM Parameter Store...")
    parameters = manager.list_parameters()
    
    if not parameters:
        click.echo("No parameters found in SSM Parameter Store.")
        return
    
    # Format parameter list for selection
    choices = []
    for param in parameters:
        display_name = f"{param['Name']} ({param['Type']})"
        if param['Description']:
            display_name += f" - {param['Description']}"
        choices.append(questionary.Choice(title=display_name, value=param['Name']))
    
    # Add option to create new parameter
    choices.append(questionary.Choice(title="[Create New Parameter]", value="__CREATE_NEW__"))
    
    # Add option to delete parameter
    choices.append(questionary.Choice(title="[Delete Parameter]", value="__DELETE__"))
    
    # Add option to quit
    choices.append(questionary.Choice(title="[Quit]", value="__QUIT__"))
    
    selected = questionary.select(
        "Select a parameter (or choose an action):",
        choices=choices
    ).ask()
    
    if not selected:
        click.echo("Cancelled.")
        return
    
    if selected == "__QUIT__":
        click.echo("Goodbye!")
        return
    
    if selected == "__CREATE_NEW__":
        create_parameter_flow(manager)
    elif selected == "__DELETE__":
        delete_parameter_interactive(manager, parameters)
    else:
        # Parameter selected - show view/update options
        parameter_action(manager, selected, parameters)


def delete_parameter_interactive(manager: SSMManager, parameters: List[Dict]):
    """Interactive deletion of a parameter."""
    click.echo("\nDelete Parameter")
    
    if not parameters:
        click.echo("No parameters available to delete.")
        return
    
    # Format parameter list for selection
    choices = []
    for param in parameters:
        display_name = f"{param['Name']} ({param['Type']})"
        if param['Description']:
            display_name += f" - {param['Description']}"
        choices.append(questionary.Choice(title=display_name, value=param['Name']))
    
    selected = questionary.select(
        "Select a parameter to delete:",
        choices=choices
    ).ask()
    
    if not selected:
        click.echo("Cancelled.")
        return
    
    # Show parameter info before deletion
    param_info = next((p for p in parameters if p['Name'] == selected), None)
    click.echo(f"\nParameter to delete: {selected}")
    if param_info:
        click.echo(f"Type: {param_info['Type']}")
        if param_info['Description']:
            click.echo(f"Description: {param_info['Description']}")
    
    # Confirm deletion
    if questionary.confirm("⚠️  Are you sure you want to delete this parameter? This action cannot be undone.", default=False).ask():
        if manager.delete_parameter(selected):
            click.echo(f"✓ Successfully deleted {selected}")
        else:
            click.echo(f"✗ Failed to delete {selected}")
    else:
        click.echo("Cancelled.")


def parameter_action(manager: SSMManager, param_name: str, parameters: List[Dict]):
    """Show view/update options for a selected parameter."""
    param_info = next((p for p in parameters if p['Name'] == param_name), None)
    
    if not param_info:
        click.echo(f"Parameter {param_name} not found.")
        return
    
    action = questionary.select(
        f"What would you like to do with '{param_name}'?",
        choices=[
            questionary.Choice("View", value="view"),
            questionary.Choice("Update", value="update"),
        ]
    ).ask()
    
    if not action:
        click.echo("Cancelled.")
        return
    
    if action == "view":
        view_parameter(manager, param_name, param_info)
    elif action == "update":
        update_existing_parameter(manager, param_name)


def view_parameter(manager: SSMManager, param_name: str, param_info: Dict):
    """Display parameter details."""
    click.echo(f"\n{'='*60}")
    click.echo(f"Parameter: {param_name}")
    click.echo(f"{'='*60}")
    
    click.echo(f"Type: {param_info['Type']}")
    
    if param_info.get('Description'):
        click.echo(f"Description: {param_info['Description']}")
    
    if param_info.get('LastModifiedDate') and param_info['LastModifiedDate'] != 'N/A':
        click.echo(f"Last Modified: {param_info['LastModifiedDate']}")
    
    # Get and display the value
    value = manager.get_parameter_value(param_name)
    if value is None:
        click.echo("\n⚠️  Could not retrieve parameter value.")
    else:
        click.echo(f"\nValue:")
        click.echo(f"{'-'*60}")
        # Show full value, but format nicely if it's long
        if len(value) > 200:
            click.echo(value[:200])
            click.echo(f"... (truncated, full length: {len(value)} characters)")
        else:
            click.echo(value)
        click.echo(f"{'-'*60}")
    
    click.echo(f"\n{'='*60}\n")
    
    # Option to go back or update
    next_action = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice("Update this parameter", value="update"),
            questionary.Choice("Go back", value="back"),
        ]
    ).ask()
    
    if next_action == "update":
        update_existing_parameter(manager, param_name)


def update_existing_parameter(manager: SSMManager, param_name: str):
    """Interactive update of an existing parameter."""
    click.echo(f"\nUpdating parameter: {param_name}")
    
    # Get current value
    current_value = manager.get_parameter_value(param_name)
    if current_value is None:
        click.echo(f"Could not retrieve current value for {param_name}")
        return
    
    click.echo(f"Current value: {current_value[:100]}{'...' if len(current_value) > 100 else ''}")
    
    # Get new value
    new_value = questionary.text(
        "Enter new value:",
        default=current_value
    ).ask()
    
    if not new_value:
        click.echo("Cancelled.")
        return
    
    # Confirm update
    if questionary.confirm("Update this parameter?").ask():
        if manager.update_parameter(param_name, new_value):
            click.echo(f"✓ Successfully updated {param_name}")
        else:
            click.echo(f"✗ Failed to update {param_name}")
    else:
        click.echo("Cancelled.")


def get_templates_directory() -> Path:
    """Get the templates directory path."""
    script_dir = Path(__file__).parent
    return script_dir / "templates"


def list_templates() -> List[Dict[str, str]]:
    """List all available template files."""
    templates_dir = get_templates_directory()
    templates = []
    
    if not templates_dir.exists():
        return templates
    
    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file, 'r') as f:
                template_data = json.load(f)
                templates.append({
                    'file': str(template_file),
                    'name': template_file.stem,
                    'data': template_data
                })
        except (json.JSONDecodeError, KeyError) as e:
            click.echo(f"Warning: Could not parse template {template_file.name}: {e}", err=True)
            continue
    
    return templates


def create_parameter_flow(manager: SSMManager):
    """Flow to choose between creating new or from template."""
    click.echo("\nCreate Parameter")
    
    choice = questionary.select(
        "How would you like to create the parameter?",
        choices=[
            questionary.Choice("Create New", value="new"),
            questionary.Choice("Create from Template", value="template"),
        ]
    ).ask()
    
    if not choice:
        click.echo("Cancelled.")
        return
    
    if choice == "new":
        create_new_parameter(manager)
    elif choice == "template":
        create_from_template(manager)


def create_from_template(manager: SSMManager):
    """Create a parameter from a template with editing capability."""
    templates = list_templates()
    
    if not templates:
        click.echo("No templates found in the templates directory.")
        click.echo("Creating a new parameter instead...")
        create_new_parameter(manager)
        return
    
    # Let user select a template
    choices = [
        questionary.Choice(
            title=f"{t['name']} - {t['data'].get('description', 'No description')}",
            value=idx
        )
        for idx, t in enumerate(templates)
    ]
    
    selected_idx = questionary.select(
        "Select a template:",
        choices=choices
    ).ask()
    
    if selected_idx is None:
        click.echo("Cancelled.")
        return
    
    template = templates[selected_idx]
    template_data = template['data']
    
    click.echo(f"\nUsing template: {template['name']}")
    click.echo("You can edit the values before saving.\n")
    
    # Pre-populate with template values, but allow editing
    name = questionary.text(
        "Parameter name:",
        default=template_data.get('name', ''),
        validate=lambda text: len(text) > 0 or "Parameter name cannot be empty"
    ).ask()
    
    if not name:
        click.echo("Cancelled.")
        return
    
    value = questionary.text(
        "Parameter value:",
        default=template_data.get('value', ''),
        validate=lambda text: len(text) > 0 or "Parameter value cannot be empty"
    ).ask()
    
    if not value:
        click.echo("Cancelled.")
        return
    
    # Determine default type index
    template_type = template_data.get('type', 'String')
    type_choices = ["String", "StringList", "SecureString"]
    default_type_idx = type_choices.index(template_type) if template_type in type_choices else 0
    
    param_type = questionary.select(
        "Parameter type:",
        choices=[
            questionary.Choice("String", value="String"),
            questionary.Choice("StringList", value="StringList"),
            questionary.Choice("SecureString", value="SecureString"),
        ],
        default=type_choices[default_type_idx]
    ).ask()
    
    if not param_type:
        click.echo("Cancelled.")
        return
    
    description = questionary.text(
        "Description (optional):",
        default=template_data.get('description', '')
    ).ask()
    
    # Show summary and confirm
    click.echo("\n--- Parameter Summary ---")
    click.echo(f"Name: {name}")
    click.echo(f"Type: {param_type}")
    click.echo(f"Value: {value[:50]}{'...' if len(value) > 50 else ''}")
    if description:
        click.echo(f"Description: {description}")
    click.echo("------------------------\n")
    
    # Confirm creation
    if questionary.confirm("Create this parameter?").ask():
        if manager.create_parameter(name, value, param_type, description):
            click.echo(f"✓ Successfully created {name}")
        else:
            click.echo(f"✗ Failed to create {name}")
    else:
        click.echo("Cancelled.")


def create_new_parameter(manager: SSMManager):
    """Interactive creation of a new parameter."""
    click.echo("\nCreating new parameter")
    
    # Get parameter details
    name = questionary.text(
        "Parameter name (e.g., /app/config/database-url):",
        validate=lambda text: len(text) > 0 or "Parameter name cannot be empty"
    ).ask()
    
    if not name:
        click.echo("Cancelled.")
        return
    
    value = questionary.text(
        "Parameter value:",
        validate=lambda text: len(text) > 0 or "Parameter value cannot be empty"
    ).ask()
    
    if not value:
        click.echo("Cancelled.")
        return
    
    param_type = questionary.select(
        "Parameter type:",
        choices=[
            questionary.Choice("String", value="String"),
            questionary.Choice("StringList", value="StringList"),
            questionary.Choice("SecureString", value="SecureString"),
        ],
        default="String"
    ).ask()
    
    if not param_type:
        click.echo("Cancelled.")
        return
    
    description = questionary.text(
        "Description (optional):",
    ).ask()
    
    # Confirm creation
    if questionary.confirm("Create this parameter?").ask():
        if manager.create_parameter(name, value, param_type, description):
            click.echo(f"✓ Successfully created {name}")
        else:
            click.echo(f"✗ Failed to create {name}")
    else:
        click.echo("Cancelled.")


@cli.command()
@click.pass_context
def create(ctx):
    """Create a new SSM parameter."""
    manager = ctx.obj['manager']
    create_parameter_flow(manager)


@cli.command()
@click.argument('name')
@click.pass_context
def get(ctx, name):
    """Get the value of a specific parameter."""
    manager = ctx.obj['manager']
    value = manager.get_parameter_value(name)
    
    if value is None:
        click.echo(f"Parameter {name} not found.", err=True)
        sys.exit(1)
    
    click.echo(value)


@cli.command()
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete(ctx, name, force):
    """Delete a specific parameter."""
    manager = ctx.obj['manager']
    
    if not force:
        if not questionary.confirm(
            f"⚠️  Are you sure you want to delete parameter '{name}'? This action cannot be undone.",
            default=False
        ).ask():
            click.echo("Cancelled.")
            return
    
    if manager.delete_parameter(name):
        click.echo(f"✓ Successfully deleted {name}")
    else:
        click.echo(f"✗ Failed to delete {name}")
        sys.exit(1)


if __name__ == '__main__':
    cli()

