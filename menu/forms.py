from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(value, f"{'★' * value} ({value}/5)") for value in range(1, 6)],
        coerce=int,
    )

    class Meta:
        model = Review
        fields = ["body", "rating"]
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us about your meal"}
            )
        }

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 10:
            raise forms.ValidationError("Please write at least 10 characters.")
        return body

