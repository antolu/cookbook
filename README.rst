=====
Cookbook
=====

Cook is a Django app to store recipes, with a responsive web design.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'cookbook.apps.CokbookConfig',
    ]

2. Include the cookbook URLconf in your project urls.py like this::

    path('cookbook/', include('cookbook.urls'))

3. Run ``python manage.py migrate`` to create the cookbook models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create recipes, or upload them on the index page.

5. Visit http://127.0.0.1:8000/cookbook/ to view the recipes.