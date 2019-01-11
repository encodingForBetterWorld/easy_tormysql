from tornado import gen


class Rel(object):
    pass


class ManyToOneRel(Rel):

    def __init__(self, rel_cls, rel_name, foreign_key):
        self.rel_cls = rel_cls
        self.rel_name = rel_name
        self.foreign_key = foreign_key


class OneToManyRel(Rel):

    def __init__(self, rel_cls, foreign_key, is_across_db):
        self.rel_cls = rel_cls
        self.foreign_key = foreign_key
        self.is_across_db = is_across_db
        db_table = rel_cls.db_table
        prefix = 'UPDATE `%s` SET `%s`.`%s`' % (db_table, db_table, foreign_key)
        suffix = 'WHERE `%s`.`id`=' % db_table + '%s'
        self.add_sql = prefix + '=%s ' + suffix
        self.remove_sql = prefix + '=NULL ' + suffix


class ManyToManyRel(Rel):

    def __init__(self, rel_cls, mt, trf, srf):
        self.rel_cls = rel_cls
        tt = rel_cls.db_table
        select_sql = 'SELECT `%s`.`id`' % tt
        for fk, fv in rel_cls.fields.iteritems():
            if isinstance(fv, ManyToOneRel):
                fk = fv.foreign_key
            select_sql += ',`%s`.`%s`' % (tt, fk)
        select_sql += ' FROM `%s` INNER JOIN `%s` ON (`%s`.`id`=`%s`.`%s_id`) WHERE `%s`.`%s_id`=' \
                   % (tt, mt, tt, mt, trf, mt, srf) + '%s'
        self.select_sql = select_sql

        self.add_sql = 'INSERT INTO `%s`(`%s_id`,`%s_id`) VALUES(' % (mt, srf, trf) + '%s,%s)'

        self.remove_sql = 'DELETE FROM `%s` WHERE `%s_id`=' % (mt, srf) + '%s AND ' + '`%s_id`=' % trf + '%s'

        self.check_sql = 'SELECT COUNT(*) FROM `%s` WHERE `%s_id`=' % (mt, srf) + '%s AND ' + '`%s_id`=' % trf + '%s'

    @gen.coroutine
    def is_related(self, sid, tid, tx):
        with (yield tx.execute(self.check_sql, [sid, tid])) as cursor:
            count = cursor.fetchall()[0][0]
            ret = count > 0
        raise gen.Return(ret)


def many2oneGetter(outter, outter_param):
    return getattr(outter, outter_param, None)


def many2oneSetter(outter, obj, outter_param, foreign_key):
    oid = None
    if obj is not None:
        oid = obj.id
    setattr(outter, foreign_key, oid)
    setattr(outter, outter_param, obj)