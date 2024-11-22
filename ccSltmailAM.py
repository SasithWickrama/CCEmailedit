from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from string import Template
import smtplib
import db
from log import getLogger
import re

conn = db.DbConnection.dbconnHadwh("")

#logger = getLogger('email', 'logs/sltemail')

sql='select * from CREDIT_CONTROL_EMAIL_AM where stat is null'
c = conn.cursor()
c.execute(sql)

logger = getLogger('email', 'logs/sltemail')

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)
    
def checkMail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return 0
    else:
        return 1   

message_template = read_template('files/notifywithAM.txt')

for row in c:
    account, email,amount,accountmanager,amemail ,stat = row
    
    messagestr = message_template.substitute(ACCOUNT_NUM=account, EMAIL=email,ACCOUNTMANAGER= accountmanager, AMEMAIL=amemail )
    
    
    
    smtp_ssl_host = '124.43.129.50'
    smtp_ssl_port = 25
    from_addr = 'sltbillcc@slt.lk'
    to_addrs = [email]
    sub = 'Bill delivery mode conversion to E-statement '
    
    try:
        message = MIMEMultipart('related')
        message['subject'] = sub
        message['from'] = from_addr
        message['to'] = ', '.join(to_addrs)
        message.preamble = 'This is a multi-part message in MIME format.'
        
        msgAlternative = MIMEMultipart('alternative')
        message.attach(msgAlternative)

        msgText = MIMEText('This is the alternative plain text message.')
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        #msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!', 'html')
        msgText = MIMEText(messagestr, 'html')
        msgAlternative.attach(msgText)

        # This example assumes the image is in the current directory
        fp = open('mailsig.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        message.attach(msgImage)
        
        server = smtplib.SMTP(smtp_ssl_host, smtp_ssl_port)
        
        if checkMail(email) == 0:
            server.sendmail(from_addr, email, message.as_string())
            
            logger.info(email)
            logger.info('mail sent.....')
            print('mail sent.....')
            logger.info('========================================================================================')
            
            server.quit()
            
            sql2="update CREDIT_CONTROL_EMAIL_AM set STAT=:STAT where  EMAIL_NAME =:EMAIL_NAME and ACCOUNT_NO=:ACCOUNT_NO and stat is null"
            with conn.cursor() as cursor3:
                cursor3.execute(sql2,["10",email,account])
                conn.commit()
                print(cursor3.rowcount)
        else:
            logger.info(email)
            logger.info('Invalid mail.....')
            print('Invalid mail.....')
            logger.info('========================================================================================')
            sql2="update CREDIT_CONTROL_EMAIL_AM set STAT=:STAT where  EMAIL_NAME =:EMAIL_NAME and ACCOUNT_NO=:ACCOUNT_NO and stat is null"
            with conn.cursor() as cursor3:
                cursor3.execute(sql2,["30",email,account])
                conn.commit()
                print(cursor3.rowcount)
            
    except Exception as e:
        print(e)
        logger.info(e)
        logger.info('========================================================================================')