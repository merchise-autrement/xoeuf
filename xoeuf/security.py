#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoeuf.security
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016,  Merchise and Contributors
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2014-04-24

'''Some tools to improve `OpenERP` security.

- :func:`reset_all_passwords`: to reset all passwords in a data-base.

- :func:`reset_invalid_passwords`: to reset all invalid passwords in a
  data-base.

Previous two functions uses `xoutil.crypto.generate_password` to generate new
passwords using as `pass_phrase` the user login, `level` means a generation
method.  Each level implies all other with an inferior numerical value.  See
`xoutil.crypto.generate_password` for more information about defined
constants of security level.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.crypto import (PASS_PHRASE_LEVEL_BASIC,  # noqa
                           PASS_PHRASE_LEVEL_MAPPED,
                           PASS_PHRASE_LEVEL_MAPPED_MIXED,
                           PASS_PHRASE_LEVEL_MAPPED_DATED,
                           PASS_PHRASE_LEVEL_STRICT,
                           DEFAULT_PASS_PHRASE_LEVEL as _DEF_LEVEL)


from xoutil.names import strlist as strs
__all__ = strs('PASS_PHRASE_LEVEL_BASIC',
               'PASS_PHRASE_LEVEL_MAPPED',
               'PASS_PHRASE_LEVEL_MAPPED_MIXED',
               'PASS_PHRASE_LEVEL_MAPPED_DATED',
               'PASS_PHRASE_LEVEL_STRICT',
               'reset_all_passwords',
               'reset_invalid_passwords')
del strs


def _reset_passwords(db, security_level, verbose, check=None):
    '''Internal module function to reset passwords in a data-base.

    This function is used by :func:`reset_all_passwords` and
    :func:`reset_invalid_passwords` functions.

      :param db: `OpenERP` data-base as defined in `xoeuf.pool`.

      :param security_level: Numerical security level (the bigger the more
             secure).

      :param verbose: If True, print to ``stdout`` information of every
             password change.

      :param check: A function that checks if for a given user the password
             must be changed or not (if not given, is equivalent for True to
             all users).  It must has following definition::

               def check(self, cr, id, login):

             Where `self` is the ``res.users`` model, `cr` the active
             data-base cursor, `id` the user data-base id to check, and
             `login` the user login identifier.

    '''
    from xoutil.objects import smart_copy
    from xoutil.crypto import generate_password
    from xoutil.string import safe_encode
    uid = db.uid
    users_model = db.models.res_users
    with db(transactional=True) as cr:
        ids = users_model.search(cr, uid, [])
        data = users_model.read(cr, uid, ids, fields=['name', 'login'])
        for item in data:
            login = item['login']
            if check is None or check(users_model, cr, item['id'], login):
                item['password'] = generate_password(login, security_level)
                vals = smart_copy(item, {}, defaults=('id', 'password'))
                if users_model.write(cr, uid, item['id'], vals):
                    if verbose:
                        print(safe_encode(">>> id: %(id)s, login: %(login)s, "
                                          "name: %(name)s, "
                                          "password: '%(password)s'" % item))
                else:
                    print(safe_encode(
                        "<<< ERROR: id: %(id)s, login: %(login)s, "
                        "name: %(name)s, " % item
                    ), "NOT CHANGED")


def reset_all_passwords(db, security_level=_DEF_LEVEL, verbose=True):
    '''Reset all passwords in a data-base.

    :param db: `OpenERP` data-base cursor as defined in `xoeuf.pool`.

    :param security_level: Numerical security level (the bigger the more
           secure).

    :param verbose: If True, print every change password to ``stdout``.

    This function can be used as::

      from xoeuf.pool import test as db
      from xoeuf.security import reset_all_passwords
      reset_all_passwords(db, security_level=2)

    See module documentation for more info.

    '''
    _reset_passwords(db, security_level, verbose)


def reset_invalid_passwords(db, security_level=_DEF_LEVEL):
    '''Reset all invalid passwords in a data-base.

    :param db: `OpenERP` data-base cursor as defined in `xoeuf.pool`.

    :param security_level: Numerical security level (the bigger the more
           secure).

    An invalid password is when it is the same as login name. Print
    information about all users with invalid passwords.

    This function can be used as::

      from xoeuf.pool import test as db
      from xoeuf.security import reset_invalid_passwords
      reset_invalid_passwords(db)

    See module documentation for more info.

    '''
    def check(self, cr, id, login):
        from openerp.exceptions import AccessDenied
        try:
            self.check_credentials(cr, id, login)
            return True
        except AccessDenied:
            return False
    _reset_passwords(db, security_level, True, check)
