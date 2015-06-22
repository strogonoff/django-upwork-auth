#!/usr/bin/env python
import os
import sys

# Make our app's module available without installation
sys.path.insert(0, os.path.abspath('..'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
