#!/usr/bin/env python3
"""
SSM Parameter Store Manager - A CLI tool to manage AWS SSM parameters.
"""

import boto3
import click
import questionary
from typing import List, Dict, Optional
import sys


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
    """List all SSM parameters and select one to update."""
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
    
    # Add option to quit
    choices.append(questionary.Choice(title="[Quit]", value="__QUIT__"))
    
    selected = questionary.select(
        "Select a parameter to update (or create new):",
        choices=choices
    ).ask()
    
    if not selected:
        click.echo("Cancelled.")
        return
    
    if selected == "__QUIT__":
        click.echo("Goodbye!")
        return
    
    if selected == "__CREATE_NEW__":
        create_new_parameter(manager)
    else:
        update_existing_parameter(manager, selected)


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
    create_new_parameter(manager)


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


if __name__ == '__main__':
    cli()

