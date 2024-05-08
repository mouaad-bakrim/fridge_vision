from django_tables2 import SingleTableView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_tables2.config import RequestConfig
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from mailer import send_html_mail



def format_phone(phone_number):
    if not phone_number:
        return ""
    stripped_phone = phone_number.strip().replace(" ","").replace(".","").replace("-","")
    if len(stripped_phone)==10 and stripped_phone.isdigit():
        return "%s%s %s%s %s%s %s%s %s%s" % tuple(stripped_phone)
    elif len(stripped_phone)==13 and stripped_phone.startswith("+212"):
        return "+212 %s %s%s %s%s %s%s %s%s" % tuple(stripped_phone[4:])
    elif len(stripped_phone)==14 and stripped_phone.startswith("00212"):
        return "00212 %s %s%s %s%s %s%s %s%s" % tuple(stripped_phone[5:])
    else:
        return phone_number.strip()

class PagedFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = super(PagedFilteredTableView, self).get_queryset()
        if self.filter_class:
            self.filter = self.filter_class(self.request.GET, queryset=qs)
            self.filter.form.helper = self.formhelper_class()
            qs = self.filter.qs
        return qs

    def get_context_data(self, **kwargs):
        context = super(PagedFilteredTableView, self).get_context_data()
        if self.filter_class:
            context[self.context_filter_name] = self.filter
        return context

    def get_filter_kwargs(self):
        return {self.request}


