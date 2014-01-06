# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.osv.model_extensions
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# @created: 2013-11-27

'''Xœuf ORM extensions for Open Object (OpenERP) models.

All the attributes of this module must be functions that can be integrated as
`BaseModel` methods.

Use :func:`xoeuf`
'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)


INTEGRATED = False    # True after integrated to `ModelBase`


def search_read(self, cr, uid, *args, **kwargs):
    '''
    Search based on a domain and with the returned ids read records with the
    given fields.

    Parameters:

      :param self: model to operate in
      :param cr: database cursor
      :param uid: current user id

    Other optional arguments can be passed by position or by name:

    - ``domain``: list of tuples specifying the search domain (See below). An
      empty list or no argument can be used to match all records. Could be
      passed by position after ``uid``. Use ``args`` as an alias in arguments
      by name (``kwargs``).

    - ``fields``: list of field names to return (default: all fields would be
      returned). Example ``['id', 'name', 'age']``. Could be passed by
      position after ``domain``.

    - ``offset``: number of results to skip in the returned values
      (default: ``0``).

    - ``limit``: max number of records to return (default: unlimited)

    - ``order``: columns to sort by (default: ``self._order=id``)

    - ``context``: context arguments in a dictionary, like lang, time
      zone. Could be passed by position after ``fields``.

    :return: dictionary or list of dictionaries((one per record asked)) with
             requested field values.
    :rtype: [{‘name_of_the_field’: value, ...}, ...]

    :raise AccessError:
      * if user has no read rights on the requested object, or
      * if user tries to bypass access rules for read on the requested object

    **Expressing a search domain (or 'args')**

    Each tuple in the search domain needs to have 3 elements, in the form:
      ``('field_name', 'operator', value)``, where:

        - **field_name** must be a valid name of field of the object model,
            possibly following many-to-one relationships using dot-notation,
            e.g 'street' or 'partner_id.country' are valid values.

        - **operator** must be a string with a valid comparison operator from
            this list: ``=``, ``!=``, ``>``, ``>=``, ``<``, ``<=``, ``like``,
            ``ilike``, ``in``, ``not in``, ``child_of``, ``parent_left``,
            ``parent_right``.

          The semantics of most of these operators are obvious. The
          ``child_of`` operator will look for records who are children or
          grand-children of a given record, according to the semantics of this
          model (i.e following the relationship field named by
          ``self._parent_name``, by default ``parent_id``.

        - **value** must be a valid value to compare with the values of
          ``field_name``, depending on its type.

        Domain criteria can be combined using 3 logical operators than can be
        added between tuples: ``&`` (logical AND, default), ``|`` (logical
        OR), ``!`` (logical NOT).  These are *prefix* operators and the arity
        of the ``&`` and ``|`` operator is 2, while the arity of the ``!`` is
        just 1.  Be very careful about this when you combine them the first
        time.

        Here is an example of searching for Partners named *ABC* from Belgium
        and Germany whose language is not english::

            [('name','=','ABC'),'!',('language.code','=','en_US'),
             '|',('country_id.code','=','be'),('country_id.code','=','de'))

        The ``&`` is omitted as it is the default, and of course we could have
        used ``!=`` for the language, but what this domain really represents
        is::

            (name is 'ABC' AND (language is NOT english) AND
             (country is Belgium OR Germany))

    '''
    from xoutil.objects import get_and_del_first_of as _get
    # Convert all positional to keyword arguments
    for pos, arg in enumerate(args):
        kwargs[pos + 3] = arg
    # Get all arguments or default values
    domain = _get(kwargs, 3, 'domain', 'args', default=[])
    fields = _get(kwargs, 4, 'fields', default=[])
    ctx = _get(kwargs, 5, 'context', default={})
    offset = _get(kwargs, 'offset', default=0)
    limit = _get(kwargs, 'limit', default=None)
    order = _get(kwargs, 'order', default=None)
    assert not kwargs, \
      "Invalid %s arguments: %s" % (len(kwargs), kwargs.keys())
    # Do it
    ids = self.search(cr, uid, domain, offset=offset, limit=limit,
                      order=order, context=ctx)
    if len(ids) == 1:
        ids = ids[0]
    return self.read(cr, uid, ids, fields=fields, context=ctx) if ids else []


def search_browse(self, cr, uid, *args, **kwargs):
    '''
    Search based on a domain and with the returned ids browse corresponding
    records or return None if nothing is found.

    Parameters:

      :param self: model to operate in
      :param cr: database cursor
      :param uid: current user id

    Other optional arguments can be passed by position or by name:

    - ``domain``: list of tuples specifying the search domain (See below). An
      empty list or no argument can be used to match all records. Could be
      passed by position after ``uid``. Use ``args`` as an alias in arguments
      by name (``kwargs``).

    - ``offset``: number of results to skip in the returned values
      (default: ``0``).

    - ``limit``: max number of records to return (default: unlimited)

    - ``order``: columns to sort by (default: ``self._order=id``)

    - ``context``: context arguments in a dictionary, like lang, time
      zone. Could be passed by position after ``fields``.

    :return: object or list of objects requested or None

    :raise AccessError:
      * if user tries to bypass access rules for read on the requested object

    See :func:`search_read` for how to express a search domain.

    '''
    from xoutil.objects import get_and_del_first_of as _get
    # Convert all positional to keyword arguments
    for pos, arg in enumerate(args):
        kwargs[pos + 3] = arg
    # Get all arguments or default values
    domain = _get(kwargs, 3, 'domain', 'args', default=[])
    ctx = _get(kwargs, 4, 'context', default={})
    offset = _get(kwargs, 'offset', default=0)
    limit = _get(kwargs, 'limit', default=None)
    order = _get(kwargs, 'order', default=None)
    assert not kwargs, \
      "Invalid %s arguments: %s" % (len(kwargs), kwargs.keys())
    # Do it
    ids = self.search(cr, uid, domain, offset=offset, limit=limit,
                      order=order, context=ctx)
    if len(ids) == 1:
        ids = ids[0]
    return self.browse(cr, uid, ids, context=ctx) if ids else None


def field_value(self, cr, uid, ids, field_name, context=None):
    '''Read a field value for a set of objects.

    This method is very protective, if any ``False`` is passed as `ids`,
    ``False`` is returned without raising errors; Also related "2one" field
    values are returned only as id integers, not tuples (id, 'name').

    Parameters:

      :param self: model to operate in

      :param cr: database cursor

      :param uid: current user id

      :param ids: id or list of the ids of the records to read

      :param field_name: field name to return

      :param context: optional context dictionary - it may contains keys for
                      specifying certain options like ``context_lang``,
                      ``context_tz`` to alter the results of the call.

                      See method :func:`read` for more details.

      :return: a value if only one id is specified or a dictionary if more
               than one. ``False`` is returned when no record is associated
               with the ids.

      :rtype: same type of field or ``{id: value, ...}``

      :raise AccessError: * if user has no read rights on the requested object
                          * if user tries to bypass access rules for read on
                            the requested object

    '''
    if ids:
        fix = lambda v: v[0] if type(v) is tuple else v
        data = self.read(cr, uid, ids, [field_name], context=context)
        dt = type(data)
        if dt is dict:
            return fix(data.get(field_name, False))
        elif dt is list:
            count = len(data)
            if count == 0:
                return False
            elif count == 1:
                return fix(data[0][field_name])
            else:
                return {item['id']: fix(item[field_name]) for item in data}
        else:
            return data
    else:
        return False
