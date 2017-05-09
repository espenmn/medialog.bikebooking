from zope import schema
from zope.interface import Interface
from zope.interface import implements
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides
from zope.i18nmessageid import MessageFactory
#from z3c.form import interfaces

from collective.z3cform.datagridfield import DataGridFieldFactory 
from collective.z3cform.datagridfield import DictRow

from zope.i18nmessageid import MessageFactory


_ = MessageFactory('medialog.bikebooking')



class IPerson(form.Schema):
    name = schema.TextLine(
        title=_(u'Navn', 'name'),
        required=True,
    )

    email = schema.TextLine(
        title=_(u'Epost', 'email'),
        required=True,
    )


class IBikeBookingBehavior(form.Schema):
    """ Persons booking"""
    
    
    bikes = schema.Int(
        title = _("Antall sykler", default=u"Antall sykler"),
        required = True,
        description = _("help_bikes",
                      default="Hvor mange sykler"),
        default=10,
    )
    
    pickup_date = schema.DateTime(
        title = _("Hentedato", default=u"Hentedato"),
    )

    form.widget(person_pair=DataGridFieldFactory)
    person_pair = schema.List(
        title = _(u"person_pair", 
            default=u"navn epost par"),
        value_type=DictRow(schema=IPerson),
        required= False,
    )

alsoProvides(IBikeBookingBehavior, IFormFieldProvider)

