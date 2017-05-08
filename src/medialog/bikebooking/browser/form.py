from Products.Five import BrowserView
from plone.directives import form

from zope import schema
from z3c.form import button
from plone.schema.email import Email

from plone import api
from Products.statusmessages.interfaces import IStatusMessage

from datetime import *
#from isoweek import Week




class IBookingForm(form.Schema):
    """ Define form fields """

    name = schema.TextLine(
            title=u"Navn",
        )
        
    email =  Email(
            title=u"Epost",
        )
    


class BookingForm(form.SchemaForm):
    """ Define Form handling

    """

    schema = IBookingForm
    ignoreContext = True
    
    #uke = datetime.today().isocalendar()[1]

    label = u"Reserver sykkel"
    description = u"Reserver sykkel " 
    
    #+  context.uke + "Dvs: mandag " 
    #Week(2011, 40).monday()
    
    
    
    @button.buttonAndHandler(u'Reserver')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if data['email'].endswith('medialog.no') or data['email'].endswith('asvg.no'):
            email = data['email']
            name = data['name']
            id = self.context.id
            mailbody = 'Hei, ' + name + '\n' +  u'Vennligst klikk lenken og bekreft reserveringen' + '\n' +  self.context.absolute_url() + '/@@confirm-form?email=' + email + "&name=" + name.encode('utf8') \
             + u'\n\n\n For senere fjerning av reserveringen, klikk her \n' +  self.context.absolute_url() + '/@@confirm-form?email=' + email + "&name=" + name.encode('utf8') + '&bestille=0'
            api.portal.send_email(
                recipient=data['email'],
                subject="Sykkelreservasjon",
                body=mailbody.encode('utf8'),
                )
            IStatusMessage(self.request).addStatusMessage(
                u"En epost blir straks sendt deg. \n Bekreft reservasjonen snarest mulig", "info"
            )
            contextURL = api.portal.get().absolute_url()
            self.request.response.redirect(contextURL)
        else: 
            self.status = "Kun personer med asvg.no epost kan reservere sykler"
        
        
    @button.buttonAndHandler(u"Avbryt")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the page.
        """
        
        
class ConfirmForm(BrowserView):
    """
    Email confirm page

    """

    label = u"Bekreft Reservasjon av sykkel"
    
    
    def in_dictlist(self, key, value):
        for this in self.context.person_pair:
            if this[key] == value:
                return this
        return False
    
    def __call__(self, email="", name="", bestille=""):
        context = self.context
        #bestille = self.request.bestille
        email  = self.request.email
        name   = self.request.name.encode('utf8') 
        if email.endswith('medialog.no') or email.endswith('asvg.no'):
            try:
                if bestille == '0':
                    self.context.person_pair.remove(self.in_dictlist('email', email))
                    api.portal.send_email(
                        recipient=data['email'],
                        subject="Sykkelreservasjon",
                        body=u'Din sykkelreservasjon har blitt fjernet',
                    )
                    IStatusMessage(self.request).addStatusMessage(
                    u"Din reservering er fjernet",
                    "Info"
                    )
                    contextURL = api.portal.get().absolute_url()
                    self.request.response.redirect(contextURL)
                elif len(context.person_pair) >= context.bikes:
                    IStatusMessage(self.request).addStatusMessage(
                    u"Alle sykler er reservert",
                    "Info"
                    )
                    contextURL = api.portal.get().absolute_url()
                    self.request.response.redirect(contextURL)
                else:
                    if not self.in_dictlist('email', email):
                        self.context.person_pair.append({'name': name, 'email': email})
                    
                    #   with api.env.adopt_roles(['Manager']):
                    #   api.content.transition(context, transition='reserver')
                    
                    IStatusMessage(self.request).addStatusMessage(
                        u"Din reservasjon er bekreftet",
                        "info"
                    )
                contextURL = api.portal.get().absolute_url()
                self.request.response.redirect(contextURL)
            except:
                self.status = "Noe gikk gale med reservasjonen"
        else: 
            self.status = "Noe gikk gale med reservasjonen"
    
    
class BikesView(BrowserView):
    """
    Show avalable bikes

    """

    #def bikes(self):
    #    return len(self.context.person_pair) < self.context.bikes
         

        
    
    