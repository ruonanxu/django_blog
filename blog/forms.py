from django import forms


class BlogForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        min_length=5,
        error_messages={
        'min_length': '输入最小长度不能小于5',
        'max_length':'输入最大长度不能大于200'
        },
        required=True,
        label= '标题')
    content = forms.CharField(
        max_length=200,
        error_messages={
        'max_length':'输入最大长度不能大于200'
        })
    category = forms.IntegerField()


class CommentForm(forms.Form):
    comment = forms.CharField(
        max_length=200,
        min_length=0,
        error_messages={
        'min_length': '输入最小长度不能小于0',
        'max_length':'输入最大长度不能大于200'
        },
        required=True,
        label= '评论')
    # blog = forms.IntegerField()
