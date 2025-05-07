from app.models import Tag, Profile

def popular_tags_and_users(request):
    popular_tags = Tag.objects.popular()
    top_users = Profile.objects.top_users()
    return {
        'popular_tags': popular_tags,
        'top_users': top_users,
    }