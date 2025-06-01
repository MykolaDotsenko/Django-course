from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'status', 'categories']
    def clean(self):
        text = self.cleaned_data["text"]   
        title = self.cleaned_data["title"]
        if text.startswith(title):
            raise forms.ValidationError("Text must not start with title")
        return self.cleaned_data

class SearchForm(forms.Form):
    query = forms.CharField(required=False, label="Пошук", widget=forms.TextInput(attrs={"class": "form_control"}) ,help_text="Введіть запит для пошуку", error_messages={"required": "Поле обов'язкове в 3 символи"})
    def clean_query(self):
        query = self.cleaned_data["query"]
        if len(query)<3:
            raise forms.ValidationError("Field must be at least 3 characters long")
        return query

