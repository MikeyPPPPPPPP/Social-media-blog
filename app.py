from flask import Flask,render_template,request,redirect, session, send_file,flash
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login, Posts, Profile, Following, Followers, Profile_image
from datetime import date, datetime
from werkzeug.utils import secure_filename
import base64

'''

-- Todo --
    --add a profile picture upload that gets stord as username.jpeg / username.png in the static file


--securety--
    --sql injections - pramitrized querys with bound variabls
    --login brute forceing - 5 time login trys a user befor lockout
    --username & password enumration on login - if you get one wrong print the same error ("wrong login")
    --xss - filter input and encode output & use apropriat response headers (Content-Type)
'''

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'zip', 'mp4', 'js', 'py', 'jar', 'exe', 'html', 'css', 'mov', 'c'}
DOWNLOAD_DIRECTORY = '/Desktop/Site/herokuv1/uploads'

app = Flask(__name__)
app.secret_key = 'flint you have a call'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', 'jpeg']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
 
db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404




def get_date():
    d = str(date.today())
    n = datetime.now()
    return str(d)#+' - '+str(n.hour)+':'+str(n.minute))

def decode_file(file_name_to_decode):
    return base64.decode(file_name_to_decode)


def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect('/blogs')
    return render_template('home.html')



@app.before_first_request
def create_all():
    db.create_all()


@app.route('/explore', methods = ['POST', 'GET'])
@login_required
def explore():
    if request.method == "POST":
        users_S = request.form['usersearch']

        found_users = []
        for usernames in Profile.query.all():
            if users_S in usernames.username:
                found_users.append(usernames.username)
        try:
            found_users.remove(current_user.username)
        except:
            pass            

        return render_template('search_user.html', values=found_users)

    return render_template('search_user.html')


@app.route('/search', methods = ['POST', 'GET'])
@login_required
def user_blog_search():
    
    if request.method == "POST":
        search_res = request.form["Search"]
        found_user = UserModel.query.filter_by(username=current_user.username).first()

        found_items = []
        for data in Posts.query.all():
            if data.owner_id == current_user.id:
                if str(search_res) in str(data.entry):
                    found_items.append(data)
            
        return render_template('user_blog_search.html', values=found_items)

            
    return render_template('user_blog_search.html')
    

@app.route('/blogs')
@login_required
def blog():
    if current_user.is_authenticated:
        found_user = UserModel.query.filter_by(username=current_user.username).first()
        found_items = []
        followers = []
        follower_owner_id = []
        #gets the following users
        
        for data in Followers.query.all():
            if data.owner_id == current_user.id:
                    #this will make sure there are no doubles added
                user_f = UserModel.query.filter_by(id=data.owner_id).first()
                #test
                if user_f.id not in follower_owner_id:
                    follower_owner_id.append(user_f.id)
                    followers.append(data)
                    print(user_f.id)

        


        #this will add your posts to the found_itmes list
        for data in Posts.query.all():
            if data.owner_id == found_user.id:
                found_items.append(data)

        for user in followers:
            #gets the username in the followers tab
            found_user = UserModel.query.filter_by(username=user.follower_user).first()
            for data in Posts.query.all():
                if data.owner_id == found_user.id:
                    found_items.append(data)

        return render_template('blog.html', values=found_items)
    return render_template('home.html')


@app.route('/profile/<username>', methods = ['POST', 'GET'])
@login_required
def profile(username):
    
    if current_user.is_authenticated:

        if username != current_user.username:
            if request.method == 'POST':
                found_user = UserModel.query.filter_by(username=current_user.username).first()
                new_following = Followers(follower_user=username, owner=found_user)

                

                db.session.add(new_following)

                db.session.commit()
                return redirect('/profile/'+current_user.username)

            found_user = UserModel.query.filter_by(username=username).first()
            found_items = []
            found_posts = []
            followers_for_user = []
            following_for_user = []
            
            for data in Profile.query.all():
                if data.owner_id == found_user.id:
                    found_items.append(data)
            
            for data in Posts.query.all():
                if data.owner_id == found_user.id:
                    found_posts.append(data)
            
            for fols in Followers.query.all():
                if fols.owner_id == found_user.id:
                    followers_for_user.append(fols)

            for fols in Following.query.all():
                if fols.owner_id == found_user.id:
                    following_for_user.append(fols)
            
            


            return render_template('unauth_profile.html', values=found_items, user_posts=found_posts, followers=len(followers_for_user), following=len(following_for_user), length_of_posts=len(found_posts))


        found_user = UserModel.query.filter_by(username=current_user.username).first()
        found_items = []
        found_posts = []
        followers_for_user = []
        following_for_user = []
        
        image_file = []
        img = Profile_image.query.filter_by(owner_id=current_user.id).first()
        #img.image
        
        '''
        for image in Profile_image.query.all():
            if image.owner_id == current_user.id:
                image_file.append(image)
        '''
        for data in Profile.query.all():
            if data.owner_id == current_user.id:
                found_items.append(data)
        
        for data in Posts.query.all():
            if data.owner_id == current_user.id:
                found_posts.append(data)
        
        for fols in Followers.query.all():
            if data.owner_id == current_user.id:
                followers_for_user.append(data)

        for fols in Following.query.all():
            if data.owner_id == current_user.id:
                following_for_user.append(data)

        '''
        if img:
            return render_template('profile2.html', prof_image=img.image, values=found_items, user_posts=found_posts, followers=len(followers_for_user), following=len(following_for_user), length_of_posts=len(found_posts))
        else:
        '''
        return render_template('profile.html', values=found_items, user_posts=found_posts, followers=len(followers_for_user), following=len(following_for_user), length_of_posts=len(found_posts))
    return render_template('home.html')

@app.route('/edit_profile', methods = ['POST', 'GET'])
@login_required
def edit_profile():
    
    if request.method == "POST":
        found_user = UserModel.query.filter_by(username=current_user.username).first()
        user_profile = Profile.query.filter_by(owner_id=found_user.id).first()
        user_gender = request.form.get("genderss", False)
        website = request.form.get("website", False)
        bio = request.form.get("entry")
        
        ####################################   added form here to 
        
        file = request.files.get('file', None)    
        #file = request.files['file']#request.form.get('file')
        # if user does not select file, browser also
        # submit an empty part without filename
        
            
        if file and allowed_file(file.filename):
            print('got a file',file.filename) #   WTF    it will not save a file to the database without this print statment   WTF
            filename = secure_filename(file.filename)
            new_profile_image = Profile_image(file_name=file.filename, image=file.read(), owner_id=found_user.id)
            #user_profile.image = file.read()
            db.session.add(new_profile_image)
            db.session.commit()
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ###################################  here
        
        print(bio)
        user_profile.bio = bio
        user_profile.gender = user_gender
        user_profile.website = website
        db.session.commit()
        return redirect('/profile/'+current_user.username)
    return render_template('edit_profile.html')





@app.route('/add', methods = ['POST', 'GET'])
@login_required
def addtoblog():
    if current_user.is_authenticated:
        if request.method == "POST":
            found_user = UserModel.query.filter_by(username=current_user.username).first()
            
            Entry = request.form["Entry"]

            current_date = str(get_date())
            
            new_post = Posts(entry=Entry.strip(), date=current_date, owner=found_user)
            db.session.add(new_post)
            db.session.commit()
            

            
            return redirect('/blogs')
        
        return render_template('addtoblog.html')

    return render_template('home.html')






@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/blogs')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        #session["user"] = user
        if user is not None and user.check_password(request.form['password']):
            #session["email"] = found_user.email
            login_user(user) 

            
            return redirect('/blogs')
     
    return render_template('login.html')
 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/blogs')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        gender = request.form['gender']
        website = request.form['website']
 
        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = UserModel(email=email, username=username)
        add_profile = Profile(username=username, gender=gender, website=website,owner=user)#, image=open('static/default.jpeg','wb'))
        
        
        user.set_password(password)
        db.session.add(user)
        db.session.add(add_profile)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')
 
 
@app.route('/logout')
def logout():
    #session.pop("user", None)
    #session.pop("email", None)
    logout_user()
    return redirect('/blogs')

if __name__ == "__main__":
    app.run()
