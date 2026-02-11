from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_projeto'] = 'Em desenvolvimento'
        return context