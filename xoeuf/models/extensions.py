#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Xœuf ORM extensions for Open Object (OpenERP) models.

All the attributes of this module must be functions that can be integrated as
`BaseModel` methods or operators.

Operators name has the format ``operator__<name>`` and are converted to
``__<name>__``.

Use :func:`xoeuf.osv.improve.integrate_extensions` for integrate these
extensions.

'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import)

from xoeuf.models import _past
_past.dissuade()

from xoutil.deprecation import deprecated

del _past


INTEGRATED = False    # True after integrated to `ModelBase`


def search_read(self, cr, uid, *args, **kwargs):
    '''Search based on a domain and with the returned ids read records with the
    given fields.

    :param self: model to operate in
    :param cr: database cursor
    :param uid: current user id

    Other optional arguments can be passed by position or by name:

    - ``domain``: list of tuples specifying the search domain (see below).  An
      empty list or no argument can be used to match all records.  Could be
      passed by position after ``uid``. Use ``args`` as an alias in arguments
      by name (``kwargs``).

    - ``fields``: list of field names to return (default: all fields would be
      returned). Example ``['id', 'name', 'age']``.  Could be passed by
      position after ``domain``.

    - ``context``: context arguments in a dictionary, like lang, time
      zone. Could be passed by position after ``fields``.

    Keyword only arguments:

    - ``offset``: number of results to skip in the returned values
      (default: ``0``).

    - ``limit``: max number of records to return (default: unlimited)

    - ``order``: columns to sort by (default: ``self._order=id``)

    - ``ensure_list``:  Always return a list.  By default is False.

      .. versionadded:: 0.5.1

    :return: dictionary or list of dictionaries (one per record asked) with
             requested field values.
    :rtype: ``[{‘name_of_the_field’: value, ...}, ...]``

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

          The semantics of most of these operators are obvious.  The
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
        or Germany whose language is not English::

            [('name','=','ABC'),'!',('language.code','=','en_US'),
             '|',('country_id.code','=','be'),('country_id.code','=','de'))

        The ``&`` is omitted as it is the default, and of course we could have
        used ``!=`` for the language, but what this domain really represents
        is::

            (name is 'ABC' AND (language is NOT english) AND
             (country is Belgium OR Germany))

    '''
    from xoutil.objects import pop_first_of as _get
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
    ensure_list = _get(kwargs, 'ensure_list', default=False)
    assert not kwargs, \
        "Invalid %s arguments: %s" % (len(kwargs), kwargs.keys())
    # Do it
    ids = self.search(cr, uid, domain, offset=offset, limit=limit,
                      order=order, context=ctx)
    if len(ids) == 1 and not ensure_list:
        ids = ids[0]
    return self.read(cr, uid, ids, fields=fields, context=ctx) if ids else []


@deprecated('search', 'Use the new API search method')
def search_browse(self, cr, uid, *args, **kwargs):
    '''Search based on a domain and with the returned ids browse corresponding
    records or return None if nothing is found.

    :param self: model to operate in
    :param cr: database cursor
    :param uid: current user id

    The rest of the arguments are the same as `search_read`:func:, excluding
    `fields` which is not acceptable in this method.

    :return: object or list of objects requested or None

    :raise AccessError:
      * if user tries to bypass access rules for read on the requested object

    See :func:`search_read` for how to express a search domain.

    '''
    from xoutil.objects import pop_first_of as _get
    # Convert all positional to keyword arguments
    for pos, arg in enumerate(args):
        kwargs[pos + 3] = arg
    # Get all arguments or default values
    domain = _get(kwargs, 3, 'domain', 'args', default=[])
    ctx = _get(kwargs, 4, 'context', default={})
    offset = _get(kwargs, 'offset', default=0)
    limit = _get(kwargs, 'limit', default=None)
    order = _get(kwargs, 'order', default=None)
    ensure_list = _get(kwargs, 'ensure_list', default=False)
    assert not kwargs, \
        "Invalid %s arguments: %s" % (len(kwargs), kwargs.keys())
    self = self.browse(cr, uid, context=ctx)
    result = self.search(domain, offset=offset, limit=limit,
                         order=order)
    if ensure_list:
        return list(result)  # note: is result is empty returns the empty list
    else:
        return result


def field_value(self, cr, uid, ids, field_name, context=None):
    '''Read a field value for a set of objects.

    This method is very protective, if any ``False`` is passed as `ids`,
    ``False`` is returned without raising errors; also related "2one" field
    values are returned only as id integers, not tuples (id, 'name').

    :param self: model to operate in

    :param cr: database cursor

    :param uid: current user id

    :param ids: id or list of the ids of the records to read

    :param field_name: field name to return

    :param context: optional context dictionary - it may contains keys for
                    specifying certain options like ``context_lang``,
                    ``context_tz`` to alter the results of the call.

                    See method :func:`read` for more details.

    :return: a value if only one id is specified or a dictionary if more than
             one. ``False`` is returned when no record is associated with the
             ids.

    :rtype: same type of field or ``{id: value, ...}``

    :raise AccessError:

       * if user has no read rights on the requested object

       * if user tries to bypass access rules for read on the requested object

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


def search_value(self, cr, uid, args, field_name, context=None):
    '''Similar to `find_value`:func: but searching.

    Instead of an `ids` it expects a search domain.  Matching ids will be then
    passed to `find_value`:func:.

    '''
    ids = self.search(cr, uid, args, context=context)
    return field_value(self, cr, uid, ids, field_name, context=context)


def obj_ref(self, cr, uid, xml_id):
    '''Returns (model_name, res_id) corresponding to a given `xml_id`

    If `xml_id` contains a dot '.', absolute ID (``<module>.<external-id>``)
    is assumed.

    If no module part is given, the resulting object reference is looked up in
    all alternatives with the same local ``xml-id``, first using
    ``self._module`` (for field ``module``) and after ``self._name`` (for
    field ``model``).

    If no alternative exactly match, a list of tuples will be returned, each
    one with ``(model, res_id)``.

    If no record is found ``False`` is returned.

    :param self: model to operate in

    :param cr: database cursor

    :param uid: current user id

    :param xml_id: external id to look for

    '''
    imd = self.pool.get('ir.model.data')
    fields = ['name', 'module', 'model', 'res_id']
    fname, fmod, fmodel, fid = fields
    if '.' in xml_id:
        module, ext_id = xml_id.split('.', 1)
        query = [(fmod, '=', module), (fname, '=', ext_id)]
        data = search_read(imd, cr, uid, query, [fmodel, fid])
    else:
        query = [(fname, '=', xml_id)]
        data = search_read(imd, cr, uid, domain=query, fields=fields)
    if data:
        dt = type(data)
        if issubclass(dt, dict):
            return data[fmodel], data[fid]
        elif issubclass(dt, list):
            count = len(data)
            if count == 1:
                res = data[0]
                return res[fmodel], res[fid]
            else:
                test = lambda d: d['module'] == self._module
                res = next((d for d in data if test(d)), None)
                if res:
                    return res[fmodel], res[fid]
                else:
                    test = lambda d: d[fmodel] == self._name
                    res = [(d[fmodel], d[fid]) for d in data if test(d)]
                    if not res:
                        res = [(d[fmodel], d[fid]) for d in data]
                    return res[0] if len(res) == 1 else res
    else:
        return bool(data)


def touch_fields(self, cr, uid, ids, only=None, context=None):
    '''Touches functional fields of the given `ids`.

    For each stored functional field the value is recalculated and stored.

    If `only` is set, it should be a list of fields to touch.  A single string
    is also valid.  Invalid (non-functional, or without a non-bool``store``)
    fields are silently ignored.

    If `ids` is empty, all items are touched.

    .. warning:: Don't rely in ids return from ``search()``.

       This function deals directly with the DB bypassing the ORM's
       ``write()`` method.  So you must provide ids as they are found in the
       DB.

       For instance, the ``crm_meeting`` returns many `str` IDs for each
       instance of a recurrent event though in the DB there's a single row.
       (Remember ``crm_meeting`` is actually the place for every event.)

    '''
    from xoutil.eight import iteritems, string_types
    from xoutil.names import nameof
    from xoutil.future.types import is_collection
    # FIX: This 'function' doesn't exist any more.
    from openerp.osv.fields import function
    if not ids:
        # Don't use self.search() here!  search() might return invalid ids
        # (crm.meeting does), and since _store_set_values bypasses write() and
        # executes SQL directly we must provide DB-level ids and not
        # model-levels ones.
        query = 'SELECT "id" FROM "%s"' % self._table
        cr.execute(query)
        ids = [row[0] for row in cr.fetchall()]
    if isinstance(only, string_types):
        only = (only, )
    if only is not None and not is_collection(only):
        msg = "Invalid type '%s' for argument 'only'"
        raise TypeError(msg % nameof(only, inner=True, typed=True))
    # TODO: use both _columns and _inherit_fields
    fields = [name for name, field in iteritems(self._columns)
              if not only or name in only
              if isinstance(field, function) and field.store]
    if fields:
        return self._store_set_values(
            cr, uid, ids, fields, dict(context or {})
        )


from xoeuf.osv.writers import ORMWriter as get_writer  # noqa
orm_writer = get_writer


from xoeuf.osv.writers import ORMCreator as get_creator  # noqa
orm_creator = get_creator


def cascade_search(self, cr, uid, *queries, **options):
    '''Perform a cascading search.

    Each `query` is tried in order until one returns non-empty.  The only
    keyword argument allowed is `context`.

    '''
    from collections import deque
    context = options.pop('context', {})
    if options:
        raise TypeError('Invalid keyword arguments %s' % options.popitem()[0])
    result = []
    queries = deque(queries)
    while not result and queries:
        query = queries.popleft()
        result = self.search(cr, uid, query, context=context)
    return result


def get_treeview_action(self, *args, **kwargs):
    '''Return the tree view action for `self`.

    There are two possible signatures:

    - ``get_treeview_action(recordset, **options)``

    - ``get_treeview_action(model, cr, uid, ids, context=context, **options)``

       .. warning:: ``context`` must be a keyword argument.

    If the recordset is a singleton, return the view type 'form' so that it's
    easier to see the full object.

    :rtype: An action `dict` you can return to the web client.

    `options` is used to override **almost any** key in the returned dict.  An
    interesting option is `target`.

    '''
    if args:
        (cr, uid, ids), args = args[:3], args[3:]
        if args:
            raise TypeError('Too many positional arguments')
        context = kwargs.pop('context', None)
    else:
        cr, uid, context = self.env.args
        ids = self.ids
    options = kwargs
    if not ids or len(ids) > 1:
        vtype = 'list'
        active_id = None
    else:
        vtype = 'form'
        active_id = ids[0]
    result = {
        'type': 'ir.actions.act_window',
        'res_model': self._name,
        'src_model': False,
        'view_id': False,
        'view_type': vtype,
        'view_mode': 'list,form',
        'views': [(False, 'list'), (False, 'form')],
        'target': 'current',
        'context': context,
    }
    if ids:
        result['domain'] = [('id', 'in', tuple(ids))]
    if active_id:
        result['active_id'] = active_id
    result.update(options)
    return result


del deprecated
