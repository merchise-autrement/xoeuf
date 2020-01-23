#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from odoo.fields import Html as Base
from lxml import html
from lxml.etree import XMLSyntaxError


class Html(Base):
    def extract_text(self_or_cls, record_or_value):
        """Extract plain text from an HTML field.

        The Odoo HTML field stores it's empty value as '<p><br/></p>' so to check
        it's emptiness we must try to extract the valid plain text if any.

        If given value cannot be parsed, return None.

        """
        value = self_or_cls._get_html_value(record_or_value)
        if value:
            try:
                texts = html.fromstring(value).xpath("//text()")
                if texts:
                    return " ".join(texts)
            except XMLSyntaxError:
                return None
        else:
            return ""

    def is_plain_text_empty(self_or_cls, record_or_value, raises=False):
        """Return True if the plain text of HTML value is empty.

        If `raises` is False and the value is not valid (i.e
        `Html.extract_text`:method: returns None), return None.  If `raises`
        is True, raise a ValueError.

        """
        res = self_or_cls.extract_text(record_or_value)
        if res is None:
            if raises:
                raise ValueError(self_or_cls._get_html_text(record_or_value))
            else:
                return None
        return not res.strip()

    def _get_html_value(self_or_cls, record_or_value):
        if isinstance(self_or_cls, type) and issubclass(self_or_cls, Base):
            return record_or_value
        else:
            return record_or_value[self_or_cls.name]
