from django import forms

class CategoryForm(forms.Form):
    hashtags = forms.CharField(widget=forms.Textarea)
