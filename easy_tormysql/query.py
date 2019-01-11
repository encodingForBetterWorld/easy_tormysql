from tornado import gen
from db_utils import get_where_sql
from db_exceptions import ObjectDoesNotExist
from rel import ManyToOneRel, OneToManyRel, ManyToManyRel


class QuerySet(object):
    rel_id = None

    @gen.coroutine
    def filter(self):
        pass

    @gen.coroutine
    def all(self):
        pass

    @gen.coroutine
    def execute(self, tx):
        pass

    def add(self, val):
        pass

    def remove(self, val):
        pass


class OneToManySet(QuerySet):

    def __init__(self, outter, rel):
        if not isinstance(rel, OneToManyRel):
            raise TypeError('invalid relationship')
        self.outter = outter
        self.rel = rel
        self.rel_add_objs = set()
        self.add_rels = set()
        self.remove_rels = set()

    @gen.coroutine
    def filter(self, **kwargs):
        rid = self.outter.id
        rel = self.rel
        datas = None
        if rid is not None:
            datas = yield eval('rel.rel_cls.filter(%s=rid, **kwargs)' % rel.foreign_key)
        raise gen.Return(datas)

    @gen.coroutine
    def all(self):
        datas = yield self.filter()
        raise gen.Return(datas)

    def add(self, obj):
        rel = self.rel
        if not isinstance(obj, rel.rel_cls):
            raise TypeError('add fail')
        oid = obj.id
        if oid is None:
            self.rel_add_objs.add(obj)
        else:
            self.add_rels.add(oid)
        self.outter.rel_exec_set.add(self)

    def remove(self, obj):
        rel = self.rel
        if not isinstance(obj, rel.rel_cls):
            raise TypeError('remove fail')
        oid = obj.id
        if oid is not None:
            self.remove_rels.add(oid)
            self.outter.rel_exec_set.add(self)

    @gen.coroutine
    def execute(self, tx):
        rel = self.rel
        rel_cls = rel.rel_cls
        is_across = rel.is_across_db
        if is_across:
            tx = yield rel_cls.db_connection_pool.begin()
        db_manager = rel_cls.db_manager
        rid = self.outter.id
        for obj in self.rel_add_objs:
            sql_param = []
            for fk, fv in rel_cls.fields.iteritems():
                if isinstance(fv, ManyToOneRel):
                    fk = fv.foreign_key
                    if fk == self.rel.foreign_key:
                        v = rid
                    else:
                        v = getattr(obj, fk, None)
                else:
                    v = getattr(obj, fk, db_manager.get_insert_default_val(fk))
                sql_param.append(v)
            sql_str = db_manager.insert_sql
            yield obj.execute_tx(sql_str, sql_param, tx)
        self.rel_add_objs.clear()

        add_sql = rel.add_sql
        for oid in self.add_rels:
            try:
                yield tx.execute(add_sql, [rid, oid])
            except Exception as e:
                print e
                yield tx.rollback()
        self.add_rels.clear()

        remove_sql = rel.remove_sql
        for oid in self.remove_rels:
            try:
                yield tx.execute(remove_sql, [oid])
            except Exception as e:
                print e
                yield tx.rollback()
        self.remove_rels.clear()

        if is_across:
            yield tx.commit()


class ManyToManySet(QuerySet):

    def __init__(self, outter, rel):
        if not isinstance(rel, ManyToManyRel):
            raise TypeError('invalid relationship')
        self.outter = outter
        self.rel = rel
        self.remove_rels = set()
        self.update_rels = set()
        self.rel_add_objs = set()

    @gen.coroutine
    def filter(self, **kwargs):
        rid = self.outter.id
        rel = self.rel
        query_list = None
        if rid is not None:
            rel_cls = rel.rel_cls
            query_list = []
            pool = rel_cls.db_connection_pool
            select_sql, sql_param = get_where_sql(rel_cls, rel.select_sql, [rid], False, **kwargs)
            with (yield pool.execute(select_sql, sql_param)) as cursor:
                for data in cursor.fetchall():
                    ret = rel_cls()
                    ret.id = data[0]
                    for idx, field in enumerate(rel_cls.fields.iteritems()):
                        fk, fv = field
                        val = data[idx + 1]
                        if isinstance(fv, ManyToOneRel):
                            rel_obj = None
                            if val is not None:
                                try:
                                    rel_obj = yield fv.rel_cls.get(id=val)
                                except ObjectDoesNotExist:
                                    pass
                            setattr(ret, fv.rel_name, rel_obj)
                        else:
                            setattr(ret, fk, val)
                    query_list.append(ret)
        raise gen.Return(query_list)

    @gen.coroutine
    def all(self):
        datas = yield self.filter()
        raise gen.Return(datas)

    def add(self, obj):
        rel = self.rel
        if not isinstance(obj, rel.rel_cls):
            raise TypeError('add fail')
        rid = self.outter.id
        oid = obj.id
        if rid is not None:
            if oid is None:
                self.rel_add_objs.add(obj)
            else:
                self.update_rels.add((rid, oid))
            self.outter.rel_exec_set.add(self)

    def remove(self, obj):
        rel = self.rel
        if not isinstance(obj, rel.rel_cls):
            raise TypeError('remove fail')
        rid = self.outter.id
        oid = obj.id
        if None not in (rid, oid):
            self.remove_rels.add((rid, oid))
            self.outter.rel_exec_set.add(self)

    @gen.coroutine
    def execute(self, tx):
        rel = self.rel
        rid = self.outter.id
        db_manager = rel.rel_cls.db_manager
        for obj in self.rel_add_objs:
            sql_param = []
            for fk, fv in rel.rel_cls.fields.iteritems():
                if isinstance(fv, ManyToOneRel):
                    fk = fv.foreign_key
                v = getattr(obj, fk, db_manager.get_insert_default_val(fk))
                sql_param.append(v)
            sql_str = db_manager.insert_sql
            yield obj.execute_tx(sql_str, sql_param, tx)
            try:
                yield tx.execute(rel.add_sql, [rid, obj.id])
            except Exception as e:
                print e
                yield tx.rollback()
        self.rel_add_objs.clear()

        for rid, oid in self.update_rels:
            is_rel = yield rel.is_related(rid, oid, tx)
            if not is_rel:
                try:
                    yield tx.execute(rel.add_sql, [rid, oid])
                except Exception as e:
                    print e
                    yield tx.rollback()
        self.update_rels.clear()

        for rid, oid in self.remove_rels:
            is_rel = yield rel.is_related(rid, oid, tx)
            if is_rel:
                try:
                    yield tx.execute(rel.remove_sql, [rid, oid])
                except Exception as e:
                    print e
                    yield tx.rollback()
        self.remove_rels.clear()