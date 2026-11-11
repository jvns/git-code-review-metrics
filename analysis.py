import sqlite3
import re

# recursively follow the the in-reply-to pointers until we find the original
def find_start_message_id(cur, message_id):
    cur.execute("SELECT message_id, subject, date, in_reply_to FROM list_messages WHERE message_id = ?", [message_id])
    data = cur.fetchone()
    if data is None:
        raise Exception(f"didn't find message {message_id}")
    if data['in_reply_to'] is not None:
        in_reply_to = data['in_reply_to']
        # Sometimes there's extra text after the message-id in the In-Reply-To
        # and I don't know why
        matches = re.findall("(<.+?>)", in_reply_to)
        in_reply_to = matches[0]
        try:
            return find_start_message_id(cur, in_reply_to)
        except:
            # TODO: track these exceptions!!!
            return data
    elif 'PATCH v' in data['subject']:
        pass
        # Do some hacks to try to find the original email
        # matches = re.findall(r"\[PATCH v.+?\] (.+)$", data['subject'])
        # if len(matches) > 0:
        #     base_subject = matches[0]
        #     base_subject = base_subject.replace('update', "Update")
        #     first_subject = f"[PATCH] {base_subject}"
        #     print(first_subject)
        #     data_2 = cur.execute("SELECT message_id FROM list_messages WHERE subject = ?", [first_subject]).fetchone()
        #     if data_2 is not None:
        #         return data_2['message_id']
    return data

def main():
    message_id = '<patch-v3-5.6-25fec54877b-20211001T102056Z-avarab@gmail.com>'
    message_id = '<xmqqa4ngsgk9.fsf@gitster.g>'
    con = sqlite3.connect('emails.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    find_start_message_id(cur, message_id)

if __name__ == '__main__':
    main()

