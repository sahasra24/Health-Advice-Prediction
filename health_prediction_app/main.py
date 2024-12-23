# import os
# import django

# # Set up Django settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
# django.setup()

from .models import Post

# Retrieve all Post objects
posts = Post.objects.all()

# Print attributes of each Post object
for post in posts:
    print(post.attribute_1, post.attribute_2)