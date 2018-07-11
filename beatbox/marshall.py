from _beatbox import _tSObjectNS
from types import ListType, TupleType
import datetime
import python_client
import re


dateregx = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
datetimeregx = re.compile(
    r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d+)(.*)')

doubleregx = re.compile(r'^(\d)+(\.\d+)?$')

stringtypes = (
    'string', 'id', 'phone', 'url', 'email',
    'anyType', 'picklist', 'reference', 'encryptedstring')

texttypes = ('textarea')

doubletypes = ('double', 'currency', 'percent')

multitypes = ('combobox', 'multipicklist')


_marshallers = dict()


def marshall(fieldtype, fieldname, xml, ns=_tSObjectNS):
    m = _marshallers[fieldtype]
    return m(fieldname, xml, ns)


def register(fieldtypes, func):
    if type(fieldtypes) not in (ListType, TupleType):
        fieldtypes = [fieldtypes]
    for t in fieldtypes:
        _marshallers[t] = func


def stringMarshaller(fieldname, xml, ns):
    return str(xml[getattr(ns, fieldname)])
register(stringtypes, stringMarshaller)


def textMarshaller(fieldname, xml, ns):
    # Avoid removal of newlines.
    node = xml[getattr(ns, fieldname)]
    text = ''
    for x in node._dir:
        text += unicode(x)
    return text.encode('utf-8')
register(texttypes, textMarshaller)


def multiMarshaller(fieldname, xml, ns):
    asString = str(xml[getattr(ns, fieldname):][0])
    if not asString:
        return []
    return asString.split(';')
register(multitypes, multiMarshaller)


def booleanMarshaller(fieldname, xml, ns):
    return python_client._bool(xml[getattr(ns, fieldname)])
register('boolean', booleanMarshaller)


def integerMarshaller(fieldname, xml, ns):
    strVal = str(xml[getattr(ns, fieldname)])
    try:
        i = int(strVal)
        return i
    except:
        return None
register('int', integerMarshaller)


def doubleMarshaller(fieldname, xml, ns):
    strVal = str(xml[getattr(ns, fieldname)])
    try:
        i = float(strVal)
        return i
    except:
        return None
register(doubletypes, doubleMarshaller)


def dateMarshaller(fieldname, xml, ns):
    datestr = str(xml[getattr(ns, fieldname)])
    match = dateregx.match(datestr)
    if match:
        grps = match.groups()
        year = int(grps[0])
        month = int(grps[1])
        day = int(grps[2])
        return datetime.date(year, month, day)
    return None
register('date', dateMarshaller)


def dateTimeMarshaller(fieldname, xml, ns):
    datetimestr = str(xml[getattr(ns, fieldname)])
    match = datetimeregx.match(datetimestr)
    if match:
        grps = match.groups()
        year = int(grps[0])
        month = int(grps[1])
        day = int(grps[2])
        hour = int(grps[3])
        minute = int(grps[4])
        second = int(grps[5])
        secfrac = float(grps[6])
        microsecond = int(secfrac * (10**6))
        return datetime.datetime(
            year, month, day, hour, minute, second, microsecond)
    return None
register('datetime', dateTimeMarshaller)


def base64Marshaller(fieldname, xml, ns):
    return str(xml[getattr(ns, fieldname)])
register('base64', base64Marshaller)
