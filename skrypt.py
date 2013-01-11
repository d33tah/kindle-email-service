#!/usr/bin/python
import smtplib, imaplib, email

"""
Currently it's just a Kindle forwarder. Too lazy to document for now.
"""

from config import imap_host, smtp_host, smtp_port, user, passwd
from config import from_addr, admin_addr, to_addr

client = imaplib.IMAP4_SSL(imap_host)
client.login(user, passwd)
client.select('INBOX')

result, search_data = client.search(None, "ALL")
email_ids = search_data[0].split()

smtp_loggedin = False

for email_id in reversed(email_ids):
	if not smtp_loggedin:
		smtp = smtplib.SMTP(smtp_host, smtp_port)
		smtp.starttls()
		smtp.login(user, passwd)
		smtp_loggedin = True

	status, data = client.fetch(email_id, "(RFC822)")
	email_data = data[0][1]
	message = email.message_from_string(email_data)

	original_from = message['From']
	original_subject = message['Subject']

	message.replace_header("From", from_addr)
	message.replace_header("To", to_addr)
	del message['Message-ID']

	print(message.as_string())
	sender_domain = original_from.split('@')[1].lower()
	if sender_domain.find('kindle')==-1 and sender_domain.find('amazon')==-1:
		smtp.sendmail(from_addr, to_addr, message.as_string())
		message.replace_header('Subject',"Re: %s" % original_subject)
		message.set_payload('SENT.\n\n'+message.get_payload())
		smtp.sendmail(from_addr, admin_addr, message.as_string())
	else:
		message.replace_header('Subject',"KINDLE ERROR: %s" % original_subject)
		smtp.sendmail(from_addr, admin_addr, message.as_string())
	client.store(email_id, '+FLAGS', '\\Deleted')
	client.expunge()

if smtp_loggedin:
	print("...done.")
	smtp.quit()
else:
	print("...did nothing.")

client.close()
client.logout()

