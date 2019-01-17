* ### About
This module provides a twice encapsulation of [TorMySql](https://pypi.org/project/TorMySQL/) based on [Django](https://pypi.org/project/Django/)'s code style.

Support [tornado](https://pypi.org/project/tornado/) and asyncio.
* ### Installation
python2  
`pip install easy_tormysql==0.1.1`  

python3  
`pip install easy_tormysql>=0.2.1`  

* ### Tutorial

#### init pool
```
from easy_tormysql import init_mysql
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
from easy_tormysql import BaseModel, Field

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
from easy_tormysql import BaseModel, Field, ForeignKey, ManyToManyField

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
#### use tornado
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

# order by
sorted_authors = yield Author.all(order_fields=("name",))

# group by
records = yield Author.filter(name='Wang', group_fields=("name",))

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
* in RequestHandler
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
#### use asyncio
* insert
```
# single
author = Author(name='Wang')

# one-to-many
article = Article(content='My story...')
author.article_set.add(article)
await author.save()

# many-to-many
tag1, tag2 = Tag(name='poetry'), Tag(name='biography')
await tag1.save()
await tag2.save()
article.tags.add(tag1)
article.tags.add(tag2)
await article.save()
```
* query
```
# query unique record
author = await Author.get(name='Wang')

# query all record
articles = await Article.all()

# query
authors = await Author.filter(name='Wang')
authors = await Author.filter(name__in=('Wang','Lee'))
authors = await Author.filter(name__contains='W')
articles = await Author.filter(create_time__between=(date1,date2))

# order by
sorted_authors = await Author.all(order_fields=("name",))

# group by
records = await Author.filter(name='Wang', group_fields=("name",))

# one-to-many
articles = await author.article_set.all()

# many-to-many
tags = await article.tags.all()
articles = await tag1.articles.all()
```
* update
```
article.content = "programming..."
await article.save()
```
* delete
```
article.tags.remove(tag1)
article.tags.remove(tag2)
await article.save()
await article.delete()
```
* in async function
```
import asyncio
async def example():
    ...
    # single
    author = Author(name='Wang')
    
    # one-to-many
    article = Article(content='My story...')
    author.article_set.add(article)
    await author.save()
    ...
       
ioloop = asyncio.events.get_event_loop()
ioloop.run_until_complete(example())
```