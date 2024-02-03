import sqlite3
from datetime import date


class Knowledge_Basket():
    conn = sqlite3.connect('Knowledge.db', check_same_thread=False)
    cur = conn.cursor()

    def show_tags(self):
        self.cur.execute('''SELECT tag_name FROM tags''')
        tags = [i[0] for i in self.cur.fetchall()]
        print(tags)
        self.conn.commit()
        return tags

    def show_post_by_tag(self, tag):
        self.cur.execute(f'''SELECT title
         FROM Posts
         ORDER BY title''')
        posts = [i[0] for i in self.cur.fetchall()]
        print(posts)
        return posts
    
    def show_post_by_subject(self, subject_title):
        self.cur.execute(f'''SELECT Posts.title
         FROM Posts INNER JOIN subject USING(subject_id)
         WHERE subject.title = '{subject_title}'
         ORDER BY Posts.date_post''')
        posts = [i[0] for i in self.cur.fetchall()]
        print(posts)
        return posts

    def show_all_posts_title(self):
        self.cur.execute('''SELECT title FROM Posts''')
        title = [i[0] for i in self.cur.fetchall()]
        return title

    def show_post(self, post_title):
        post_title = post_title.strip()
        self.cur.execute(f'''SELECT Posts.title, date_post, subject.title, post_text, image
        FROM Posts INNER JOIN subject USING(subject_id)
        WHERE Posts.title = "{post_title}"''')
        post = self.cur.fetchall()
        return post

    def show_subjects_titles(self):
        self.cur.execute('SELECT title from subject')
        subjects_titles = self.cur.fetchall()
        subjects_titles = [i[0] for i in subjects_titles]
        return subjects_titles
        

    def add_tag(self, tag):
        self.cur.execute('''INSERT INTO tag 
        VALUES (?);''', (tag, ))
        self.conn.commit()

    def add_subject(self, subject_title, subject_description):
        self.cur.execute('''INSERT INTO  subject
                VALUES (?, ?, ?);''', (None, subject_title,subject_description))
        self.conn.commit()

    def find_subject_id(self, subject_title):
        self.cur.execute(f'''SELECT subject_id FROM subject WHERE title = "{subject_title}"''')
        subject_id = self.cur.fetchone()[0]
        return subject_id

    def add_post(self, title, subject_title, text, url):
        subject_id = self.find_subject_id(subject_title)
        today_date = date.today()
        if bool(subject_id) == False:
            self.add_subject(subject_title)
        self.cur.execute('''INSERT INTO Posts ('post_id', 'title',
'date_post','subject_id','post_text','image')
VALUES (?, ?, ?, ?, ?, ?);''', (None, title, today_date, subject_id, text, url))
        self.conn.commit()

    def dell_post(self, title):
        self.cur.execute(f'''DELETE FROM Posts
WHERE title = "{title}"''') 
