from rest_framework import serializers
from .models import Person
from geoencoding_node_structure.serializers import LocationSerializer
from date_node_structure.serializers import DateSerializer
from django.core.exceptions import ValidationError
import ast
from datetime import datetime
import json
import copy


class PersonSerializer(serializers.BaseSerializer):

    def __init__(self, *args, **kwargs):

        self.simple = kwargs.pop('simple', False)
        super(PersonSerializer, self).__init__(*args, **kwargs)

    def __pop_all_relational_data(self, data):
        relation_data = {}
        if 'birth_date_begin' in data:
            relation_data['birth_date_begin'] = data.pop(
                'birth_date_begin')
        if 'birth_date_end' in data:
            relation_data['birth_date_end'] = data.pop(
                'birth_date_end')
        if 'death_date_begin' in data:
            relation_data['death_date_begin'] = data.pop(
                'death_date_begin')
        if 'death_date_end' in data:
            relation_data['death_date_end'] = data.pop(
                'death_date_end')
        if 'son_of' in data:
            relation_data['son_of'] = data.pop('son_of')
        if 'sons' in data:
            relation_data['sons'] = data.pop('sons')
        if 'adopted' in data:
            relation_data['adopted'] = data.pop('adopted')
        if 'adopted_by' in data:
            relation_data['adopted_by'] = data.pop('adopted_by')
        if 'married' in data:
            relation_data['married'] = data.pop('married')
        if 'divorced' in data:
            relation_data['divorced'] = data.pop('divorced')
        if 'born_in' in data:
            relation_data['born_in'] = data.pop('born_in')
        if 'death_in' in data:
            relation_data['death_in'] = data.pop('death_in')
        if 'lived_in' in data:
            relation_data['lived_in'] = data.pop('lived_in')
        return relation_data

    def to_internal_value(self, data):

        name = data.get('name')
        surname = data.get('surname')
        second_surname = data.get('second_surname')
        genere = data.get('genere')
        birth_date_begin = data.get('birth_date_begin')
        birth_date_end = data.get('birth_date_end')
        death_date_begin = data.get('death_date_begin')
        death_date_end = data.get('death_date_end')
        born_in = data.get('born_in')
        death_in = data.get('death_in')
        lived_in = data.get('lived_in', [])
        son_of = data.get('son_of', [])
        sons = data.get('sons', [])
        adopted = data.get('adopted', [])
        adopted_by = data.get('adopted_by', [])
        married = data.get('married', [])
        divorced = data.get('divorced', [])

        if not name:
            raise ValidationError({
                'name': "name is required"
                })

        # Perform the data validation.
        if genere and genere != 'M' and genere != 'W':
            raise ValidationError({
                'genere': "Incorrect data format, should be 'M' or 'W'"
            })

        if son_of:
            try:
                son_of = ast.literal_eval(son_of)
            except(ValidationError):
                raise ValidationError({
                    'son_of': "Incorrect data format, should be a list"
                })
        if sons:
            try:
                sons = ast.literal_eval(sons)
            except(ValidationError):
                raise ValidationError({
                    'sons': "Incorrect data format, should be a list"
                })
        if divorced:
            try:
                divorced = ast.literal_eval(divorced)
            except(ValidationError):
                raise ValidationError({
                    'divorced': "Incorrect data format, should be a list"
                })
        if adopted:
            try:
                adopted = ast.literal_eval(adopted)
            except(ValidationError):
                raise ValidationError({
                    'adopted': "Incorrect data format, should be a list"
                })
        if adopted_by:
            try:
                adopted_by = ast.literal_eval(adopted_by)
            except(ValidationError):
                raise ValidationError({
                    'adopted_by': "Incorrect data format, should be a list"
                })
        if married:
            try:
                married = ast.literal_eval(married)
            except(ValidationError):
                raise ValidationError({
                    'married': "Incorrect data format, should be a list"
                })
        if lived_in:
            try:
                lived_in = ast.literal_eval(lived_in)
                # lived_in = [json.loads(lv) for lv in lived_in]
            except(ValidationError):
                raise ValidationError({
                    'lived_in': "Incorrect data format," +
                    "should be a list of JSONs"
                })
        if born_in:
            try:
                born_in = ast.literal_eval(born_in)
            except(ValidationError):
                raise ValidationError({
                    'born_in': "Incorrect data format, should be a JSON"
                })
        if death_in:
            try:
                death_in = json.loads(death_in)
            except(ValidationError):
                raise ValidationError({
                    'death_in': "Incorrect data format, should be a JSON"
                })
        if birth_date_begin:
            try:
                birth_date_begin = datetime.strptime(
                    birth_date_begin, "%Y-%m-%d")
            except(ValidationError):
                raise ValidationError({
                    'birth_date_begin': "Incorrect data format," +
                    " the date format should be YYYY-MM-DD"
                    })
        if birth_date_end:
            try:
                birth_date_end = datetime.strptime(
                    birth_date_end, "%Y-%m-%d")
            except(ValidationError):
                raise ValidationError({
                    'birth_date_end': "Incorrect data format," +
                    " the date format should be YYYY-MM-DD"
                    })
        if death_date_begin:
            try:
                death_date_begin = datetime.strptime(
                    death_date_begin, "%Y-%m-%d")
            except(ValidationError):
                raise ValidationError({
                    'death_date_begin': "Incorrect data format," +
                    " the date format should be YYYY-MM-DD"
                    })
        if death_date_end:
            try:
                death_date_end = datetime.strptime(
                    death_date_end, "%Y-%m-%d")
            except(ValidationError):
                raise ValidationError({
                    'death_date_end': "Incorrect data format," +
                    " the date format should be YYYY-MM-DD"
                    })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        validated_data = {
            'name': name,
            'surname': surname,
            'second_surname': second_surname,
            'genere': genere,
            'birth_date_begin': birth_date_begin,
            'birth_date_end': birth_date_end,
            'death_date_begin': death_date_begin,
            'death_date_end': death_date_end,
            'born_in': born_in,
            'death_in': death_in,
            'lived_in': lived_in,
            'son_of': son_of,
            'sons': sons,
            'adopted': adopted,
            'adopted_by': adopted_by,
            'married': married,
            'divorced': divorced
        }

        aux = copy.deepcopy(validated_data)
        if self.partial:
            for key in aux:
                if key not in data:
                    validated_data.pop(key)

        return validated_data

    def to_representation(self, node):

        if self.simple:
            return '/persons/' + node.id

        sons = list(node.sons.all())
        sons_serialized = None
        if sons:
            sons_serialized = PersonSerializer(
                sons, many=True, simple=True).data

        son_of = list(node.son_of.all())
        son_of_serialized = None
        if son_of:
            son_of_serialized = PersonSerializer(
                son_of, many=True, simple=True).data

        adopted = list(node.adopted.all())
        adopted_serialized = None
        if adopted:
            sons_serialized = PersonSerializer(
                adopted, many=True, simple=True).data

        adopted_by = list(node.adopted_by.all())
        adopted_by_serialized = None
        if adopted_by:
            adopted_by_serialized = PersonSerializer(
                adopted_by, many=True, simple=True).data

        born_in = list(node.born_in.all())
        born_in_serialized = None
        if born_in:
            born_in_serialized = LocationSerializer(born_in[0]).data

        death_in = list(node.death_in.all())
        death_in_serialized = None
        if death_in:
            death_in_serialized = LocationSerializer(death_in[0]).data

        lived_in = list(node.lived_in.all())
        lived_in_serialized = None
        if lived_in:
            lived_in_serialized = LocationSerializer(
                lived_in, many=True).data

        death_date = list(node.death_date_begin.all())
        death_date_begin_serialized = None
        if death_date:
            death_date_begin_serialized = DateSerializer(death_date[0]).data

        death_date = list(node.death_date_end.all())
        death_date_end_serialized = None
        if death_date:
            death_date_end_serialized = DateSerializer(death_date[0]).data

        birth_date = list(node.birth_date_begin.all())
        birth_date_begin_serialized = None
        if birth_date:
            birth_date_begin_serialized = DateSerializer(birth_date[0]).data

        birth_date = list(node.birth_date_end.all())
        birth_date_end_serialized = None
        if birth_date:
            birth_date_end_serialized = DateSerializer(birth_date[0]).data

        married = list(node.married.all())
        married_serialized = None
        if married:
            married_serialized = PersonSerializer(
                married, many=True, simple=True).data

        divorced = list(node.divorced.all())
        divorced_serialized = None
        if divorced:
            divorced_serialized = PersonSerializer(
                divorced, many=True, simple=True).data

        return {
            'url': '/persons/' + node.id,
            'name': node.name,
            'surname': node.surname,
            'second_surname': node.second_surname,
            'genere': node.genere,
            'birth_date_begin': birth_date_begin_serialized,
            'birth_date_end': birth_date_end_serialized,
            'death_date_begin': death_date_begin_serialized,
            'death_date_end': death_date_end_serialized,
            'sons': sons_serialized,
            'son_of': son_of_serialized,
            'adopted': adopted_serialized,
            'adopted_by': adopted_by_serialized,
            'born_in': born_in_serialized,
            'death_in': death_in_serialized,
            'lived_in': lived_in_serialized,
            'married': married_serialized,
            'divorced': divorced_serialized
        }

    def create(self, validated_data):
        rel = self.__pop_all_relational_data(validated_data)
        result = Person(**validated_data).save()
        result.create_relations(**rel)
        return result

    def update(self, instance, validated_data):
        rel = self.__pop_all_relational_data(validated_data)
        instance.set_attr(**validated_data)
        instance.create_relations(**rel)
        return instance
