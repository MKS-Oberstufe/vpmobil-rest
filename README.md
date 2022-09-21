**This project is in no way associated with Stundenplan24, VPMobil or Freistaat Sachsen**

## What is this?
This is a REST-ful HTTP API for [stundenplan24](www.stundenplan24.de/) because parsing xml is a thing of the past and REST is what people should be using  
This is built in python using FastAPI.

## Why?
Stundenplan24 has no native JSON API, only their raw `.xml` files.  
this leads to a lot of problems for anyone trying to develop something with their site.  

First, a lot of methods are missing natively (e.g. searching for classes, teachers, etc.) since all of the classes are in a single xml file.  
This API tries to provide the missing functions and features by returning scraped results.  
That makes it a lot easier to develop applications that want to use stundenplan24.

## Authentification
Authentification is supplied via BasicAuth just like on stundenplan24.

## Deployment
You can deploy this for yourself with uvicorn. Or put your instance on Heroku etc.
example deployment for development  
```
uvicorn app.server:app --port 80 --host 0.0.0.0 --reload
```

## Documentation?
Documentation is supplied as per FastAPI on the `/docs` route  


## How to?
If you didn't read the docs or just want an example:   
```
curl -X 'GET' 'http://127.0.0.1/school/12345678/class/05-4' -H 'accept: application/json' -H 'Authorization: Basic {YOUR AUTH HEADER HERE}'; echo;
```

## TO-DO
- [ ] Allow getting the plan for different timestamps
- [ ] Add a route to get a teacher's plan
- [ ] Add testing
- [ ] Don't make a new ClientSession on every request