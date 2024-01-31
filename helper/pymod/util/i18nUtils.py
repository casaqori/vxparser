"""
i18nUtils
=========

Module for handling internationalization in Python programs

Copyright (c) 2020 Tom Arn, www.t-arn.com

For suggestions and questions:
<sw@t-arn.com>

This file is distributed under the terms of the MIT license
"""

import i18n
import locale
from pathlib import Path


class I18nUtils:
    version = '0.3'
    version_date = '2020-07-03 - 2020-10-20'
    fallback_lang = None
    lang = None
    translation_dir = None

    def __init__(self, translation_dir, fallback_lang, lang=None):
        """
        Initializes the class and loads the translation files

        :param str translation_dir: The path to the directory containing the translation files in the format xx.yml
                                   where xx is the language, e.g. en.yml
        :param str fallback_lang: The language to be used if the chosen language is not available
        :param str lang: The language to use. Defaults to self.get_default_app_language()
        """
        self.translation_dir = translation_dir
        self.fallback_lang = fallback_lang
        if lang is None:
            self.lang = self.get_default_app_language()
        else:
            self.lang = lang
        self.load_i18n(translation_dir)
    # __init__

    def get_app_languages(self):
        """
        Returns a list of languages supported by the app

        :returns: The languages for which there are translation files
        :rtype: list[str]
        """
        _languages = []
        _p = Path(self.translation_dir)
        for _child in _p.iterdir():
            if _child.name.endswith('.yml'):
                _languages.append(_child.stem)
        # for
        return _languages
    # get_app_languages

    @staticmethod
    def get_default_system_language():
        """
        Returns the default language of the system
        or 'en' when default language cannot be determined

        :returns: The default language of the system or 'en'
        :rtype: str
        """
        lang = 'en'
        default_locale = locale.getdefaultlocale()
        if default_locale is not None:
            lang = default_locale[0][0:2]
        return lang
    # get_default_system_language

    def get_default_app_language(self):
        """
        Returns the default language of the app.

        :returns: get_default_system_language() if it is
        in get_app_languages(). Otherwise, it will return self.fallbackLang
        :rtype: str
        """
        def_lang = I18nUtils.get_default_system_language()
        if def_lang not in self.get_app_languages():
            def_lang = self.fallback_lang
        return def_lang
    # get_default_app_language

    def get_error_translation(self, text):
        """
        Returns the translation of the error text or the original error text
        To translate error texts, remove all '.' in the message, prefix it with 'python.error.' and use this as the
        key, e.g. python.error.factorial() not defined for negative values: factorial() ist nicht definiert für
        negative Werte

        :param str text: The error text
        :returns: The translated error text if found. Otherwise the original error text
        :rtype: str
        """
        _key = text.replace('.', '')
        _key = 'python.error.' + _key
        _trans = self.t(_key)
        if _trans != _key:
            return _trans
        else:
            return text
    # get_error_translation

    def load_i18n(self, dir_name=''):
        """
        Loads the translation files from the passed directory or (when not passed) from
        the default translation directory which is in __init__
        The translation files must be named xx.yml where xx is the language code, e.g. en.yml

        :param str dir_name: The path to the directory with the translation files
        """
        if dir_name == '':
            dir_name = self.translation_dir
        i18n.set('skip_locale_root_data', True)
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('enable_memoization', True)
        i18n.set('locale', self.lang)
        i18n.set('fallback', self.fallback_lang)
        i18n.load_path.append(dir_name)
    # load_i18n

    @staticmethod
    def t(key, **kwargs):
        """
        Gets the translation for the passed text key
        If the key cannot be found in the set language, the key
        itself will be returned

        :param str key: The key for text
        :param int kwargs: locale chooses a specifc locale, count is used for pluralization of the text: 0 will choose the 'zero' element, 1 the 'one' element, 2 or greater
                      will choose the 'many' element of the translated text. Pass -1 if you want to get the complete dictionary back
        :returns: Returns the translated text or the key itself when no translation was found
        :rtype: str
        """
        _text = i18n.t(key, **kwargs)
        if _text == '':
            _text = key
        if _text.startswith('{') and _text.endswith('}'):
            # fix for BabelEdit not supporting dictionaries and python-i18n not supporting
            # dictionaries formatted as strings
            _dict = eval(_text)
            if kwargs['count'] == -1:
                pass  # return the dictionary
            elif kwargs['count'] == 0:
                _text = _dict['zero']
            elif kwargs['count'] == 1:
                _text = _dict['one']
            else:
                _text = _dict['many']
        return _text
    # t
# I18nUtils
