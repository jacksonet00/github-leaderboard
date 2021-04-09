from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Submit
from django import forms

from github_leaderboard.app.models import Leaderboard


class CreateLeaderboardForm(forms.ModelForm):
    class Meta:
        model = Leaderboard
        fields = ("name", "repo_url", "end", "start")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column("name", css_class="form-group col-md-6 mb-0"),
            Column("repo_url", css_class="form-group col-md-6 mb-0"),
            Column("end", css_class="form-group col-md-6 mb-0"),
            Column("start", css_class="form-group col-md-6 mb-0"),
        )
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Create Leaderboard"))
