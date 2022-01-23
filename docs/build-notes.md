



## Developing Locally

Start the postgresql service
```
sudo systemctl start postgresql.service
```

Export the Postgres database connection string to your env:
```
export DATABASE_URL="postgres://svc_django:The0mimosaWill4Everyone@127.0.0.1:5432/nmap"
export USE_DOCKER="no"
```

Test with Django that your postgres db is connecting successfully:
