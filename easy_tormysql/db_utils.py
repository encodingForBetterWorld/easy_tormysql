import tormysql
from rel import ManyToOneRel

def init_mysql(**conn):
    global _pool_dict, _database_router
    _pool_dict = {}
    _database_router = {}
    for k, v in conn.iteritems():
        if k != "default":
            tables = v.pop("tables", [])
            _database_router[k] = tables
        _pool_dict[k] = tormysql.helpers.ConnectionPool(**v)


def get_db_connection_pool(cls_name):
    pool = _pool_dict.get("default")
    for k, v in _database_router.iteritems():
        if cls_name.lower() in v:
            pool = _pool_dict.get(k)
            break
    return pool


def get_where_sql(model_cls, sql_prefix, sql_param, plus_where, **where_case):
    db_table = model_cls.db_table
    if sql_prefix is None:
        select_sql = 'SELECT `%s`.* FROM `%s`' % (db_table, db_table)
    else:
        select_sql = sql_prefix
    if sql_param is None:
        select_param = []
    else:
        select_param = sql_param
    if where_case:
        if plus_where:
            select_sql += ' WHERE '
        else:
            select_sql += ' AND '
        count = len(where_case)
        for k, v in where_case.iteritems():
            t = None
            if '__' in k:
                idx = k.rfind('__')
                t = k[idx:]
                k = k[:idx]
            if isinstance(model_cls.fields.get(k, None), ManyToOneRel):
                k = k + '_id'
                if isinstance(v, (list, tuple)):
                    v = [o.id for o in v]
                else:
                    v = v.id
            if t == '__in':
                select_sql += '`%s`.`%s` IN (%s)' % (db_table, k, '%s,' * (len(v) - 1) + '%s')
                select_param.extend(v)
            elif t == '__between':
                select_sql += '`%s`.`%s` > ' % (db_table, k) + "%s AND " + '`%s`.`%s` < ' % (db_table, col) + "%s "
                select_param.extend(v)
            elif t == '__contains':
                select_sql += "`%s`.`%s` LIKE " % (db_table, k) + "\'%%" + str(v) + "%%\' "
            else:
                select_sql += '`%s`.`%s`' % (db_table, k)
                if v is None:
                    select_sql += 'IS NULL '
                else:
                    select_sql += '=%s '
                    select_param.append(v)
            count -= 1
            if count > 0:
                select_sql += 'AND '
    return select_sql, select_param




