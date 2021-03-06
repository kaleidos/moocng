# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from fabric.api import (task, run, hide, show)
from fabric.api import settings as fab_settings

from moocng.externalapps.models import ExternalApp


logger = logging.getLogger(__name__)


def exists_instance(instance_name):
    res = run("ls %s" % settings.FABRIC_ASKBOT_INSTANCES_PATH)
    return instance_name in res

#    warn_only=True,
@task()
def create_instance(externalapp_id):
    with fab_settings(
        hide('stdout', 'warnings'),
        show('running', 'stderr'),
    ):
        created = False
        externalapp = ExternalApp.objects.get(pk=externalapp_id)
        instance_name = externalapp.slug
        exists = exists_instance(instance_name)
        if exists:
            created = False
        else:
            instance_type = externalapp.instance_type
            result = run("openmooc-askbot-instancetool -c %s %s_%s" % (instance_name, instance_type, instance_name))
            if result.succeeded:
                result = run("supervisorctl reload")
                if result.succeeded:
                    result = run("service nginx restart")
                    if result.succeeded:
                        created = True
        return created
