# django-newspaper-slug

Django Slug Tutorial

In this tutorial we will add slugs to a Django website. As noted in the official docs: "Slug is a newspaper term. A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs."

To give a concrete example, assume you had a Newspaper website (such as we'll build in this tutorial). For a story titled "Hello World," the URL would be example.com/hello-world assuming the site was called example.com.

Despite their ubiquity, slugs can be somewhat challenging to implement the first time around, at least in my experience. Therefore we will implement everything from scratch so you can see how the pieces all fit together. If you are already comfortable implementing ListView and DetailView you can jump right to the Slug section.

Set Up
To start let's navigate into a directory for our code. This can be hosted anywhere on your computer but if you're on a Mac, an easy-to-find location is the Desktop.

$ cd ~/Desktop
$ mkdir newspaper && cd newspaper
To pay homage to Django's origin at a newspaper, we'll create a basic Newspaper website with Articles. If you need help installing Python, Django, and all the rest (see here for in-depth instructions).

On your command line, enter the following commands to install the latest version with Pipenv, create a project called config, set up the initial database via migrate, and then start the local web server with runserver.

$ pipenv install django~=3.1.0
$ pipenv shell
(newspaper) $ django-admin startproject config .
(newspaper) $ python manage.py migrate
(newspaper) $ python manage.py runserver
Don't forget to include that period . at the end of the startproject command! It is an optional step that avoid Django creating an additional directory otherwise.

Navigate to http://127.0.0.1:8000/ in your web browser to see the Django welcome page which confirms everything is configured properly.

Django welcome page

Articles app
Since the focus of this tutorial is on slugs I'm going to simply give the commands and code to wire up this Articles app. Full explanations can be found in my book Django for Beginners!

Let's start by creating an app called articles. Stop the local server with Control+c and use the startapp command to create this new app.

(newspaper) $ python manage.py startapp articles
Then update INSTALLED_APPS within our config/settings.py file to notify Django about the app.

# config/settings.py
INSTALLED_APPS = [
    ...
    'articles', # new
]
Article Model
Create the database model which will have a title and body. We'll also set __str__ and a get_absolute_url which are Django best practices.

# articles/models.py
from django.db import models
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])
Now create a migrations file for this change, then add it to our database via migrate.

(newspaper) $ python manage.py makemigrations articles
(newspaper) $ python manage.py migrate
Django Admin
The Django admin is a convenient way to play around with models so we'll use it. But first, create a superuser account.

(newspaper) $ python manage.py createsuperuser
And then update articles/admin.py to display our app within the admin.

# articles/admin.py
from django.contrib import admin

from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'body',)

admin.site.register(Article, ArticleAdmin)
Start up the server again with python manage.py runserver and navigate to the admin at http://127.0.0.1:8000/admin. Log in with your superuser account.

Admin Homepage

Click on the "+ Add" next to the Articles section and add an entry.

Admin Article

URLs
In addition to a model we'll eventually need a URL, view, and template to display an Article page. I like to move to URLs next after models although the order doesn't matter: we need all four before we can display a single page. The first step is to add the articles app to our project-level config/urls.py file.

# config/urls.py
from django.contrib import admin
from django.urls import path, include # new

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('articles.urls')), # new
]
Next we must create the app-level urls.py file.

$ touch articles/urls.py
We'll have a ListView to list all articles and a DetailView for individual articles.

Note that we're referencing two views that have yet to be created: ArticleListView and ArticleDetailView. We'll add them in the next section.

# articles/urls.py
from django.urls import path

from .views import ArticleListView, ArticleDetailView

urlpatterns = [
    path('<int:pk>', ArticleDetailView.as_view(), name='article_detail'),
    path('', ArticleListView.as_view(), name='article_list'),
]
Views
For each view we specify the related model and appropriate not-yet-created template.

# articles/views.py
from django.views.generic import ListView, DetailView

from .models import Article

class ArticleListView(ListView):
    model = Article
    template_name = 'article_list.html'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'
Templates
Finally, we come to the last step: templates. By default Django will look within each app for a templates directory. That structure in our case would be articles/templates/template.html.

Type Control+c on the command line and create the new templates directory.

(newspaper) $ mkdir articles/templates
Now add the two new templates.

(newspaper) $ touch articles/templates/article_list.html
(newspaper) $ touch articles/templates/article_detail.html
For our list page we loop over object_list which is provided by ListView. And we add an a href by using the get_absolute_url method added to the model.

<!-- article_list.html -->
<h1>Articles</h1>
{% for article in object_list %}
  <ul>
    <li><a href="{{ article.get_absolute_url }}">{{ article.title }}</a></li>
  </ul>
{% endfor %}
The detail view outputs our two fields--title and body--using the object default provided by DetailView. You can, and probably should, rename both object_list in the ListView and object in the DetailView to be more descriptive.

<!-- article_detail.html -->
<div>
  <h2>{{ object.title }</h2>
  <p>{{ object.body }}</p>
</div>
Make sure the server is running--python manage.py runserver--and check out both our pages in your web browser.

The list of all articles is available at http://127.0.0.1:8000/.

ListView

And the detail view for our single article is at http://127.0.0.1:8000/1.

DetailView

Slugs
Finally we come to slugs. Ultimately we want our article title to be reflected in the URL. In other words, "A Day in the Life" should have the URL of http://127.0.0.1:8000/a-day-in-the-life.

There are only two steps required: updating our articles/models.py file and articles/urls.py. Ready? Let's go...

In our model, we can add Django's built-in SlugField. But we must also--and this is the part that typically trips people up--update get_absolute_url as well. That's where we pass in the value used in our URL. Currently it passes in the id for the article an args, so 1 for our first article. We need to change that over to a keyword argument, kwargs, for our slug.

# articles/models.py
from django.db import models
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField() # new

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug}) # new
Moving along let's add a migration file since we've updated our model.

(newspaper) $ python manage.py makemigrations articles
You are trying to add a non-nullable field 'slug' to article without a default; we can't do that (the database needs something to populate existing rows).
Please select a fix:
 1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
 2) Quit, and let me add a default in models.py
Ack! What is this?! It turns out we already have data in our database, our single Article, so we can't just willy-nilly add a new field on. Django is helpfully telling us that we either need to a one-off default of null or add it ourself. Hmmm.

For this very reason, it is generally good advice to always add new fields with either null=True or with a default value.

Let's take the easy approach of setting null=True for now. So type 2 on the command line. Then add this to our slug field.

# articles/models.py
from django.db import models
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(null=True) # new

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
Try to create a migrations file again and it will work.

(newspaper) $ python manage.py makemigrations articles
Go ahead and migrate the database as well to apply the change.

(newspaper) $ python manage.py migrate
But if you think about it, what we've done is create a null value for our slug. We have to go into the admin to set it properly. Start up the local server, python manage.py runserver, and go to the Article page in the Admin. The Slug field is empty.

Empty Slug

Manually add in our desired value a-day-in-the-life and click "Save."

Add Slug

Ok, last step is to update articles/urls.py so that we display the slug keyword argument in the URL itself. Luckily that just means swapping out <int:pk> for <slug:slug>.

# articles/urls.py
from django.urls import path

from .views import ArticleListView, ArticleDetailView

urlpatterns = [
    path('<slug:slug>', ArticleDetailView.as_view(), name='article_detail'), # new
    path('', ArticleListView.as_view(), name='article_list'),
]
And we're done! Go to the list view page at http://127.0.0.1:8000/ and click on the link for our article.

Slug URL

And there it is with our slug as the URL! Beautiful.

Unique and Null
Moving forward, do we really want to allow a null value for a slug? Probably not as it will break our site! Another consideration is: what happens if there are identical slugs? How will that resolve itself? The short answer is: not well.

Therefore let's change our slug field so that null is not allowed and unique values are required.

# articles/models.py
from django.db import models
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(null=False, unique=True) # new

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
Make migration/migrate. Need empty for past entry.

(newspaper) $ python manage.py makemigrations articles
You are trying to change the nullable field 'slug' on article to non-nullable without a default; we can't do that (the database needs something to populate existing rows).
Please select a fix:
 1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
 2) Ignore for now, and let me handle existing rows with NULL myself (e.g. because you added a RunPython or RunSQL operation to handle NULL values in a previous data migration)
 3) Quit, and let me add a default in models.py
Select an option:
Select 2 since we can manually handle the existing row ourself, and in fact, already have. Then migrate the database.

(newspaper) $ python manage.py migrate
PrePopulated Fields
Manually adding a slug field each time quickly becomes tedious. So we can use a prepopulated_field in the admin to automate the process for us.

Update articles/admin.py as follows:

# articles/admin.py
from django.contrib import admin

from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'body',)
    prepopulated_fields = {'slug': ('title',)} # new

admin.site.register(Article, ArticleAdmin)
Now head over to the admin and add a new article. You'll note that as you type in the Title field, the Slug field is automatically populated. Pretty neat!

Signals, Lifecycle Hooks, Save, and Forms/Serializers
In the real world, it's unlikely to simply provide admin access to a user. You could, but at scale it's definitely not a good idea. And even on a small scale, most non-technical users will find a web interface more appealing.

So...how to auto-populate the slug field when creating a new Article. It turns out Django has a built-in tool for this called slugify!

But how to use slugify? In practice, it's common to see this done with a Signal. But I would argue--as would Django Fellow Carlton Gibson--that this is not a good use of signals because we know both the sender and receiver here. There's no mystery. We discuss the proper use of signals at length in our Django Chat Podcast episode on the topic.

An alternative to signals is to use a lifecycle hook via something like the django-lifecycle package. Lifecycle hooks are an alternative to Signals that provide similar functionality with less indirection.

Another common way to see this implemented is by overriding the Article model's save method. This also "works" but is not the best solution. Here is one way to do that.

# articles/models.py
from django.db import models
from django.template.defaultfilters import slugify # new
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
The best solution, in my opinion, is to create the slug in the form itself. This can be done by overriding the form's clean method so that cleaned_data has the slug, or JavaScript can be used to auto-populate the field as is done in the Django admin itself. If you're using an API, the same approach can be applied to the serializer.

