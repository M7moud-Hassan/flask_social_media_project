from auth import db,app
import sys
from auth.models import Register

def create_db():
	with app.app_context():
		db.create_all()


#def create_Subject():
#	with app.app_context():
#		stu = Student.query.first()
#		student = Subject(id=2,sub='this my description', student_email=stu.email)
#		db.session.add(student)
#		db.session.commit()

#def print_subject():
#	with app.app_context():
#		student = Student.query.first()
#		print(student.subjects)
		#print(subjects)



if __name__ == '__main__':
	globals()[sys.argv[1]]()