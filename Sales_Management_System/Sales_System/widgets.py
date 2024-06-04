from django.forms.widgets import ClearableFileInput

class CustomClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': True})
        super().__init__(attrs)
