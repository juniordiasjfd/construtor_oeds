import csv

from django.views import View
from django.http import HttpResponse
from django.utils.html import strip_tags

from oeds.models import Oed


class ExportarOedsCSVView(View):

    def get(self, request, *args, **kwargs):

        filename = f"oeds_report.csv"

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        response.write("\ufeff")
        writer = csv.writer(response)

        # campos do modelo Oed
        fields = [f.name for f in Oed._meta.fields]

        # campos extras
        fields += [
            "atribuido_a",
            "total_pontos_cadastrados",
            "criado_em",
            "criado_por",
            "atualizado_em",
            "atualizado_por",
        ]

        writer.writerow(fields)

        queryset = (
            Oed.objects
            .select_related(
                "status",
                "tipo",
                "projeto",
                "componente",
                "criado_por",
                "atualizado_por",
            )
            .prefetch_related("atribuido_a", "pontos")
        )

        for oed in queryset:

            row = []

            for field in fields:

                if field == "atribuido_a":
                    value = ", ".join(str(u) for u in oed.atribuido_a.all())

                elif field == "total_pontos_cadastrados":
                    value = oed.total_pontos_cadastrados

                else:
                    value = getattr(oed, field, "")

                    if value is None:
                        value = ""

                    elif not isinstance(value, (str, int, float, bool)):
                        value = str(value)

                if isinstance(value, str):
                    value = strip_tags(value)

                row.append(value)

            writer.writerow(row)

        return response