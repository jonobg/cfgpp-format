#!/usr/bin/env python3
"""
Notification system for CFGPP-Format project
Integrates with meta workspace notification infrastructure
"""

from meta_bridge import run_meta_tool

def send_notification(message, priority='info'):
    """
    Send notification through meta workspace system
    """
    return run_meta_tool('notifications', ['send', 'cfgpp-format', priority, message])

def check_notifications():
    """
    Check for incoming notifications
    """
    return run_meta_tool('notifications', ['check', 'cfgpp-format'])
