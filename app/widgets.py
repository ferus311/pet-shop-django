from django.forms.widgets import MultiWidget, DateInput, TimeInput
from django import forms


class ImagePreviewWidget(forms.ClearableFileInput):
    template_name = 'app/widgets/image_preview_input.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['is_initial'] = False
        return context


class DateTimePickerWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time()]
        return [None, None]

    def format_output(self, rendered_widgets):
        return ''.join(rendered_widgets)
