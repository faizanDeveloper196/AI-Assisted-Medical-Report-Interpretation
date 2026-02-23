from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.process_report import process_report
from django.conf import settings
from django.views.generic import TemplateView
import os
import traceback


class HomeView(TemplateView):
    template_name = 'reports/home.html'

    def post(self, request, *args, **kwargs):
        context = {}
        if request.FILES.get('report_file'):
            uploaded_file = request.FILES['report_file']

            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(filename)

            try:
                results = process_report(uploaded_file_path)
                context['results'] = results
                context['file_url'] = fs.url(filename)
                if not results.get('values'):
                    context['debug_text'] = results.get('raw_text', 'No text extracted.')[:500]
            except Exception as e:
                traceback.print_exc()
                context['error'] = f"Error processing file: {str(e)}"

        return render(request, self.template_name, context)

class ReportHistoryView(TemplateView):
    """Render a single history file in the main panel (image/pdf/text)."""

    template_name = 'reports/report_history.html'

    def get(self, request, fname, *args, **kwargs):
        media_dir = settings.MEDIA_ROOT
        safe_path = os.path.join(media_dir, fname)
        if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
            return render(request, self.template_name, {'error': 'File not found.', 'file': None})

        url = settings.MEDIA_URL + fname
        ext = os.path.splitext(fname)[1].lower()
        kind = 'other'
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.jfif']:
            kind = 'image'
        elif ext == '.pdf':
            kind = 'pdf'
        elif ext in ['.txt']:
            kind = 'text'

        context = {}
        try:
            results = process_report(safe_path)
            context['results'] = results
            context['file_url'] = url
            if not results.get('values'):
                context['debug_text'] = results.get('raw_text', 'No text extracted.')[:500]
        except Exception as e:
            traceback.print_exc()
            context['error'] = f"Error processing history file: {str(e)}"

        context['file'] = {'name': fname, 'url': url, 'kind': kind}
        return render(request, 'reports/home.html', context)
