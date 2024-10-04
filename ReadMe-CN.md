# Argon-Django
这是<a href="https://github.com/solstice23/argon-theme">Argon-Theme</a>主题的Django重构版，主要界面参考<a href="https://www.liveout.cn/">Echo的博客</a>。

## 使用说明
1. 安装依赖库
```pip
pip install -r requirements.txt
```

2. 数据迁移
```cmd
python manage.py makemigrations
```
```cmd
python manage.py migrate
```

3. 构建索引
```cmd
python manage.py rebuild_index 
```

4. 最后启动
```cmd
python manage.py runserver
```

访问**127.0.0.1:8000/argon**即可。

## LICENSE
GPL-3
