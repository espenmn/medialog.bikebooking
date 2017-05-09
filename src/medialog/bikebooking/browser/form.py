from Products.Five import BrowserView
from plone.directives import form

from zope import schema
from z3c.form import button
from plone.schema.email import Email

from plone import api
from Products.statusmessages.interfaces import IStatusMessage

from datetime import *
#from isoweek import Week
from email.mime.text import MIMEText
from email import message_from_string
import hashlib



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
            checksum = hashlib.sha224(data['email']).hexdigest()
            name = data['name']
            
            html = """\
                <html>
                  <head>
                  <style>.button {
                 border: none;
                 background: #777;
                 color: #fff;
                 padding: 10px;
                 display: inline-block;
                 margin: 10px 0px;
                 font-family: Helvetica, Arial, sans-serif;
                 -webkit-border-radius: 3px;
                 -moz-border-radius: 3px;
                 border-radius: 3px;
                 text-decoration: none;
                 }

                 .button:hover {
                 color: #fff;
                 background: #666;
                 }
                 </style>
                  </head>
                  <body>
                    <p>Hei, %(name)s<br><br>
                       <a class="button" href="%(url)s/@@confirm-form?email=%(email)s&name=%(name)s&checksum=%(checksum)s">Bekreft reserveringen</a><br><br><br>
                       <br/><hr /><br/>
                       <a href="%(url)s/@@confirm-form?email=%(email)s&name=%(name)s&checksum=%(checksum)s&bestille=0"> Hvis du senere trenger &aring; avbestille - klikk her</a>
                    </p>
                  </body>
                </html>
                """ % { 'name': name.encode('utf8'),
                         'email': email,
                         'url':  self.context.absolute_url(),
                         'checksum': checksum,
                    }
                    
            mailbody = MIMEText(html, 'html')
            api.portal.send_email(
                recipient=data['email'],
                subject="Sykkelreservasjon",
                body= mailbody,
                )
            IStatusMessage(self.request).addStatusMessage(
                u"En epost blir straks sendt deg. \n Bekreft reservasjonen snarest mulig", "info"
            )
            #contextURL = api.portal.get().absolute_url()
            #self.request.response.redirect(contextURL)
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
    
    def __call__(self, email="", name="", bestille="", checksum="nothing"):
        context = self.context
        #bestille = self.request.bestille
        #email  = self.request.email
        name   = self.request.name.encode('utf8') 
        if checksum == hashlib.sha224(email).hexdigest():
            if email.endswith('medialog.no') or email.endswith('asvg.no'):
                import pdb; pdb.set_trace()
                try:
                    if bestille == '0':
                        if self.in_dictlist('email', email):
                            self.context.person_pair.remove(self.in_dictlist('email', email))
                            api.portal.send_email(
                                recipient=data['email'],
                                subject="Sykkelreservasjon",
                                body=u'Din sykkelreservasjon har blitt fjernet',
                            )
                        IStatusMessage(self.request).addStatusMessage(
                            u"Din reservering er fjernet", "Info"
                        )
                        #with api.env.adopt_roles(['Manager']):
                        #api.content.transition(context, transition='reserver')
                        
                        #contextURL = api.portal.get().absolute_url()
                        #self.request.response.redirect(contextURL)
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
                        
                        #with api.env.adopt_roles(['Manager']):
                        #api.content.transition(context, transition='reserver')
                    
                        IStatusMessage(self.request).addStatusMessage(
                            u"Din reservasjon er bekreftet",
                            "info"
                        )
                    #contextURL = api.portal.get().absolute_url()
                    #self.request.response.redirect(contextURL)
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
         

        
    
    