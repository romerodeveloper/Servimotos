from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView


from django.db.models.functions import Coalesce
from django.db.models import Sum, DecimalField

from reports.forms import ReportForm
from ventas.models import Venta


class ReportVentaView(TemplateView):
    template_name = 'report_venta.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                search = Venta.objects.all()
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for s in search:
                    data.append([
                        s.id,
                        s.use.username,
                        s.date_joined.strftime('%Y-%m-%d'),
                        format(s.subtotal, '.1f'),
                        format(s.iva, '.1f'),
                        format(s.total, '.1f'),
                    ])

                subtotal = search.aggregate(r=Coalesce(Sum('subtotal'), 0, output_field=DecimalField())).get('r')
                iva = search.aggregate(r=Coalesce(Sum('iva'), 0, output_field=DecimalField())).get('r')
                total = search.aggregate(r=Coalesce(Sum('total'), 0, output_field=DecimalField())).get('r')

                data.append([
                    '---',
                    '---',
                    'TOTAL VENTAS',
                    format(subtotal, '.1f'),
                    format(iva, '.1f'),
                    format(total, '.1f'),
                ])


            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Ventas'
        context['entity'] = 'Reportes'
        context['list_url'] = reverse_lazy('venta_report')
        context['form'] = ReportForm()
        return context


