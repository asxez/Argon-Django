# Argon-Django
<a href="./ReadMe-CN.md">中文文档</a>

This is a Django refactoring of the <a href="https://github.com/solstice23/argon-theme">Argon-Theme</a> theme, with the main interface referenced to <a href="https://www.liveout.cn/">Echo's blog</a>.
## Use
1. Install dependencies
```pip
pip install -r requirements.txt
```

2. Data Migration
```cmd
python manage.py makemigrations
```
```cmd
python manage.py migrate
```

3. Now you should build index for your posts.
```cmd
python manage.py rebuild_index 
```

4. Then:
```cmd
python manage.py runserver 
```
Request **127.0.0.1:8000/argon**.

## LICENSE
GPL-3
