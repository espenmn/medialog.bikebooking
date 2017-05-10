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
from zope.lifecycleevent import modified
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides






class IBookingForm(form.Schema):
    """ Define form fields """

    name = schema.TextLine(
            title=u"Navn",
        )
    
    klasse = schema.TextLine(
            title=u"Klasse",
        )
        
    email =  Email(
            title=u"Epost",
        )
    mobil = schema.TextLine(
            title=u"Mobil",
        )
    


class BookingForm(form.SchemaForm):
    """ Define Form handling

    """

    schema = IBookingForm
    ignoreContext = True
    
    #uke = datetime.today().isocalendar()[1]

    label = u"Reserver sykkel"
    description = u"Hvis du nylig har har hatt sykkel kan du kun reservere samme dag. " 
    
    #+  context.uke + "Dvs: mandag " 
    #Week(2011, 40).monday()
    
    
    def in_dictlist(self, key, value):
    
        if self.context.pickup_date <= datetime.today().date():
            return False
        
        catalog = api.portal.get_tool(name='portal_catalog')
        all_weeks = catalog(portal_type='uke')
        
        
        for brain in all_weeks:
            #index is not working properly, not sure why
            for pair in brain.getObject().person_pair:
                #print pair
                if pair[key] == value:
                    return True
        return False
    
    @button.buttonAndHandler(u'Reserver')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        if  not self.in_dictlist('email', data['email']):
            if data['email'].endswith('medialog.no') or data['email'].endswith('asvg.no'):
                email = data['email']
                checksum = hashlib.sha224(data['email']).hexdigest()
                name = data['name'].encode('utf8')
                klasse = data['klasse'].encode('utf8')
                mobil = data['mobil'].encode('utf8')
            
            
                html = """\
                    <html>
                      <head>
                      <style>
                      .button.avbestille {background: #c8222c;}
                      .button {
                     border: none;
                     background: #68c831;
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
                           <a class="button" href="%(url)s/@@confirm-form?email=%(email)s&name=%(name)s&mobil=%(mobil)s&klasse=%(klasse)s&checksum=%(checksum)s">Bekreft reserveringen</a><br><br><br>
                           Husk &aring; lese info her: <a href="http://sykkel.asvg.no/rutiner-for-utlan">Rutiner for utl&aring;n</a><br/>
                           <a class="button avbestille" href="%(url)s/@@confirm-form?email=%(email)s&name=%(name)s&mobil=%(mobil)s&klasse=%(klasse)s&checksum=%(checksum)s&bestille=0">Avbestille</a>
                        <br><br/></p>
                      </body>
                    </html>
                    """ % { 'name': name,
                             'email': email,
                             'url':  self.context.absolute_url(),
                             'checksum': checksum,
                             'klasse' : klasse,
                             'mobil': mobil,
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
            IStatusMessage(self.request).addStatusMessage(
                    u"Kun personer med asvg.no epost som ikke har reserver tidligere kan reservere sykler", "warning"
            )

        
    @button.buttonAndHandler(u"Avbryt")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the page.
        """
alsoProvides(BookingForm, IDisableCSRFProtection)

   
class ConfirmForm(BrowserView):
    """
    Email confirm page

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
          
    #label = u"Bekreft Reservasjon av sykkel"
    index = ViewPageTemplateFile("confirm_view.pt")
    
    
    def __call__(self, email="", name="", bestille="", checksum="nothing", klasse="", mobil=""):
        return self.render(email=email, name=name, bestille=bestille, checksum=checksum, klasse=klasse, mobil=mobil)
    
    def in_dictlist(self, key, value):
        
        #if nobody booked it, let users that has booked before book
        if self.context.pickup_date <= datetime.today().date():
            return False
        
        catalog = api.portal.get_tool(name='portal_catalog')
        all_weeks = catalog(portal_type='uke')

        for brain in all_weeks:
            #index is not working properly, not sure why
            for pair in brain.getObject().person_pair:
                #print brain.person_pair
                if pair[key] == value:
                    return pair
        return False
    
    def render(self, email="", name="", bestille="", checksum="nothing", klasse="", mobil=""):
        context = self.context
        #email  = email.decode('utf8') 
        #klasse = klasse.decode('utf8')
        #mobil = mobil.decode('utf8')
        #name   = name.decode('utf8'
        if checksum == hashlib.sha224(email).hexdigest():
            if email.endswith('medialog.no') or email.endswith('asvg.no'):
                try:
                    if bestille == '0':
                        if self.in_dictlist('email', email):
                            self.context.person_pair.remove(self.in_dictlist('email', email))
                            api.portal.send_email(
                                recipient=email,
                                subject="Sykkelreservasjon",
                                body=u'Din sykkelreservasjon har blitt fjernet',
                            )
                        IStatusMessage(self.request).addStatusMessage(
                            u"Din reservering er fjernet", "info"
                        )
                        #with api.env.adopt_roles(['Manager']):
                        #api.content.transition(context, transition='reserver')
                        
                    elif len(context.person_pair) >= context.bikes:
                        IStatusMessage(self.request).addStatusMessage(
                            u"Alle sykler er reservert",
                            "info"
                        )
                    elif self.in_dictlist('email', email):
                        IStatusMessage(self.request).addStatusMessage(
                            u"Du har reservert sykkel tidligere....",
                            "info"
                        )
                    else:
                        if not self.in_dictlist('email', email):
                            self.context.person_pair.append({'name': name, 'email': email, 'klasse': klasse, 'mobil': mobil})
                        
                        #with api.env.adopt_roles(['Manager']):
                        #api.content.transition(context, transition='reserver')
                    
                        IStatusMessage(self.request).addStatusMessage(
                            u"Din reservasjon er bekreftet",
                            "info"
                        )
                    
                except:
                    IStatusMessage(self.request).addStatusMessage(
                            u"Noe gikk gale med reservasjonen",
                            "warning"
                    )
                
                modified(context)
                return self.index()

        else: 
            IStatusMessage(self.request).addStatusMessage(
                            u"Noe gikk gale med reservasjonen",
                            "warning"
            )
            return self.index()
    
alsoProvides(ConfirmForm, IDisableCSRFProtection)
    
class BikesView(BrowserView):
    """
    Show avalable bikes

    """

    #def bikes(self):
    #    return len(self.context.person_pair) < self.context.bikes
    
    def user(self):
     return api.user.get_current()
         

        
    
    