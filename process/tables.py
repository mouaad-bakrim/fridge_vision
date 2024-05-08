import django_tables2 as tables

from process.models import Process


class ProcessListTable(tables.Table):
    name = tables.TemplateColumn(
        '<a href="{% url "process:Detail_Process" record.id %}">{{ record.name}}</a>',
        verbose_name="name")


    image = tables.TemplateColumn(
        '''<div class="d-flex align-items-center">
																			<div class="symbol symbol-50px me-3">
																						<img src="{{ record.image.url }}" class="" alt="" />
																					</div>
																					
																				</div>''',

        verbose_name="Image"
    )



    created_at = tables.DateColumn(format='d/m/Y', orderable=True, verbose_name="Date")

    class Meta:
        model = Process
        fields = ("image","name", "created_at")
        attrs = {
            "class": "table table-bordered table-striped table-hover text-gray-600 table-heading table-datatable dataTable g-3 fs-7"
        }
        per_page = 100
        template_name = 'django_tables2/bootstrap.html'
