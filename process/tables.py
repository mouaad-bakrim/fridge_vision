import django_tables2 as tables
from process.models import Process

class ProcessListTable(tables.Table):
    usability = tables.TemplateColumn(
        '<a href="{% url "process:Detail_Process"  record.id%}">{{ record.usability }}</a>',
        verbose_name="Usability",
        attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}}
    )

    etat = tables.TemplateColumn(
        '<a>{{ record.etat }}</a>',
        verbose_name="Etat",
        attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}}
    )
    brand = tables.TemplateColumn(
        '<a>{{ record.brand }}</a>',
        verbose_name="Brand",
        attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}}
    )
    score = tables.TemplateColumn(
        '<a>{{ record.score }}</a>',
        verbose_name="Note",
        attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}}
    )


    image = tables.TemplateColumn(
        '''
     {% if record.image %}
    <div class="d-flex align-items-center">
        <div class="symbol symbol-50px me-3">
            <img src="{{ record.image.url }}" class="" alt="" />
        </div>
    </div>
{% else %}
 <div class="d-flex align-items-center">
        <div class="symbol symbol-50px me-3">
    <img src="https://png.pngtree.com/thumb_back/fh260/background/20230929/pngtree-this-is-a-refrigerator-in-a-home-image_13301679.jpg" class="" alt="" />
        </div>
    </div>


{% endif %}

        ''',
        verbose_name="Image",
        attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}}
    )

    created_at = tables.DateColumn(format='d/m/Y', orderable=True, verbose_name="Date",
                                   attrs={"th": {"class": "text-center"}})

    class Meta:
        model = Process
        fields = ("image", "usability", "brand", "etat", "score", "created_at")
        attrs = {
            "class": "table table-bordered table-striped table-hover text-gray-100 table-heading table-datatable dataTable g-2 fs-6"
        }
        per_page = 10
        template_name = 'django_tables2/bootstrap.html'
