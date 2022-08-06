from webdav3.client import Client
from io import BytesIO, StringIO
import vobject
from datetime import datetime, timedelta
import argparse, os, uuid

def parseDate(date_str):
    for date_fmt in ('%Y-%m-%d', '%Y%m%d', '--%m%d'):
        try:
            return datetime.strptime(date_str, date_fmt)
        except:
            pass
    raise ValueError(f"could not parse date {date_str}")

parser = argparse.ArgumentParser(description='test')
parser.add_argument('--contacts_url', default=os.environ.get('WEBDAV_CONTACTS_URL'))
parser.add_argument('--calendar_url', default=os.environ.get('WEBDAV_CALENDAR_URL'))
parser.add_argument('--user', default=os.environ.get('WEBDAV_USER'))
parser.add_argument('--password', default=os.environ.get('WEBDAV_PASSWORD'))
args = parser.parse_args()

def build_client(url):
    options = {
        "webdav_hostname": url,
        "webdav_login": args.user,
        "webdav_password": args.password,
        "webdav_override_methods": {
            'check': 'GET'
        }
    }

    client = Client(options)
    client.verify = True

    return client

contacts_client = build_client(args.contacts_url)
calendar_client = build_client(args.calendar_url)

for vcf_file in contacts_client.list('/'):
    if not vcf_file.endswith('.vcf'):
        continue

    buff = BytesIO()
    contacts_client.download_from(
        buff=buff,
        remote_path=vcf_file
    )

    contacts = vobject.readComponents(buff.getvalue().decode('utf-8'))
    for contact in contacts:
        print(contact.fn.value)

        if not hasattr(contact, 'bday'):
            continue

        try:
            bday = parseDate(contact.bday.value)

            calendar = vobject.iCalendar()
            event = calendar.add('vevent')
            event.add('summary').value = f"Birthday of {contact.fn.value}"
            event.add('dtstart').value = bday
            event.add('dtend').value = bday + timedelta(days=1)
            event.add('rrule').value =u"FREQ=YEARLY"
            event.add('uid').value = contact.uid.value

            calendar_client.upload_to(buff=calendar.serialize().encode('utf-8'), remote_path=f"{contact.uid.value}.ics")
            print(calendar_client.list())
        except ValueError as e:
            print(f"{e}: {contact.fn.value}")
            continue
