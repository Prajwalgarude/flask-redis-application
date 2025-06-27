# flask-redis-application
This is Flask-Redis TWO-TIER application.
which Displays --> Number of times you visited the page.
--------------------------------------------------------

U can deploy it with redis container or without redis also.
---
With Redis
--
podman run -dt --name redis-server redis/redis-stack-server:latest
---
Without Redis 
--
Directly Build The image and Run it using Your favourite container management tool.
--
Note: Before building the image Remove redis entry from requirements.txt
