from Products.Five import BrowserView
from plone.directives import form

from zope import schema
from z3c.form import button
from plone.schema.email import Email

from plone import api
from Products.statusmessages.interfaces import IStatusMessage

from datetime import *


#from AccessControl import ClassSecurityInfo, getSecurityManager
#from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
#from AccessControl.User import nobody
#from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser



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
    
    uke = datetime.today().isocalendar()[1]

    label = u"Reserver sykkel"
    description = u"Reserver sykkel for <b>neste</b> uke. Dvs. Ukenummmer: " +  str(uke)
    
    
    
    @button.buttonAndHandler(u'Reserver')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if data['email'].endswith('medialog.no') or data['email'].endswith('asvg.no'):
            email = data['email']
            name = data['name']
            self.context.email = email
            self.context.navn = name
            self.context.dato = datetime.now()
            id = self.context.id
            mailbody = 'Hei, ' + name + '\n' +  u'Vennligst klikk lenken og bekreft reserveringen' + '\n' +  self.context.absolute_url() + '/@@confirm-form?reservasjon=' + email
            api.portal.send_email(
                recipient=data['email'],
                subject="Sykkelreservasjon",
                body=mailbody,
                )
            IStatusMessage(self.request).addStatusMessage(
                u"En epost blir straks sendt deg. \n Bekreft reservasjonen innen 15 minutter", "info"
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

    
    def __call__(self, reservation=None):
        context = self.context
        epost = self.request.reservasjon
        description = context.email
    
        if self.context.email == epost:
            try:
                with api.env.adopt_roles(['Manager']):
                    api.content.transition(context, transition='reserver')
                ##context.reindexObject()
                IStatusMessage(self.request).addStatusMessage(
                    u"Din reservasjon er bekreftet",
                    "info"
                )
                contextURL = api.portal.get().absolute_url()
                #self.context.absolute_url() + '/content_status_modify?workflow_action=reserver'
                self.request.response.redirect(contextURL)
            except:
                self.status = "Noe gikk gale med reservasjonen"
        else: 
            self.status = "Noe gikk gale med reservasjonen"
    
    
class BikesView(BrowserView):
    """
    Show avalable bikes

    """

    def righttime(self):
        return datetime.now() - timedelta(minutes=15)
        
    
    