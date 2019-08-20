def validate_type(object_type: type, obj: object, name: str):
    """
    Check that obj is instance of object_type and raise error if it is not

    :param object_type: the type to check
    :param obj: the object to check
    :param name: the object name
    :raises TypeError: when obj is not None, and is not an instance of object_type.
    """
    if obj is not None and not isinstance(obj, object_type):
        raise TypeError('{name} must be of type {type}.'.format(**{'name': name, 'type': object_type}))
