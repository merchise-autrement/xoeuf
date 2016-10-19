==========================================================
 `xoeuf.osv.fields`:mod: -- Extensions to the Odoo fields
==========================================================

.. module:: xoeuf.osv.fields

.. class:: localized_datetime

   A field for localized datetimes.

   Localized datetimes are actually a functional field that takes two
   underlying columns a datetime and timezone name.

   :param dt: The name of the column where the datetime (in UTC) is actually
              saved.

   :param tzone: The name of the column where the timezone where the event
                 should be presented to the user.

   Upon reading, we assume the user's timezone is properly set.

   The datetime column will be actually saved in UTC as all datetimes in Odoo.
   But upon reading we convert to a properly shifted datetime so that is
   presented to the user in the saved time zone.

   .. note:: At the time this field is read-only, not searchable, and
             non-storable.
