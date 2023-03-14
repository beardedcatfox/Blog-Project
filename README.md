# hillel-Blog

## Basic blog project with registration/login/logout (CustomUser), post publications, post list, user posts, post editing, ability to comment posts, post's drafts. + Also, if user logged in, he comment posts from self name, if not - its field to enter name (all anonymous user get a name prefix "Guest")

## Basic functionality of admin panel with sorting, filters, mass actions + added ability to export Posts and Comments in CSV

## Notifications by celery + redis when user pubish post or creating new comment and for contact us form, also nofications to user about new comment to his posts

## To keep data use PostgreSQL + DigitalOcean Space S3

## Added management command "python manage.py users --users 2 --posts 5 --comments 3" --users - number of users to create, --posts - number of posts to each user (is-published=True), --comments - number of comments to each post (is_published=True)

## Contact us made by js script and available from each page

## Custom styles for pages