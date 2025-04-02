from django.shortcuts import render, redirect
import joblib
import pandas as pd
from django.contrib.auth.models import User
from django.contrib import messages, auth


# Load saved models
countvect = joblib.load("C:/Users/HP/Desktop/Django Projects/Course/Courserecommend/ml_models/count_vectorizer.pkl")
cosine_sim_mat = joblib.load("C:/Users/HP/Desktop/Django Projects/Course/Courserecommend/ml_models/cosine_similarity.pkl")

# Load course data
df = pd.read_csv("C:/Users/HP/Desktop/Django Projects/Course/Courserecommend/ml_models/cleaned_courses.csv")

# Function to get recommendations
def recommend_course(title, numrec=5):
    """
    Returns a list of recommended courses based on the input title.
    """
    course_index = pd.Series(df.index, index=df['course_title'].str.lower().str.strip()).drop_duplicates()

    title = title.lower().strip()
    if title not in course_index:
        return [{"error": "No matching course found. Please enter a valid course title."}]

    index = course_index[title]
    scores = list(enumerate(cosine_sim_mat[index]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    selected_course_index = [i[0] for i in sorted_scores[1:numrec+1]]
    selected_course_score = [i[1] for i in sorted_scores[1:numrec+1]]

    rec_df = df.iloc[selected_course_index].copy()  # Avoid SettingWithCopyWarning
    rec_df.loc[:, 'Similarity_Score'] = selected_course_score  # Use .loc to modify safely

    return rec_df[['course_title', 'Similarity_Score', 'url', 'price', 'num_subscribers']].to_dict(orient="records")

# Django view function
def home(request):
    """
    Handles requests for the home page and provides course recommendations based on user input.
    """
    recommended_courses = []
    error_message = None

    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        if user_input:
            recommended_courses = recommend_course(user_input)
            if recommended_courses and "error" in recommended_courses[0]:  # Safe check
                error_message = recommended_courses[0]["error"]
                recommended_courses = []

    return render(request, "index.html", {"courses": recommended_courses, "error": error_message})




def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login Successfull!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    else:
        return render(request, "login.html")




def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password1"]
        conf_password = request.POST["password2"]

        if password == conf_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
                return redirect("register")
            
            else:
                user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,)
                user.save()
                messages.success(request, "Registration successful! You are now logged in.")
                auth.login(request , user)
                return redirect ("home")
        else:
            messages.error(request, "Password not matching...")
    else:
        return render(request, "register.html")
    

def logout(request):
    auth.logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect("home")
