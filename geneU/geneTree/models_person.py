from neomodel import (
    StructuredNode, StringProperty, One,
    RelationshipTo, RelationshipFrom, Relationship,
    ZeroOrOne, ArrayProperty, BooleanProperty, OneOrMore)
from uuid import uuid4
from geoencoding_node_structure.core import AddressComponent, Location
from date_node_structure.core import Day, NodeDate
# import geneTree.models_person as'
from string import Template


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Tree(StructuredNode):
    id = StringProperty(unique_index=True, default=uuid4)
    name = StringProperty(required=True)
    description = StringProperty()
    private = BooleanProperty(default=False)
    persons = RelationshipTo('Person', 'MEMBER')
    user = Relationship('core.models.UserNode', 'OWN')

    def set_owner(self, owner):
        self.user.connect(owner)

    def get_persons(self):
        return self.persons.all()


class Event(StructuredNode):
    id = StringProperty(unique_index=True, default=uuid4)
    location = Relationship(AddressComponent, 'LOCATION')
    location_prop = StringProperty()
    date_begin = Relationship(Day, 'DATE_BEGIN')
    date_end = Relationship(Day, 'DATE_END')
    description = StringProperty()

    def set_event(
            self, loc=None, location_prop=None, description=None,
            date_begin=None, date_end=None):
        if loc:
            locat = Location(address_components=loc).save()
            self.location.connect(locat)
        if date_begin:
            date_begin = NodeDate(date_begin).save()
            self.date_begin.connect(date_begin)
        if date_end:
            date_end = NodeDate(date_end).save()
            self.date_end.connect(date_end)
        if location_prop:
            self.location_prop = location_prop
        if description:
            self.description = description


class Marriage(Event):
    married = Relationship('Person', 'MARRIED')

    def add_spouse(self, married):
        self.married.connect(married)

    def get_spouses(self):
        return list(self.married.all())

    @classmethod
    def const(
            self, loc=None, location_prop=None,
            description=None, date_begin=None, date_end=None):
        a = self().save()
        a.set_event(loc, location_prop, description, date_begin, date_end)
        return a


class Divorce(Event):
    divorced = Relationship('Person', 'DIVORCED')

    def add_spouse(self, married):
        self.divorced.connect(married)

    def get_spouses(self):
        return list(self.divorced.all())

    @classmethod
    def const(
            self, loc=None, location_prop=None,
            description=None, date_begin=None, date_end=None):
        a = self().save()
        a.set_event(loc, location_prop, description, date_begin, date_end)
        return a


class Birth(Event):
    father = Relationship('Person', 'FATHER')
    son = Relationship('Person', 'SON')

    def add_father(self, father):
        self.father.connect(father)

    def set_son(self, son):
        self.son.connect(son)

    def get_fathers(self):
        return list(self.father.all())

    def get_son(self):
        a = list(self.son.all())
        if a:
            return a[0]
        else:
            return None

    @classmethod
    def const(
            self, son, loc=None, location_prop=None,
            description=None, date_begin=None, date_end=None):
        a = self().save()
        a.son.connect(son)
        a.set_event(loc, location_prop, description, date_begin, date_end)
        return a


class Death(Event):
    person = Relationship('Person', 'DEATH')

    def set_death(self, death):
        self.person.connect(death)

    def get_person(self):
        a = list(self.person.all())
        if a:
            return a[0]
        else:
            return None

    @classmethod
    def const(
            self, person, loc=None, location_prop=None,
            description=None, date_begin=None, date_end=None):
        a = self().save()
        a.person.connect(person)
        a.set_event(loc, location_prop, description, date_begin, date_end)
        return a


class Adoption(Event):
    father_adpt = Relationship('Person', 'FATHER')
    son_adpt = Relationship('Person', 'SON')

    def add_father(self, father):
        self.father_adpt.connect(father)

    def set_son(self, son):
        self.son_adpt.connect(son)

    def get_son(self):
        a = list(self.son_adpt.all())
        if a:
            return a[0]
        else:
            None

    def get_fathers(self):
        return list(self.father_adpt.all())

    @classmethod
    def const(
            self, son, loc=None, location_prop=None,
            description=None, date_begin=None, date_end=None):
        a = self().save()
        a.son_adpt.connect(son)
        a.set_event(loc, location_prop, description, date_begin, date_end)
        return a


class Lived(Event):
    lived_in = Relationship('Person', 'LIVED_IN')

    def set_person(self, person):
        self.lived_in.connect(person)

    def get_person(self):
        a = list(self.lived_in.all())
        if a:
            return a[0]
        else:
            None

    @classmethod
    def const(
            self, person, loc=None, location_prop=None,
            description=None, date_begin=None, date_end=None):
        a = self().save()
        a.lived_in.connect(person)
        a.set_event(loc, location_prop, description, date_begin, date_end)
        return a


class Person(StructuredNode):

    id = StringProperty(unique_index=True, default=uuid4)
    name = StringProperty()
    surname = StringProperty(index=True)
    second_surname = StringProperty(index=True)
    genere = StringProperty(choices=(('M', 1), ('F', 2)))

    married = Relationship('Marriage', 'MARRIED')
    divorced = Relationship('Divorce', 'DIVORCED')
    death = Relationship('Death', 'DEATH')
    father = Relationship('Birth', 'FATHER')
    father_adpt = Relationship('Adoption', 'FATHER')
    son = Relationship('Birth', 'SON')
    son_adpt = Relationship('Adoption', 'SON')
    lived_in = Relationship('Lived', 'LIVED_IN')

    tree = Relationship(Tree, 'MEMBER', cardinality=OneOrMore)

    query_similars = \
        Template("""
        START a=node({self})
        MATCH a-[:$relation]-(e1)-[:LOCATION]-()-[:LOCATION]-(e2)-[:$relation]-(b)
        MATCH e1-[:DATE_BEGIN]-(e1_date_begin)-[:MONTH]-(e1_month_begin)-[:YEAR]-(e1_year_begin)
        MATCH e1-[:DATE_END]-(e1_date_end)-[:MONTH]-(e1_month_end)-[:YEAR]-(e1_year_end)
        MATCH e2-[:DATE_BEGIN]-(e2_date_begin)-[:MONTH]-(e2_month_begin)-[:YEAR]-(e2_year_begin)
        MATCH e2-[:DATE_END]-(e2_date_end)-[:MONTH]-(e2_month_end)-[:YEAR]-(e2_year_end)
        WHERE a <> b
        //intersection time between events in the same location
        AND ((e2_year_begin.id > e1_year_begin.id AND e2_year_begin.id < e1_year_end.id)
            OR (e1_year_begin.id = e1_year_end.id AND e1_month_begin.value = e1_month_end.value
        AND e2_year_begin.id = e1_year_begin.id AND e2_month_begin.value = e1_month_begin.value
        AND e2_date_begin.value >= e1_date_begin.value AND e2_date_begin.value < e1_date_end.value)
        OR (e1_year_begin.id = e1_year_end.id AND e1_month_begin.value < e1_month_end.value
        AND e2_year_begin.id = e1_year_begin.id
        AND ((e2_month_begin.value = e1_month_begin.value AND e2_date_begin.value >= e1_date_begin.value)
        OR (e2_month_begin.value > e1_month_begin.value AND e2_month_begin.value < e1_month_end.value)
        OR (e2_month_begin.value = e1_month_end.value AND e2_date_begin.value < e1_date_end.value)))
        OR (e1_year_begin.id < e1_year_end.id
        AND e2_year_begin.id = e1_year_begin.id
        AND ((e2_month_begin.value > e1_month_begin.value)
        OR (e2_month_begin.value = e1_month_begin.value AND e2_date_begin.value >= e1_date_begin.value)))
        OR (e1_year_begin.id < e1_year_end.id
        AND e2_year_begin.id = e1_year_end.id
        AND ((e2_month_begin.value < e1_month_end.value)
        OR (e2_month_begin.value = e1_month_end.value AND e2_date_begin.value < e1_date_end.value))))
        OR ((e2_year_end.id > e1_year_begin.id AND e2_year_end.id < e1_year_end.id)
            OR (e1_year_begin.id = e1_year_end.id AND e1_month_begin.value = e1_month_end.value
        AND e2_year_end.id = e1_year_begin.id AND e2_month_end.value = e1_month_begin.value
        AND e2_date_end.value >= e1_date_begin.value AND e2_date_end.value < e1_date_end.value)
        OR (e1_year_begin.id = e1_year_end.id AND e1_month_begin.value < e1_month_end.value
        AND e2_year_end.id = e1_year_begin.id
        AND ((e2_month_end.value = e1_month_begin.value AND e2_date_end.value >= e1_date_begin.value)
        OR (e2_month_end.value > e1_month_begin.value AND e2_month_end.value < e1_month_end.value)
        OR (e2_month_end.value = e1_month_end.value AND e2_date_end.value < e1_date_end.value)))
        OR (e1_year_begin.id < e1_year_end.id
        AND e2_year_end.id = e1_year_begin.id
        AND ((e2_month_end.value > e1_month_begin.value)
        OR (e2_month_end.value = e1_month_begin.value AND e2_date_end.value >= e1_date_begin.value)))
        OR (e1_year_begin.id < e1_year_end.id
        AND e2_year_end.id = e1_year_end.id
        AND ((e2_month_end.value < e1_month_end.value)
        OR (e2_month_end.value = e1_month_end.value AND e2_date_end.value < e1_date_end.value))))
        OR (((e1_year_begin.id > e2_year_begin.id AND e1_year_begin.id < e2_year_end.id)
            OR (e2_year_begin.id = e2_year_end.id AND e2_month_begin.value = e2_month_end.value
        AND e1_year_begin.id = e2_year_begin.id AND e1_month_begin.value = e2_month_begin.value
        AND e1_date_begin.value >= e2_date_begin.value AND e1_date_begin.value < e2_date_end.value)
        OR (e2_year_begin.id = e2_year_end.id AND e2_month_begin.value < e2_month_end.value
        AND e1_year_begin.id = e2_year_begin.id
        AND ((e1_month_begin.value = e2_month_begin.value AND e1_date_begin.value >= e2_date_begin.value)
        OR (e1_month_begin.value > e2_month_begin.value AND e1_month_begin.value < e2_month_end.value)
        OR (e1_month_begin.value = e2_month_end.value AND e1_date_begin.value < e2_date_end.value)))
        OR (e2_year_begin.id < e2_year_end.id
        AND e1_year_begin.id = e2_year_begin.id
        AND ((e1_month_begin.value > e2_month_begin.value)
        OR (e1_month_begin.value = e2_month_begin.value AND e1_date_begin.value >= e2_date_begin.value)))
        OR (e2_year_begin.id < e2_year_end.id
        AND e1_year_begin.id = e2_year_end.id
        AND ((e1_month_begin.value < e2_month_end.value)
        OR (e1_month_begin.value = e2_month_end.value AND e1_date_begin.value < e2_date_end.value))))
        AND ((e1_year_end.id > e2_year_begin.id AND e1_year_end.id < e2_year_end.id)
            OR (e2_year_begin.id = e2_year_end.id AND e2_month_begin.value = e2_month_end.value
        AND e1_year_end.id = e2_year_begin.id AND e1_month_end.value = e2_month_begin.value
        AND e1_date_end.value >= e2_date_begin.value AND e1_date_end.value < e2_date_end.value)
        OR (e2_year_begin.id = e2_year_end.id AND e2_month_begin.value < e2_month_end.value
        AND e1_year_end.id = e2_year_begin.id
        AND ((e1_month_end.value = e2_month_begin.value AND e1_date_end.value >= e2_date_begin.value)
        OR (e1_month_end.value > e2_month_begin.value AND e1_month_end.value < e2_month_end.value)
        OR (e1_month_end.value = e2_month_end.value AND e1_date_end.value < e2_date_end.value)))
        OR (e2_year_begin.id < e2_year_end.id
        AND e1_year_end.id = e2_year_begin.id
        AND ((e1_month_end.value > e2_month_begin.value)
        OR (e1_month_end.value = e2_month_begin.value AND e1_date_end.value >= e2_date_begin.value)))
        OR (e2_year_begin.id < e2_year_end.id
        AND e1_year_end.id = e2_year_end.id
        AND ((e1_month_end.value < e2_month_end.value)
        OR (e1_month_end.value = e2_month_end.value AND e1_date_end.value < e2_date_end.value)))))
        RETURN b
        """)

    def set_lieved(
            self, date_begin=None,
            date_end=None, loc=None,
            loc_p=None, description=None
    ):
        b = Lived().save()
        b.set_event(
            loc=loc, location_prop=loc_p, date_begin=date_begin,
            date_end=date_end)
        b.lived_in.connect(self)
        if description:
            self.description = description
        return b

    def set_marriage(
            self, spouse, date_begin=None,
            date_end=None, loc=None, loc_p=None):
        b = Marriage().save()
        b.set_event(
            loc=loc, location_prop=loc_p, date_begin=date_begin,
            date_end=date_end)
        b.married.connect(self)
        if spouse:
            b.married.connect(spouse)
        return b

    def set_divorced(
            self, spouse, date_begin=None, date_end=None,
            loc=None, loc_p=None):
        b = Divorce().save()
        b.set_event(
            loc=loc, location_prop=loc_p,
            date_begin=date_begin, date_end=date_end)
        b.divorced.connect(self)
        if spouse:
            b.divorced.connect(spouse)
        return b

    def set_birth(
            self, date_begin=None, date_end=None,
            loc=None, loc_p=None, father1=None, father2=None):
        if self.son.all():
            raise AttributeError('...')
        b = Birth().save()
        b.set_event(
            loc=loc, location_prop=loc_p,
            date_begin=date_begin, date_end=date_end)
        b.son.connect(self)
        if father1:
            father1.father.connect(b)
        if father2:
            father2.father.connect(b)
        return b

    def set_death(
            self, description=None, date_begin=None, date_end=None,
            loc=None, loc_p=None):
        if self.death.all():
            raise AttributeError('...')
        b = Death().save()
        b.set_event(
            loc=loc, location_prop=loc_p, date_begin=date_begin,
            date_end=date_end)
        b.person.connect(self)
        if description:
            b.description = description
        return b

    def set_adopted(
            self, father1, father2, date_begin=None, date_end=None, loc=None,
            loc_p=None):
        if self.son_adpt.all():
            raise AttributeError('...')
        b = Adoption().save()
        b.set_event(
            loc=loc, location_prop=loc_p, date_begin=date_begin,
            date_end=date_end)
        b.son_adpt.connect(self)
        if father1:
            father2.father_adpt.connect(b)
        if father2:
            father2.father_adpt.connect(b)
        return b

    def set_tree(self, tree):
        self.tree.connect(tree)

    def get_marriages(self):
        return self.married.all()

    def get_divorces(self):
        return self.divorced.all()

    def get_adopted(self):
        a = list(self.son_adpt.all())
        if a:
            return a[0]
        else:
            return None

    def get_birth(self):
        a = list(self.son.all())
        if a:
            return a[0]
        else:
            return None

    def get_death(self):
        a = list(self.death.all())
        if a:
            return a[0]
        else:
            return None

    def get_adoptions(self):
        return self.father_adpt.all()

    def get_father(self):
        return self.father.all()

    def get_lived(self):
        return self.lived_in.all()

    @classmethod
    def get_query_similars(cls):
        return cls.query_similars

    def get_similar_lived(self):
        query = self.get_query_similars().substitute(relation='LIVED_IN')
        print 'query resp: ', self.cypher(query)
        results, columns = self.cypher(query)
        res = [self.inflate(row[0]) for row in results]
        print res
        print list(set(res))
        return list(set(res))
