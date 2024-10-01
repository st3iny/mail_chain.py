#!/bin/python3

import math
import sys

from datetime import datetime, timezone
from email import utils as email_utils
from email.message import EmailMessage
from imaplib import IMAP4_SSL
from os.path import basename
from random import randint
from uuid import uuid4

# ----- BEGIN SETTINGS -----
IMAP_HOST = 'localhost'
IMAP_PORT = 4993

# Format: (NAME, ADDRESS, LOGIN, PASSWORD)
USER_A = ('Alice', 'alice@stalwart.localhost', 'alice@stalwart.localhost', 'alice')
USER_B = ('Bob',   'bob@stalwart.localhost',   'bob@stalwart.localhost',   'bob')

# Mailbox names on the IMAP server (names with spaces need to be quoted)
INBOX_NAME = 'INBOX'
SENT_NAME = '"Sent Items"'

MIN_THREAD_LENGTH = 1
MAX_THREAD_LENGTH = 10
# ----- END SETTINGS -----

LOREM = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'

def generate_lorem(paragraphs):
	return '\n\n'.join([LOREM] * paragraphs)

def generate_message_id():
	return f'<{uuid4()}@mail_chain.py>'

class User:
	def __init__(self, name, address, login, password):
		self.name = name
		self.address = address
		self.login = login
		self.password = password
		self.imap = self.connect()

	def connect(self):
		imap = IMAP4_SSL(IMAP_HOST, IMAP_PORT)
		imap.login(self.login, self.password)
		return imap

	@property
	def rfc2822(self):
		return email_utils.formataddr((self.name, self.address))

	def send(self, msg):
		self.imap.append(SENT_NAME, None, datetime.now(timezone.utc), msg)

	def receive(self, msg):
		self.imap.append(INBOX_NAME, None, datetime.now(timezone.utc), msg)

def thread(alice, bob, length):
	msgids = []
	for i in range(length):
		msgid = generate_message_id()
		subject = f'Lorem Ipsum [{i + 1}/{length}]'

		msg = EmailMessage()
		msg.add_header('Message-ID', msgid)
		msg.add_header('References', ', '.join(msgids))
		msg.add_header('Date', email_utils.format_datetime(datetime.now(timezone.utc)))
		if i % 2 == 0:
			msg.add_header('From', alice.rfc2822)
			msg.add_header('To', bob.rfc2822)
		else:
			msg.add_header('From', bob.rfc2822)
			msg.add_header('To', alice.rfc2822)
		if len(msgids) == 0:
			msg.add_header('Subject', subject)
		else:
			msg.add_header('Subject', f'Re: {subject}')
			msg.add_header('In-Reply-To', msgids[-1])
		msg.set_payload(generate_lorem(randint(1, 3)))

		raw_msg = msg.as_bytes()
		if i % 2 == 0:
			alice.send(raw_msg)
			bob.receive(raw_msg)
		else:
			bob.send(raw_msg)
			alice.receive(raw_msg)

		msgids.append(msgid)

def mail_chain(total_messages):
	user_a = User(*USER_A)
	user_b = User(*USER_B)
	total_messages_digits = math.ceil(math.log10(total_messages)) + 1
	sent_messages = 0
	while sent_messages < total_messages:
		length = randint(MIN_THREAD_LENGTH, MAX_THREAD_LENGTH)
		thread(user_a, user_b, length)
		sent_messages += length

		sent_messages_padded = str(sent_messages).rjust(total_messages_digits, ' ')
		print(f'Sent {sent_messages_padded}/{total_messages} messages')

def usage():
	name = basename(sys.argv[0])
	print(f'Usage: {name} <total_messages>')
	print('')
	print('Generate many email threads for testing purposes and persist them on an IMAP server.')
	print(f'Edit the settings block at the beginning of {name} before running.')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		usage()
		sys.exit(1)

	total_messages = int(sys.argv[1])
	if total_messages <= 0:
		print(f'Invalid value for total messages: {sys.argv[1]}')
		usage()
		sys.exit(1)

	mail_chain(total_messages)
