import sentry_pagerduty
import pygerduty
from sentry_pagerduty.forms import PagerDutyConfigForm
from sentry.plugins.bases.notify import NotifyPlugin


class PagerDutyPlugin(NotifyPlugin):
    """
    Sentry plugin to send errors stats to Pagerduty.
    """
    author = 'Depop developers'
    author_url = 'https://github.com/depop/sentry-pagerduty'
    version = sentry_pagerduty.VERSION
    description = 'Send error occurence to Pagerduty.'
    slug = 'pagerduty'
    title = 'Pagerduty'
    conf_key = slug
    conf_title = title
    resource_links = [
        ('Source', 'https://github.com/depop/sentry-pagerduty'),
        ('Bug Tracker', 'https://github.com/depop/sentry-pagerduty/issues'),
        ('README', 'https://github.com/depop/sentry-pagerduty/blob/master/README.rst'),
    ]
    project_conf_form = PagerDutyConfigForm

    def is_configured(self, project, **kwargs):
        params = self.get_option
        return (params('api_key', project) and
                params('service_key', project) and
                params('domain_name', project))

    def notify_users(self, group, event, fail_silently=False):
        if not self.is_configured(group.project):
            return

        api_key = self.get_option('api_key', group.project)
        domain_name = self.get_option('domain_name', group.project)
        service_key = self.get_option('service_key', group.project)
        description = event.message[:1024]
        details = {
            'event_id': event.event_id,
            'project': group.project.name,
            'release': event.get_tag('sentry:release'),
            'platform': event.platform,
            'culprit': event.culprit,
            'message': event.message,
            'datetime': event.datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'time_spent': event.time_spent,
            'tags': dict(event.get_tags()),
            'url': group.get_absolute_url(),
        }

        client = pygerduty.PagerDuty(domain_name, api_key)
        client.trigger_incident(service_key, description, details=details, client='sentry', client_url=group.get_absolute_url())
