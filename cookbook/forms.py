from django import forms


class UploadRecipeForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
