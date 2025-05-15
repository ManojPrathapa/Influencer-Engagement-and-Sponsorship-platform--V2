# go to windows powershell and type : wsl
## then start the redis server :  sudo service redis-server start


## open terminal in vs code
## cd Code
### then : cd backend 
### create venv : python -m venv venv    and  activate the venv : .\venv\Scripts\activate
### do : pip install -r requirements.txt 
### and : pip install flask_bcrypt flask_mail flask_jwt_extended
### then : python app.py



## open new terminal in vscode : cd frontend
### then do : npm install
### then : npm run dev 
# run the application with the link there 

### Compile and Minify for Production

```sh
npm run build
```




#`celery -A app.celery worker --loglevel=info`
#`celery -A app.celery beat --loglevel=info`
#`celery -A app.celery worker --loglevel=info --pool=solo`
#`pytest --maxfail=1 --disable-warnings -q`