from sqlalchemy.orm import create_session, relationship, mapper, \
    contains_eager, joinedload, subqueryload, subqueryload_all,\
    Session, aliased

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.engine import default

from test.lib import AssertsCompiledSQL, fixtures, testing
from test.lib.schema import Table, Column
from test.lib.testing import assert_raises, eq_

class Company(fixtures.ComparableEntity):
    pass
class Person(fixtures.ComparableEntity):
    pass
class Engineer(Person):
    pass
class Manager(Person):
    pass
class Boss(Manager):
    pass
class Machine(fixtures.ComparableEntity):
    pass
class Paperwork(fixtures.ComparableEntity):
    pass

class SelfReferentialTestJoinedToBase(fixtures.MappedTest):

    run_setup_mappers = 'once'

    @classmethod
    def define_tables(cls, metadata):
        Table('people', metadata,
            Column('person_id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('name', String(50)),
            Column('type', String(30)))

        Table('engineers', metadata,
            Column('person_id', Integer,
                ForeignKey('people.person_id'),
                primary_key=True),
            Column('primary_language', String(50)),
            Column('reports_to_id', Integer,
                ForeignKey('people.person_id')))

    @classmethod
    def setup_mappers(cls):
        engineers, people = cls.tables.engineers, cls.tables.people

        mapper(Person, people,
            polymorphic_on=people.c.type,
            polymorphic_identity='person')

        mapper(Engineer, engineers,
            inherits=Person,
            inherit_condition=engineers.c.person_id == people.c.person_id,
            polymorphic_identity='engineer',
            properties={
                'reports_to':relationship(
                    Person,
                    primaryjoin=
                        people.c.person_id == engineers.c.reports_to_id)})

    def test_has(self):
        p1 = Person(name='dogbert')
        e1 = Engineer(name='dilbert', primary_language='java', reports_to=p1)
        sess = create_session()
        sess.add(p1)
        sess.add(e1)
        sess.flush()
        sess.expunge_all()
        eq_(sess.query(Engineer)
                .filter(Engineer.reports_to.has(Person.name == 'dogbert'))
                .first(),
            Engineer(name='dilbert'))

    def test_oftype_aliases_in_exists(self):
        e1 = Engineer(name='dilbert', primary_language='java')
        e2 = Engineer(name='wally', primary_language='c++', reports_to=e1)
        sess = create_session()
        sess.add_all([e1, e2])
        sess.flush()
        eq_(sess.query(Engineer)
                .filter(Engineer.reports_to
                    .of_type(Engineer)
                    .has(Engineer.name == 'dilbert'))
                .first(),
            e2)

    def test_join(self):
        p1 = Person(name='dogbert')
        e1 = Engineer(name='dilbert', primary_language='java', reports_to=p1)
        sess = create_session()
        sess.add(p1)
        sess.add(e1)
        sess.flush()
        sess.expunge_all()
        eq_(sess.query(Engineer)
                .join('reports_to', aliased=True)
                .filter(Person.name == 'dogbert').first(),
            Engineer(name='dilbert'))

class SelfReferentialJ2JTest(fixtures.MappedTest):

    run_setup_mappers = 'once'

    @classmethod
    def define_tables(cls, metadata):
        people = Table('people', metadata,
            Column('person_id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('name', String(50)),
            Column('type', String(30)))

        engineers = Table('engineers', metadata,
            Column('person_id', Integer,
                ForeignKey('people.person_id'),
                primary_key=True),
            Column('primary_language', String(50)),
            Column('reports_to_id', Integer,
                ForeignKey('managers.person_id'))
          )

        managers = Table('managers', metadata,
            Column('person_id', Integer, ForeignKey('people.person_id'),
                primary_key=True),
        )

    @classmethod
    def setup_mappers(cls):
        engineers = cls.tables.engineers
        managers = cls.tables.managers
        people = cls.tables.people

        mapper(Person, people,
            polymorphic_on=people.c.type,
            polymorphic_identity='person')

        mapper(Manager, managers,
            inherits=Person,
            polymorphic_identity='manager')

        mapper(Engineer, engineers,
            inherits=Person,
            polymorphic_identity='engineer',
            properties={
                'reports_to':relationship(
                    Manager,
                    primaryjoin=
                        managers.c.person_id == engineers.c.reports_to_id,
                    backref='engineers')})

    def test_has(self):
        m1 = Manager(name='dogbert')
        e1 = Engineer(name='dilbert', primary_language='java', reports_to=m1)
        sess = create_session()
        sess.add(m1)
        sess.add(e1)
        sess.flush()
        sess.expunge_all()

        eq_(sess.query(Engineer)
                .filter(Engineer.reports_to.has(Manager.name == 'dogbert'))
                .first(),
            Engineer(name='dilbert'))

    def test_join(self):
        m1 = Manager(name='dogbert')
        e1 = Engineer(name='dilbert', primary_language='java', reports_to=m1)
        sess = create_session()
        sess.add(m1)
        sess.add(e1)
        sess.flush()
        sess.expunge_all()

        eq_(sess.query(Engineer)
                .join('reports_to', aliased=True)
                .filter(Manager.name == 'dogbert').first(),
            Engineer(name='dilbert'))

    def test_filter_aliasing(self):
        m1 = Manager(name='dogbert')
        m2 = Manager(name='foo')
        e1 = Engineer(name='wally', primary_language='java', reports_to=m1)
        e2 = Engineer(name='dilbert', primary_language='c++', reports_to=m2)
        e3 = Engineer(name='etc', primary_language='c++')

        sess = create_session()
        sess.add_all([m1, m2, e1, e2, e3])
        sess.flush()
        sess.expunge_all()

        # filter aliasing applied to Engineer doesn't whack Manager
        eq_(sess.query(Manager)
                .join(Manager.engineers)
                .filter(Manager.name == 'dogbert').all(),
            [m1])

        eq_(sess.query(Manager)
                .join(Manager.engineers)
                .filter(Engineer.name == 'dilbert').all(),
            [m2])

        eq_(sess.query(Manager, Engineer)
                .join(Manager.engineers)
                .order_by(Manager.name.desc()).all(),
            [(m2, e2), (m1, e1)])

    def test_relationship_compare(self):
        m1 = Manager(name='dogbert')
        m2 = Manager(name='foo')
        e1 = Engineer(name='dilbert', primary_language='java', reports_to=m1)
        e2 = Engineer(name='wally', primary_language='c++', reports_to=m2)
        e3 = Engineer(name='etc', primary_language='c++')

        sess = create_session()
        sess.add(m1)
        sess.add(m2)
        sess.add(e1)
        sess.add(e2)
        sess.add(e3)
        sess.flush()
        sess.expunge_all()

        eq_(sess.query(Manager)
                .join(Manager.engineers)
                .filter(Engineer.reports_to == None).all(),
            [])

        eq_(sess.query(Manager)
                .join(Manager.engineers)
                .filter(Engineer.reports_to == m1).all(),
            [m1])

class SelfReferentialJ2JSelfTest(fixtures.MappedTest):

    run_setup_mappers = 'once'

    @classmethod
    def define_tables(cls, metadata):
        people = Table('people', metadata,
            Column('person_id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('name', String(50)),
            Column('type', String(30)))

        engineers = Table('engineers', metadata,
            Column('person_id', Integer,
                ForeignKey('people.person_id'),
                primary_key=True),
            Column('reports_to_id', Integer,
                ForeignKey('engineers.person_id')))

    @classmethod
    def setup_mappers(cls):
        engineers = cls.tables.engineers
        people = cls.tables.people

        mapper(Person, people,
            polymorphic_on=people.c.type,
            polymorphic_identity='person')

        mapper(Engineer, engineers,
            inherits=Person,
            polymorphic_identity='engineer',
            properties={
                'reports_to':relationship(
                    Engineer,
                    primaryjoin=
                        engineers.c.person_id == engineers.c.reports_to_id,
                    backref='engineers',
                    remote_side=engineers.c.person_id)})

    def _two_obj_fixture(self):
        e1 = Engineer(name='wally')
        e2 = Engineer(name='dilbert', reports_to=e1)
        sess = Session()
        sess.add_all([e1, e2])
        sess.commit()
        return sess

    def _five_obj_fixture(self):
        sess = Session()
        e1, e2, e3, e4, e5 = [
            Engineer(name='e%d' % (i + 1)) for i in xrange(5)
        ]
        e3.reports_to = e1
        e4.reports_to = e2
        sess.add_all([e1, e2, e3, e4, e5])
        sess.commit()
        return sess

    def test_has(self):
        sess = self._two_obj_fixture()
        eq_(sess.query(Engineer)
                .filter(Engineer.reports_to.has(Engineer.name == 'wally'))
                .first(),
            Engineer(name='dilbert'))

    def test_join_explicit_alias(self):
        sess = self._five_obj_fixture()
        ea = aliased(Engineer)
        eq_(sess.query(Engineer)
                .join(ea, Engineer.engineers)
                .filter(Engineer.name == 'e1').all(),
            [Engineer(name='e1')])

    def test_join_aliased_flag_one(self):
        sess = self._two_obj_fixture()
        eq_(sess.query(Engineer)
                .join('reports_to', aliased=True)
                .filter(Engineer.name == 'wally').first(),
            Engineer(name='dilbert'))

    def test_join_aliased_flag_two(self):
        sess = self._five_obj_fixture()
        eq_(sess.query(Engineer)
                .join(Engineer.engineers, aliased=True)
                .filter(Engineer.name == 'e4').all(),
            [Engineer(name='e2')])

    def test_relationship_compare(self):
        sess = self._five_obj_fixture()
        e1 = sess.query(Engineer).filter_by(name='e1').one()

        eq_(sess.query(Engineer)
                .join(Engineer.engineers, aliased=True)
                .filter(Engineer.reports_to == None).all(),
            [])

        eq_(sess.query(Engineer)
                .join(Engineer.engineers, aliased=True)
                .filter(Engineer.reports_to == e1).all(),
            [e1])

class M2MFilterTest(fixtures.MappedTest):

    run_setup_mappers = 'once'
    run_inserts = 'once'
    run_deletes = None

    @classmethod
    def define_tables(cls, metadata):
        organizations = Table('organizations', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('name', String(50)))

        engineers_to_org = Table('engineers_to_org', metadata,
            Column('org_id', Integer,
                ForeignKey('organizations.id')),
            Column('engineer_id', Integer,
                ForeignKey('engineers.person_id')))

        people = Table('people', metadata,
            Column('person_id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('name', String(50)),
            Column('type', String(30)))

        engineers = Table('engineers', metadata,
            Column('person_id', Integer,
                ForeignKey('people.person_id'),
                primary_key=True),
            Column('primary_language', String(50)))

    @classmethod
    def setup_mappers(cls):
        organizations = cls.tables.organizations
        people = cls.tables.people
        engineers = cls.tables.engineers
        engineers_to_org = cls.tables.engineers_to_org

        class Organization(cls.Comparable):
            pass

        mapper(Organization, organizations,
            properties={
                'engineers':relationship(
                    Engineer,
                    secondary=engineers_to_org,
                    backref='organizations')})

        mapper(Person, people,
            polymorphic_on=people.c.type,
            polymorphic_identity='person')

        mapper(Engineer, engineers,
            inherits=Person,
            polymorphic_identity='engineer')

    @classmethod
    def insert_data(cls):
        Organization = cls.classes.Organization
        e1 = Engineer(name='e1')
        e2 = Engineer(name='e2')
        e3 = Engineer(name='e3')
        e4 = Engineer(name='e4')
        org1 = Organization(name='org1', engineers=[e1, e2])
        org2 = Organization(name='org2', engineers=[e3, e4])
        sess = create_session()
        sess.add(org1)
        sess.add(org2)
        sess.flush()

    def test_not_contains(self):
        Organization = self.classes.Organization
        sess = create_session()
        e1 = sess.query(Person).filter(Engineer.name == 'e1').one()

        # this works
        eq_(sess.query(Organization)
                .filter(~Organization.engineers
                    .of_type(Engineer)
                    .contains(e1))
                .all(),
            [Organization(name='org2')])

        # this had a bug
        eq_(sess.query(Organization)
                .filter(~Organization.engineers
                    .contains(e1))
                 .all(),
            [Organization(name='org2')])

    def test_any(self):
        sess = create_session()
        Organization = self.classes.Organization

        eq_(sess.query(Organization)
                .filter(Organization.engineers
                    .of_type(Engineer)
                    .any(Engineer.name == 'e1'))
                .all(),
            [Organization(name='org1')])

        eq_(sess.query(Organization)
                .filter(Organization.engineers
                    .any(Engineer.name == 'e1'))
                .all(),
            [Organization(name='org1')])

class SelfReferentialM2MTest(fixtures.MappedTest, AssertsCompiledSQL):

    @classmethod
    def define_tables(cls, metadata):
        Table('secondary', metadata,
            Column('left_id', Integer,
                ForeignKey('parent.id'),
                nullable=False),
            Column('right_id', Integer,
                ForeignKey('parent.id'),
                nullable=False))

        Table('parent', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('cls', String(50)))

        Table('child1', metadata,
            Column('id', Integer,
                ForeignKey('parent.id'),
                primary_key=True))

        Table('child2', metadata,
            Column('id', Integer,
                ForeignKey('parent.id'),
                primary_key=True))

    @classmethod
    def setup_classes(cls):
        class Parent(cls.Basic):
            pass
        class Child1(Parent):
            pass
        class Child2(Parent):
            pass

    @classmethod
    def setup_mappers(cls):
        child1 = cls.tables.child1
        child2 = cls.tables.child2
        Parent = cls.classes.Parent
        parent = cls.tables.parent
        Child1 = cls.classes.Child1
        Child2 = cls.classes.Child2
        secondary = cls.tables.secondary

        mapper(Parent, parent,
            polymorphic_on=parent.c.cls)

        mapper(Child1, child1,
            inherits=Parent,
            polymorphic_identity='child1',
            properties={
                'left_child2':relationship(
                    Child2,
                    secondary=secondary,
                    primaryjoin=parent.c.id == secondary.c.right_id,
                    secondaryjoin=parent.c.id == secondary.c.left_id,
                    uselist=False,
                    backref="right_children")})

        mapper(Child2, child2,
            inherits=Parent,
            polymorphic_identity='child2')

    def test_query_crit(self):
        Child1, Child2 = self.classes.Child1, self.classes.Child2
        sess = create_session()
        c11, c12, c13 = Child1(), Child1(), Child1()
        c21, c22, c23 = Child2(), Child2(), Child2()
        c11.left_child2 = c22
        c12.left_child2 = c22
        c13.left_child2 = c23
        sess.add_all([c11, c12, c13, c21, c22, c23])
        sess.flush()

        # test that the join to Child2 doesn't alias Child1 in the select
        eq_(set(sess.query(Child1).join(Child1.left_child2)),
            set([c11, c12, c13]))

        eq_(set(sess.query(Child1, Child2).join(Child1.left_child2)),
            set([(c11, c22), (c12, c22), (c13, c23)]))

        # test __eq__() on property is annotating correctly
        eq_(set(sess.query(Child2)
                    .join(Child2.right_children)
                    .filter(Child1.left_child2 == c22)),
            set([c22]))

        # test the same again
        self.assert_compile(
            sess.query(Child2)
                .join(Child2.right_children)
                .filter(Child1.left_child2 == c22)
                .with_labels().statement,
            "SELECT child2.id AS child2_id, parent.id AS parent_id, "
            "parent.cls AS parent_cls FROM secondary AS secondary_1, "
            "parent JOIN child2 ON parent.id = child2.id JOIN secondary AS "
            "secondary_2 ON parent.id = secondary_2.left_id JOIN (SELECT "
            "parent.id AS parent_id, parent.cls AS parent_cls, child1.id AS "
            "child1_id FROM parent JOIN child1 ON parent.id = child1.id) AS "
            "anon_1 ON anon_1.parent_id = secondary_2.right_id WHERE "
            "anon_1.parent_id = secondary_1.right_id AND :param_1 = "
            "secondary_1.left_id",
            dialect=default.DefaultDialect()
        )

    def test_eager_join(self):
        Child1, Child2 = self.classes.Child1, self.classes.Child2
        sess = create_session()
        c1 = Child1()
        c1.left_child2 = Child2()
        sess.add(c1)
        sess.flush()

        # test that the splicing of the join works here, doesn't break in
        # the middle of "parent join child1"
        q = sess.query(Child1).options(joinedload('left_child2'))
        self.assert_compile(q.limit(1).with_labels().statement,
            "SELECT anon_1.child1_id AS anon_1_child1_id, anon_1.parent_id "
            "AS anon_1_parent_id, anon_1.parent_cls AS anon_1_parent_cls, "
            "anon_2.child2_id AS anon_2_child2_id, anon_2.parent_id AS "
            "anon_2_parent_id, anon_2.parent_cls AS anon_2_parent_cls FROM "
            "(SELECT child1.id AS child1_id, parent.id AS parent_id, "
            "parent.cls AS parent_cls FROM parent JOIN child1 ON parent.id = "
            "child1.id LIMIT :param_1) AS anon_1 LEFT OUTER JOIN secondary "
            "AS secondary_1 ON anon_1.parent_id = secondary_1.right_id LEFT "
            "OUTER JOIN (SELECT parent.id AS parent_id, parent.cls AS "
            "parent_cls, child2.id AS child2_id FROM parent JOIN child2 ON "
            "parent.id = child2.id) AS anon_2 ON anon_2.parent_id = "
            "secondary_1.left_id",
            {'param_1':1},
            dialect=default.DefaultDialect())

        # another way to check
        assert q.limit(1).with_labels().subquery().count().scalar() == 1
        assert q.first() is c1

    def test_subquery_load(self):
        Child1, Child2 = self.classes.Child1, self.classes.Child2
        sess = create_session()
        c1 = Child1()
        c1.left_child2 = Child2()
        sess.add(c1)
        sess.flush()
        sess.expunge_all()

        query_ = sess.query(Child1).options(subqueryload('left_child2'))
        for row in query_.all():
            assert row.left_child2

class EagerToSubclassTest(fixtures.MappedTest):
    """Test eager loads to subclass mappers"""

    run_setup_classes = 'once'
    run_setup_mappers = 'once'
    run_inserts = 'once'
    run_deletes = None

    @classmethod
    def define_tables(cls, metadata):
        Table('parent', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('data', String(10)))

        Table('base', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('type', String(10)),
            Column('related_id', Integer,
                ForeignKey('related.id')))

        Table('sub', metadata,
            Column('id', Integer,
                ForeignKey('base.id'),
                primary_key=True),
            Column('data', String(10)),
            Column('parent_id', Integer,
                ForeignKey('parent.id'),
                nullable=False))

        Table('related', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('data', String(10)))

    @classmethod
    def setup_classes(cls):
        class Parent(cls.Comparable):
            pass
        class Base(cls.Comparable):
            pass
        class Sub(Base):
            pass
        class Related(cls.Comparable):
            pass

    @classmethod
    def setup_mappers(cls):
        sub = cls.tables.sub
        Sub = cls.classes.Sub
        base = cls.tables.base
        Base = cls.classes.Base
        parent = cls.tables.parent
        Parent = cls.classes.Parent
        related = cls.tables.related
        Related = cls.classes.Related

        mapper(Parent, parent,
            properties={'children':relationship(Sub, order_by=sub.c.data)})

        mapper(Base, base,
            polymorphic_on=base.c.type,
            polymorphic_identity='b',
            properties={'related':relationship(Related)})

        mapper(Sub, sub,
            inherits=Base,
            polymorphic_identity='s')

        mapper(Related, related)

    @classmethod
    def insert_data(cls):
        global p1, p2

        Parent = cls.classes.Parent
        Sub = cls.classes.Sub
        Related = cls.classes.Related
        sess = Session()
        r1, r2 = Related(data='r1'), Related(data='r2')
        s1 = Sub(data='s1', related=r1)
        s2 = Sub(data='s2', related=r2)
        s3 = Sub(data='s3')
        s4 = Sub(data='s4', related=r2)
        s5 = Sub(data='s5')
        p1 = Parent(data='p1', children=[s1, s2, s3])
        p2 = Parent(data='p2', children=[s4, s5])
        sess.add(p1)
        sess.add(p2)
        sess.commit()

    def test_joinedload(self):
        Parent = self.classes.Parent
        sess = Session()
        def go():
            eq_(sess.query(Parent)
                    .options(joinedload(Parent.children)).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 1)

    def test_contains_eager(self):
        Parent = self.classes.Parent
        Sub = self.classes.Sub
        sess = Session()
        def go():
            eq_(sess.query(Parent)
                    .join(Parent.children)
                    .options(contains_eager(Parent.children))
                    .order_by(Parent.data, Sub.data).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 1)

    def test_subq_through_related(self):
        Parent = self.classes.Parent
        Sub = self.classes.Sub
        sess = Session()
        def go():
            eq_(sess.query(Parent)
                    .options(subqueryload_all(Parent.children, Sub.related))
                    .order_by(Parent.data).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 3)

class SubClassEagerToSubClassTest(fixtures.MappedTest):
    """Test joinedloads from subclass to subclass mappers"""

    run_setup_classes = 'once'
    run_setup_mappers = 'once'
    run_inserts = 'once'
    run_deletes = None

    @classmethod
    def define_tables(cls, metadata):
        Table('parent', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('type', String(10)),
        )

        Table('subparent', metadata,
            Column('id', Integer,
                ForeignKey('parent.id'),
                primary_key=True),
            Column('data', String(10)),
        )

        Table('base', metadata,
            Column('id', Integer,
                primary_key=True,
                test_needs_autoincrement=True),
            Column('type', String(10)),
        )

        Table('sub', metadata,
            Column('id', Integer,
                ForeignKey('base.id'),
                primary_key=True),
            Column('data', String(10)),
            Column('subparent_id', Integer,
                ForeignKey('subparent.id'),
                nullable=False)
        )

    @classmethod
    def setup_classes(cls):
        class Parent(cls.Comparable):
            pass
        class Subparent(Parent):
            pass
        class Base(cls.Comparable):
            pass
        class Sub(Base):
            pass

    @classmethod
    def setup_mappers(cls):
        sub = cls.tables.sub
        Sub = cls.classes.Sub
        base = cls.tables.base
        Base = cls.classes.Base
        parent = cls.tables.parent
        Parent = cls.classes.Parent
        subparent = cls.tables.subparent
        Subparent = cls.classes.Subparent

        mapper(Parent, parent,
            polymorphic_on=parent.c.type,
            polymorphic_identity='b')

        mapper(Subparent, subparent,
            inherits=Parent,
            polymorphic_identity='s',
            properties={
                'children':relationship(Sub, order_by=base.c.id)})

        mapper(Base, base,
            polymorphic_on=base.c.type,
            polymorphic_identity='b')

        mapper(Sub, sub,
            inherits=Base,
            polymorphic_identity='s')

    @classmethod
    def insert_data(cls):
        global p1, p2

        Sub, Subparent = cls.classes.Sub, cls.classes.Subparent
        sess = create_session()
        p1 = Subparent(
            data='p1',
            children=[Sub(data='s1'), Sub(data='s2'), Sub(data='s3')])
        p2 = Subparent(
            data='p2',
            children=[Sub(data='s4'), Sub(data='s5')])
        sess.add(p1)
        sess.add(p2)
        sess.flush()

    def test_joinedload(self):
        Subparent = self.classes.Subparent

        sess = create_session()
        def go():
            eq_(sess.query(Subparent)
                    .options(joinedload(Subparent.children)).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 1)

        sess.expunge_all()
        def go():
            eq_(sess.query(Subparent)
                    .options(joinedload("children")).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 1)

    def test_contains_eager(self):
        Subparent = self.classes.Subparent

        sess = create_session()
        def go():
            eq_(sess.query(Subparent)
                    .join(Subparent.children)
                    .options(contains_eager(Subparent.children)).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 1)

        sess.expunge_all()
        def go():
            eq_(sess.query(Subparent)
                    .join(Subparent.children)
                    .options(contains_eager("children")).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 1)

    def test_subqueryload(self):
        Subparent = self.classes.Subparent

        sess = create_session()
        def go():
            eq_(sess.query(Subparent)
                    .options(subqueryload(Subparent.children)).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 2)

        sess.expunge_all()
        def go():
            eq_(sess.query(Subparent)
                    .options(subqueryload("children")).all(),
                [p1, p2])
        self.assert_sql_count(testing.db, go, 2)

