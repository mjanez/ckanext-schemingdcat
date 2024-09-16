from __future__ import annotations
import logging
from typing import Any

import ckan.plugins as p
from ckan import types

import ckanext.schemingdcat.config as sdct_config
from ckanext.schemingdcat.helpers import schemingdcat_update_open_data_statistics

log = logging.getLogger(__name__)

def get_subscriptions():
    return {
        p.toolkit.signals.action_succeeded: [
            {"sender": "bulk_update_public", "receiver": stats_changed},
            {"sender": "bulk_update_private", "receiver": stats_changed},
            {"sender": "bulk_update_delete", "receiver": stats_changed},
            {"sender": "package_create", "receiver": stats_changed},
            {"sender": "package_update", "receiver": stats_changed},
            {"sender": "package_delete", "receiver": stats_changed},
            {"sender": "group_create", "receiver": stats_changed},
            {"sender": "group_update", "receiver": stats_changed},
            {"sender": "group_delete", "receiver": stats_changed},
            {"sender": "organization_create", "receiver": stats_changed},
            {"sender": "organization_update", "receiver": stats_changed},
            {"sender": "organization_delete", "receiver": stats_changed},
        ]
    }
    
def stats_changed(sender: str, **kwargs: Any):
    """
    Handles the event when certain actions are performed and updates site statistics.

    Args:
        sender (str): The name of the sender that triggered the event.
        **kwargs (Any): Additional keyword arguments passed to the function.

    Raises:
        Exception: If updating site statistics fails, an error is logged.
    """
    try:
        schemingdcat_update_open_data_statistics()
        log.debug(f"schemingdcat subscription -> [{sender}]. Update Open Data site statistics")
    except Exception as e:
        log.error(f"Failed to Update Open Data site statistics: {e}")