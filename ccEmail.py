# import necessary packages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from string import Template

from log import getLogger

logger = getLogger('email', 'logs/email')

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def get_contacts(filename):
    email = []
    date = []
    account = []
    amount = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            email.append(a_contact.split()[0])
            date.append(a_contact.split()[1])
            account.append(a_contact.split()[2])
            amount.append(a_contact.split()[3])
    return email,date, account,amount


# For each contact, send the email:

# s = smtplib.SMTP(host='124.43.129.50', port=25)
# s.starttls()
# s.login('sltbillcc@slt.lk', 'wYS#qa?MP5')

email, date, account, amount = get_contacts('files/detail.txt')  # read contacts
message_template = read_template('files/message.txt')

for email, date, account, amount in zip(email,date, account, amount):
    msg = MIMEMultipart()  # create a message

    # add in the actual person name to the message template
    #messagestr = message_template.substitute(DATE=date, ACCOUNT_NUM=account, AMOUNT=amount,CONTACT='0112396502')
    messagestr = message_template.substitute(ACCOUNT_NUM=account, AMOUNT=amount)
    logger.info(messagestr)
    print(messagestr)


    # connect with Google's servers
    #smtp_ssl_host = 'mail.slt.com.lk'
    smtp_ssl_host = '124.43.129.50'
    smtp_ssl_port = 25
    # use username or email to log in
    #username = 'origin@gmail.com'
    #password = 'password'

    #from_addr = 'oss@slt.com.lk'
    from_addr = 'sltbillcc@slt.lk'

    to_addrs = [email]

    # the email lib has a lot of templates
    # for different message formats,
    # on our case we will use MIMEText
    # to send only text
    sub = 'SLTMobitel - Home bill outstanding as at 24/11/2022'

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

        # we'll connect using SSL
        server = smtplib.SMTP(smtp_ssl_host, smtp_ssl_port)
        # to interact with the server, first we log in
        # and then we send the message
        #server.login(username, password)
        server.sendmail(from_addr, to_addrs, message.as_string())
        logger.info(email)
        logger.info('mail sent.....')
        print('mail sent.....')
        logger.info('========================================================================================')
        server.quit()
    except Exception as e:
        print(e)
        logger.info(e)
        logger.info('========================================================================================')

