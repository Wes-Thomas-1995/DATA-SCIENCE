from datetime import datetime, timedelta, date
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import email, smtplib, ssl
import os




class EMAIL():

    def __init__(self, TRADE_VALUE, PROFIT):

        self.TRADE_VALUE = TRADE_VALUE
        self.PROFIT      = PROFIT
        self.EMAIL()



    def EMAIL(self):

        
        DATETIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        
        
        mail_content = '''Good Morning Wes, 
    The Current Datetime is  {} 
    The Amount Trade Value is {}
    The Profit From Last Trade is {}
        

    Kind Regards,
    ENKI Technology Ltd.
        
        
        ''' .format(DATETIME, self.TRADE_VALUE, self.PROFIT)
        
        #The mail addresses and password 
        sender_address          = 'XXXXX'
        sender_pass             = 'XXXXX' 
        receiver                = ['XXXXX']
        email_subject           = 'Portfolio Performance Analysis - ' + date.today().strftime("%Y-%m-%d")

        
        
        for y in range(len(receiver)):
            receiver_address        = receiver[y]
            message                 = MIMEMultipart() 
            message['From']         = sender_address 
            message['To']           = receiver_address 
            message['Subject']      = email_subject


            message.attach(MIMEText(mail_content, 'plain')) 

            
            
            
            #Create SMTP session for sending the mail 
            session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port 
            session.starttls() #enable security 
            session.login(sender_address, sender_pass) #login with mail_id and password 
            text = message.as_string() 
            session.sendmail(sender_address, receiver_address, text) 
            session.quit() 

        return 




