from django.shortcuts import render

from base.utils import PagedFilteredTableView
from process.forms import ProcessListFormHelper
from process.models import Process
from process.tables import ProcessListTable
from django.views.generic import DetailView

class ListProcess(PagedFilteredTableView):
    permission_required = 'stock.view_picking'
    model = Process
    table_class = ProcessListTable
    formhelper_class = ProcessListFormHelper
    template_name = 'process_list.html'

    def get_filter_kwargs(self):
        filter_kwargs = {}
        return filter_kwargs

    def get_context_data(self, **kwargs):
        table = self.get_table()
        print(table)
        table.exclude = ['selection', ]
        context = super(ListProcess, self).get_context_data(**kwargs)

        context.update({'active_item': 'process_list', 'active_menu': 'processs', 'table': table})
        return context



class DetailProcess(DetailView):
    template_name = 'process_detail.html'
    model = Process
    context_object_name = 'process'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context.update({


            'active_item': 'process_list',
            'active_menu': 'process',

        })
        return context

