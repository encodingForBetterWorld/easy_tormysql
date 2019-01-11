class Field(object):
    def __init__(self, **kwargs):
        self.default = kwargs.get('default', None)
        self.auto_now_add = kwargs.get('auto_now_add', None)
        self.auto_now = kwargs.get('auto_now', None)


class RelatedField(object):
    one2one = None
    one2many = None
    many2one = None
    many2many = None

    def __init__(self, to, foreign_key=None, middle_table=None, target_rel_field=None, src_rel_field=None):
        self.to = to
        self.foreign_key = foreign_key
        self.middle_table = middle_table
        self.target_rel_field = target_rel_field
        self.src_rel_field = src_rel_field


class OneToOneField(RelatedField):
    one2one = True

    def __init__(self, to, foreign_key=None):
        super(OneToOneField, self).__init__(to=to, foreign_key=foreign_key)


class OneToManyField(RelatedField):
    one2many = True

    def __init__(self, to, foreign_key=None):
        super(OneToManyField, self).__init__(to=to, foreign_key=foreign_key)


class ManyToOneField(RelatedField):
    many2one = True

    def __init__(self, to, foreign_key=None):
        super(ManyToOneField, self).__init__(to=to, foreign_key=foreign_key)


class ManyToManyField(RelatedField):
    many2many = True

    def __init__(self, to, middle_table, target_rel_field=None, src_rel_field=None):
        super(ManyToManyField, self).__init__(to=to, middle_table=middle_table, target_rel_field=target_rel_field, src_rel_field=src_rel_field)


class ForeignKey(ManyToOneField):
    pass