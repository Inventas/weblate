.. _apple:
.. _strings:

Apple iOS strings
-----------------

.. index::
    pair: Apple strings; file format

File format typically used for translating Apple :index:`iOS <pair: iOS;
translation>` applications, but also standardized by PWG 5100.13 and used on
NeXTSTEP/OpenSTEP.

Apple iOS strings are usually used as monolingual.

.. seealso::

   * :ref:`stringsdict`
   * `Apple "strings files" documentation <https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPInternational/MaintaingYourOwnStringsFiles/MaintaingYourOwnStringsFiles.html>`_
   * `Message Catalog File Format in PWG 5100.13 <https://ftp.pwg.org/pub/pwg/candidates/cs-ippjobprinterext3v10-20120727-5100.13.pdf#page=66>`_
   * :doc:`tt:formats/strings`

.. include:: /snippets/format-features/strings-features.rst

Weblate configuration
+++++++++++++++++++++

+-------------------------------------------------------------------------------+
| Typical Weblate :ref:`component`                                              |
+================================+==============================================+
| File mask                      |``Resources/*.lproj/Localizable.strings``     |
+--------------------------------+----------------------------------------------+
| Monolingual base language file |``Resources/en.lproj/Localizable.strings`` or |
|                                |``Resources/Base.lproj/Localizable.strings``  |
+--------------------------------+----------------------------------------------+
| Template for new translations  | `Empty`                                      |
+--------------------------------+----------------------------------------------+
| File format                    | `iOS Strings`                                |
+--------------------------------+----------------------------------------------+
| File encoding                  | `UTF-8`                                      |
+--------------------------------+----------------------------------------------+

.. _xcstrings:

Apple String Catalog
--------------------

.. index::
    pair: Apple String Catalog; file format
    pair: xcstrings; file format

Apple String Catalog files store the source language and all localizations in
one ``.xcstrings`` catalog file. Configure the component file mask to point to
the catalog file directly, without a language placeholder.

.. seealso::

   * `Localizing and varying text with a string catalog <https://developer.apple.com/documentation/xcode/localizing-and-varying-text-with-a-string-catalog>`_

Weblate configuration
+++++++++++++++++++++

+--------------------------------+----------------------------------------------+
| Typical Weblate :ref:`component`                                              |
+================================+==============================================+
| File mask                      |``Resources/Localizable.xcstrings``           |
+--------------------------------+----------------------------------------------+
| Monolingual base language file | `Empty`                                      |
+--------------------------------+----------------------------------------------+
| Template for new translations  | `Empty`                                      |
+--------------------------------+----------------------------------------------+
| File format                    | `Apple String Catalog`                       |
+--------------------------------+----------------------------------------------+
