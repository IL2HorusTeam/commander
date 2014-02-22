# -*- coding: utf-8 -*-
"""
Main project views.
"""
import logging

from celery.result import AsyncResult

from coffin.shortcuts import render
from coffin.views.generic import TemplateView

from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext as _

from website.forms import AnonymousContactForm, AuthenticatedContactForm
from website.decorators import ajax_api
from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


class BaseView(TemplateView):
    """
    Extended TemplateView which provides self.extra_context dictionary and
    stores request at self.request.
    """
    def __init__(self, *args, **kwargs):
        self.request = None
        self.extra_context = {}
        super(BaseView, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super(BaseView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.extra_context)


class IndexView(BaseView):
    """
    View for the site frontpage.
    """
    template_name = "website/pages/index.html"


@ajax_api(method='GET')
def api_task_result(request, task_id):
    """
    View which handles AJAX GET requests for getting results of Celery tasks.
    """
    result = AsyncResult(task_id)
    if result.status == 'PENDING':
        return JSONResponse.error(message=_("Unknown task ID."))
    else:
        return JSONResponse.success(payload={
            'ready': result.ready(),
            'result': result.get(),
        })


def contact(request, template_name="website/pages/contact.html"):
    """
    A view for sending messages to support team.
    """
    if not request.method == 'GET':
        return HttpResponseBadRequest()

    form_class = AnonymousContactForm if request.user.is_anonymous() else \
                 AuthenticatedContactForm
    form = form_class()
    context = {
        'form': form,
    }
    return render(request, template_name, context)


@ajax_api()
def api_contact(request):
    """
    Handles AJAX POST requests for sending messages to support team.
    """
