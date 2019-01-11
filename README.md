* ### About
This module provides a twice encapsulation of [TorMySql](https://pypi.org/project/TorMySQL/) based on [Django](https://pypi.org/project/Django/)'s code style.

Support [tornado](https://pypi.org/project/tornado/).
* ### Installation
`pip install easy_tormysql`

* ### Tutorial

#### init pool
```
from easy_tormysql.models import init_mysql
init_mysql(
    default={
        "max_connections" : 20, #max open connections
        "idle_seconds" : 7200, #conntion idle timeout time, 0 is not timeout
        "wait_connection_timeout" : 3, #wait connection timeout
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "root",
        "charset": "utf8",
        "db": "example1"
    },
    other_connection={
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "root",
        "charset": "utf8",
        "db": "example2",
        """
            treat all tables contain in default database(example1) automatically.
            you must define(use table-mapping class's lowercase name, not table's name) which tables contain in current database(example2) instead of default database.
        """
        "tables": [
            "example_table_mapping_class_lowercase_name"
        ]
    }
)
```
#### define models
* single
```
from easy_tormysql.models import BaseModel, Field

class Subscriber(BaseModel):
    """
        table-mapping class(User) map to table tb_user.
        if undefine db_table,map to table user(class's lowercase name)
    """
    db_table = 'tb_user'
    name = Field()
    
    #   auto_now_add: whether current colum set with now time when insert data.
    create_time = Field(auto_now_add=True)
    
    #   auto_now_add: whether current colum set with now time when insert data.
    login_time = Field(auto_now=True) #auto_now: whether current colum set with now time when update data.
```
* relationship
```
from easy_tormysql.models import BaseModel, Field, ForeignKey, ManyToManyField

class Author(BaseModel):
    name = Field()

class Tag(BaseModel):
    name = Field()

class Article(BaseModel):
    content = Field()
    create_time = Field()
    
    # many-to-one relationship
    author = ForeignKey(Author)
    
    # many-to-many relationship: must define the middle table's name
    tags = ManyToManyField(Tag, middle_table='article_tags')
```
#### sql function
* insert
```
# single
author = Author(name='Wang')

# one-to-many
article = Article(content='My story...')
author.article_set.add(article)
yield author.save()

# many-to-many
tag1, tag2 = Tag(name='poetry'), Tag(name='biography')
yield tag1.save()
yield tag2.save()
article.tags.add(tag1)
article.tags.add(tag2)
yield article.save()
```
* query
```
# query unique record
author = yield Author.get(name='Wang')

# query all record
articles = yield Article.all()

# query
authors = yield Author.filter(name='Wang')
authors = yield Author.filter(name__in=('Wang','Lee'))
authors = yield Author.filter(name__contains='W')
articles = yield Author.filter(create_time__between=(date1,date2))

# one-to-many
articles = yield author.article_set.all()

# many-to-many
tags = yield article.tags.all()
articles = yield tag1.articles.all()
```
* update
```
article.content = "programming..."
yield article.save()
```
* delete
```
article.tags.remove(tag1)
article.tags.remove(tag2)
yield article.save()
yield article.delete()
```

#### use tornado
```
from tornado.web import RequestHandler
from tornado.gen import coroutine


class ExampleHandler(RequestHandler):

    @coroutine
    def get(self):
        ...
        # single
        author = Author(name='Wang')
        
        # one-to-many
        article = Article(content='My story...')
        author.article_set.add(article)
        yield author.save()
        ...
```
