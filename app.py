from flask import Flask ,render_template,request
import mysql.connector
import time

app = Flask(__name__)
@app.route('/')
def login():
	return render_template('login.html')

@app.route('/user/',methods = ['POST'])
def user():
	l = time.strftime("%x")
	dat = list(map(int,l.split('/')))
	todaydate  = '20'+str(dat[2])+'-'+str(dat[0])+'-'+str(dat[1])

	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	login_id = request.form['loginid']
	password = request.form['password']
	searchUser="select category from Member where login_id = %s and password = %s"
	cursor = cnx.cursor(buffered=True)
	cursor.execute(searchUser,(login_id,password))
	category = cursor.fetchall()
	if searchUser!=[]:
		if category[0][0] == 'student':
			cursor.execute('call fine(%s)',(todaydate,))
			cursor.execute('select SUM(fine) from Borrower where login_id like %s',(login_id,))
			fine = cursor.fetchall()
			cursor.execute('select book_id,issue_date,expire_date,fine from Borrower where login_id = %s',(login_id,))
			books = cursor.fetchall()
			cursor.execute('select name from Member where login_id = %s',(login_id,))
			name = cursor.fetchall()
			cursor.execute('select total_fine from Member where login_id = %s',(login_id,))
			totalfine= cursor.fetchall()
			if fine[0][0] != None:
				return render_template('student.html',user = 'Hey! '+ name[0][0],books = books,totalfine = int(totalfine[0][0]) + int(fine[0][0]))
			else :
				return render_template('na.html',totalfine = int(totalfine[0][0]))
		if category[0][0] == 'faculty':
			cursor.execute('call fine(%s)',(todaydate,))
			cursor.execute('select SUM(fine) from Borrower where login_id like %s',(login_id,))
			fine = cursor.fetchall()
			cursor.execute('select book_id,issue_date,expire_date,fine from Borrower where login_id = %s',(login_id,))
			books = cursor.fetchall()
			cursor.execute('select name from Member where login_id = %s',(login_id,))
			name = cursor.fetchall()
			cursor.execute('select total_fine from Member where login_id = %s',(login_id,))
			totalfine= cursor.fetchall()
			print(totalfine[0][0],fine[0][0])
			if fine[0][0] != None:
				return render_template('student.html',user = 'Hey! '+ name[0][0],books = books,totalfine = int(totalfine[0][0]) + int(fine[0][0]))
			else :
				return render_template('na.html',totalfine = int(totalfine[0][0]))
		if category[0][0] == 'librarian':
			return render_template('library.html')
		if category[0][0] == 'admin':
			return render_template('admin.html') 
	cnx.commit()
	cursor.close()
	return "wrong id password"

@app.route('/booksearch/',methods = ['POST'])
def booksearch():
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	name = request.form['bookName']
	cursor = cnx.cursor(buffered=True)
	cursor.execute('select book_id,name,available from Books where name like %s',('%'+name+'%',))
	books=cursor.fetchall()
	cnx.commit()
	cursor.close()
	return render_template('bookresult.html',books=books)


@app.route('/bookissue/',methods = ['POST'])
def bookissue():
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	bookid = request.form['bookId']
	loginid = request.form['loginId']
	cursor = cnx.cursor(buffered=True)
	a = time.strftime("%x")
	dat = list(map(int,a.split('/')))
	issuedate  = '20'+str(dat[2])+'-'+str(dat[0])+'-'+str(dat[1])
	cursor.execute('insert into Borrower(login_id,book_id,issue_date) values (%s,%s,%s)',(loginid,bookid,issuedate))
	cursor.execute('update Books set available = %s where book_id = %s',('no',bookid))
	cnx.commit()
	cursor.close()
	return "done"

# after bookreturn takecare of fine
@app.route('/bookreturn/',methods = ['POST'])
def bookreturn():
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	bookid = request.form['bookId']
	loginid = request.form['loginId']
	cursor = cnx.cursor(buffered=True)
	cursor.execute('select fine from Borrower where book_id = %s',(bookid,))
	fine = cursor.fetchall()
	cursor.execute('update Member set total_fine = total_fine + %s',(fine[0][0],))
	cursor.execute('delete from Borrower where login_id = %s and book_id=%s',(loginid,bookid))
	cursor.execute('update Books set available = %s where book_id = %s',('yes',bookid))
	cnx.commit()
	cursor.close()
	return "done"

@app.route('/userfine/',methods = ['POST'])
def userfine():
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	loginid = request.form['loginId']
	cursor = cnx.cursor(buffered=True)
	cursor.execute('select total_fine from Member where login_id = %s',(loginid,))
	totalfine=cursor.fetchall()
	cnx.commit()
	cursor.close()
	return render_template('finepaid.html',fine=totalfine[0][0],loginid=loginid)

@app.route('/paid/<loginid>/',methods=['GET', 'POST'])
def finepaid(loginid):
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	cursor = cnx.cursor(buffered=True)
	cursor.execute('update Member set total_fine = 0 where login_id = %s',(loginid,) )
	cnx.commit()
	cursor.close()
	return  "fine paid"

@app.route('/booklost/',methods = ['POST'])
def booklost():
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')
	cursor = cnx.cursor(buffered=True)
	cursor.execute('update Books set available =%s where book_id=%s',('los',request.form['bookId']))
	cnx.commit()
	cursor.close()
	return "database updated"


@app.route('/admin/',methods = ['POST'])
def admin():
	option = request.form['option']
	if(option == 'abook'):
		return render_template('add.html',action = option,price_email="price",pubid_pass="pubid")
	if(option == 'rbook'):
		return render_template('remove.html',action = option,id = 'BOOK ID')
	if(option == 'astud'):
		return render_template('add.html',action = option,price_email="email",pubid_pass="pass")
	if(option == 'rstud'):
		return render_template('remove.html',action = option,id = 'STUDENT ID')
	if(option == 'afacu'):
		return render_template('add.html',action = option,price_email="email",pubid_pass="pass")
	if(option == 'rfacu'):
		return render_template('remove.html',action = option,id = 'FACULTY ID')
	if(option == 'alibr'):
		return render_template('add.html',action = option,price_email="email",pubid_pass="pass")
	if(option == 'rlibr'):
		return render_template('remove.html',action = option,id = 'LIBRARIAN ID')

@app.route('/admin/<action>',methods = ['POST'])
def remove(action):
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')	
	id = request.form['id']
	if action == 'rbook' :
		cur= cnx.cursor(buffered=True)
		cur.execute('delete from Books where book_id = %s',(id,))
		cnx.commit()
		cur.close()
	if action == 'rstud' :
		cur= cnx.cursor(buffered=True)
		cur.execute('delete from Member where login_id = %s',(id,))
		cnx.commit()
		cur.close()
	if action == 'rfacu' :
		cur= cnx.cursor(buffered=True)
		cur.execute('delete from Member where login_id = %s',(id,))
		cnx.commit()
		cur.close()
	if action == 'rlibr' :
		cur= cnx.cursor(buffered=True)
		cur.execute('delete from Member where login_id = %s',(id,))
		cnx.commit()
		cur.close()

	return "removed"


@app.route('/admin/a/<action>',methods=['POST'])
def add(action):
	cnx = mysql.connector.connect(user='devkalra', password='password',host='127.0.0.1',database='library')	
	name = request.form['name']
	id = request.form['id']
	form = request.form
	if action == 'abook':
		cur= cnx.cursor(buffered=True)
		cur.execute('insert into Books values(%s,%s,%s,%s,%s)',(id,name,int(form['price']),form['pubid'],'yes'))
		cnx.commit()
		cur.close()
	if action == 'astud':
		cur= cnx.cursor(buffered=True)
		cur.execute('insert into Member values(%s,%s,%s,%s,%s,0)',(id,form['pass'],form['email'],'student',name))
		cnx.commit()
		cur.close()
	if action == 'afacu':
		cur= cnx.cursor(buffered=True)
		cur.execute('insert into Member values(%s,%s,%s,%s,%s,0)',(id,form['pass'],form['email'],'faculty',name))
		cnx.commit()
		cur.close()
	if action == 'alibr':
		cur= cnx.cursor(buffered=True)
		cur.execute('insert into Member values(%s,%s,%s,%s,%s,0)',(id,form['pass'],form['email'],'librarian',name))
		cnx.commit()
		cur.close()
	
	return 'done'


