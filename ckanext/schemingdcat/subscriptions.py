from __future__ import annotations
import logging
from typing import Any

import ckan.plugins as p
from ckan import types

import ckanext.schemingdcat.statistics.model as sdct_model

log = logging.getLogger(__name__)

def get_subscriptions():
    return {
        p.toolkit.signals.action_succeeded: [
            {"sender": "bulk_update_public", "receiver": schemingdcat_stats_changed},
            {"sender": "bulk_update_private", "receiver": schemingdcat_stats_changed},
            {"sender": "bulk_update_delete", "receiver": schemingdcat_stats_changed},
            {"sender": "schemingdcat_harvest_package_updated", "receiver": schemingdcat_stats_changed},
            {"sender": "schemingdcat_harvest_package_created", "receiver": schemingdcat_stats_changed},
            {"sender": "package_create", "receiver": schemingdcat_stats_changed},
            {"sender": "package_create_rest", "receiver": schemingdcat_stats_changed},
            {"sender": "package_update", "receiver": schemingdcat_stats_changed},
            {"sender": "package_update_rest", "receiver": schemingdcat_stats_changed},
            {"sender": "package_delete", "receiver": schemingdcat_stats_changed},
            {"sender": "group_create", "receiver": schemingdcat_stats_changed},
            {"sender": "group_update", "receiver": schemingdcat_stats_changed},
            {"sender": "group_delete", "receiver": schemingdcat_stats_changed},
            {"sender": "organization_create", "receiver": schemingdcat_stats_changed},
            {"sender": "organization_update", "receiver": schemingdcat_stats_changed},
            {"sender": "organization_delete", "receiver": schemingdcat_stats_changed},
        ]
    }
    
def schemingdcat_stats_changed(sender: str, **kwargs: Any):
    """
    Handles the event when certain actions are performed and updates site statistics.

    Args:
        sender (str): The name of the sender that triggered the event.
        **kwargs (Any): Additional keyword arguments passed to the function.

    Raises:
        Exception: If updating site statistics fails, an error is logged.
    """
    try:
        log.debug(f"[{sender}] -> Update Open Data site statistics")
        sdct_model.update_table()
    except Exception as e:
        log.error(f"Failed to Update Open Data site statistics: {e}")
