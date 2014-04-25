#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoeuf.security
#----------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2014-04-24

'''Some tools to improve `OpenERP` security.


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from xoutil.crypto import (PASS_PHRASE_LEVEL_BASIC,
                           PASS_PHRASE_LEVEL_MAPPED,
                           PASS_PHRASE_LEVEL_MAPPED_MIXED,
                           PASS_PHRASE_LEVEL_MAPPED_DATED,
                           PASS_PHRASE_LEVEL_STRICT,
                           DEFAULT_PASS_PHRASE_LEVEL as _DEF_LEVEL)


def reset_all_passwords(db, security_level=_DEF_LEVEL, verbose=True):
    '''Reset all passwords in a data-base.

    :param db: `OpenERP` data-base cursor as defined in `xoeuf.pool`.

    :param security_level: Numerical security level (the bigger the more
           secure). This function uses `xoutil.crypto.generate_password` to
           generate new passwords, never use levels 0 or 1.

    :param verbose: If True, print every change password to ``stdout``.

    This function can be used as::

      >>> from xoeuf.pool import test as db
      >>> from xoeuf.security import reset_all_passwords
      >>> reset_all_passwords(db, security_level=2)

    '''
    from xoutil.crypto import generate_password
    uid = db.uid
    models = db.models
    users_model = models.res_users
    msg = ">>> id: %s, login: %s, password: '%s', name: %s"
    with db(transactional=True) as cr:
        ids = users_model.search(cr, uid, [])
        data = users_model.read(cr, uid, ids, fields=['name', 'login'])
        for item in data:
            id = item['id']
            login = item['login']
            password = generate_password(login, security_level)
            vals = {'id': id, 'password': password}
            if users_model.write(cr, uid, [id], vals):
                if verbose:
                    print(msg % (id, login, password, item['name']))
            else:
                info = msg % (id, login, password, item['name'])
                print('Error setting password for', info)


def reset_invalid_passwords(db, security_level=_DEF_LEVEL):
    '''Reset all invalid passwords in a data-base.

    :param db: `OpenERP` data-base cursor as defined in `xoeuf.pool`.

    :param security_level: Numerical security level (the bigger the more
           secure). This function uses `xoutil.crypto.generate_password` to
           generate new passwords, never use levels 0 or 1.

    An invalid password is when it is the same as login name. Print
    information about all users with invalid passwords.

    This function can be used as::

      >>> from xoeuf.pool import test as db
      >>> from xoeuf.security import reset_invalid_passwords
      >>> reset_invalid_passwords(db)

    '''
    from xoutil.crypto import generate_password
    from openerp.exceptions import AccessDenied
    uid = db.uid
    users_model = db.models.res_users
    msg = ">>> id: %s, login: %s, password: '%s', name: %s"
    with db(transactional=True) as cr:
        ids = users_model.search(cr, uid, [])
        data = users_model.read(cr, uid, ids, fields=['name', 'login'])
        for item in data:
            id = item['id']
            login = item['login']
            try:
                users_model.check_credentials(cr, id, login)
                password = generate_password(login, security_level)
                vals = {'id': item['id'], 'password': password}
                info = msg % (id, login, password, item['name'])
                if not users_model.write(cr, uid, [id], vals):
                    info = 'Error setting password for ' + info
                print(info)
            except AccessDenied:
                pass
            except Exception as error:
                info = msg % (id, login, password, item['name'])
                print(">>> ERROR: %s :: %s" % (error, info))

# TODO: See ``/openerp/service/security.py``
