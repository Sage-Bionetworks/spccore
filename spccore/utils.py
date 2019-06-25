def validate_type(object_type: object, obj: object, name: str):
    """
    Check that obj is instance of object_type and raise error if it is not

    :param object_type: the type to check
    :param obj: the object to check
    :param name: the object name
    """
    if obj is not None and not isinstance(object_type, obj):
        raise TypeError('{name} must be of type {type}.'.format(**{'name': name, 'type': object_type}))
