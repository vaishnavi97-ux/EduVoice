from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from speechprocessor import process_audio, summarize, speech_to_text, clean_text
from flask import send_file
import tempfile

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduvoice.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# ------------------ MODELS ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(10))

class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    file_path = db.Column(db.String(200))
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

# ------------------ ROUTES ------------------

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('teacher_dashboard' if user.role=='teacher' else 'student_dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        teachers = User.query.filter_by(role='teacher').all()
        return render_template(
            'student_dashboard.html',
            teachers=teachers,
            active_tab='student'
        )
    return redirect(url_for('login'))
# ------------------ TEACHER DASHBOARD ------------------

@app.route('/teacher_dashboard', methods=['GET','POST'])
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        subject = request.form['subject']

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        transcript, summary = process_audio(filepath)

        lecture = Lecture(
            title=title,
            subject=subject,
            file_path=file.filename,
            transcript=transcript,
            summary=summary,
            uploaded_by=session['user_id']
        )

        db.session.add(lecture)
        db.session.commit()

    lectures = Lecture.query.filter_by(uploaded_by=session['user_id']).all()
    teacher_name = User.query.get(session['user_id']).name

    return render_template("teacher_dashboard.html", lectures=lectures, teacher_name=teacher_name)

@app.route('/teacher/<int:teacher_id>')
def teacher_profile(teacher_id):
    if 'role' not in session:
        return redirect(url_for('login'))

    teacher = User.query.get_or_404(teacher_id)
    lectures = Lecture.query.filter_by(uploaded_by=teacher.id).all()

    return render_template(
        'teacher_profile.html',
        teacher=teacher,
        lectures=lectures,
        active_tab='student'
    )

@app.route('/edit_lecture/<int:lecture_id>', methods=['GET', 'POST'])
def edit_lecture(lecture_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    lecture = Lecture.query.get_or_404(lecture_id)

    if request.method == 'POST':
        lecture.title = request.form['title']
        lecture.subject = request.form['subject']

        db.session.commit()

        return redirect(url_for('teacher_dashboard'))

    return render_template('edit_lecture.html', lecture=lecture)

@app.route('/delete_lecture/<int:lecture_id>', methods=['POST'])
def delete_lecture(lecture_id):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    lecture = Lecture.query.get_or_404(lecture_id)

    db.session.delete(lecture)
    db.session.commit()

    return redirect(url_for('teacher_dashboard'))

@app.route('/download_notes/<int:lecture_id>')
def download_notes(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)

    # Create temp file
    temp_path = os.path.join("uploads", f"notes_{lecture_id}.txt")

    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {lecture.title}\n")
        f.write(f"Subject: {lecture.subject}\n\n")
        f.write("Summary:\n")
        f.write(lecture.summary)

    return send_file(temp_path, as_attachment=True)
# ------------------ LIVE SUMMARY (IMPORTANT) ------------------

@app.route('/summarize_text', methods=['POST'])
def summarize_text():
    try:
        data = request.get_json()
        text = data.get("text", "")

        cleaned = clean_text(text)
        summary = summarize(cleaned)

        return jsonify({"summary": summary})
    except Exception as e:
        print("SUMMARY ERROR:", e)
        return jsonify({"summary": "Summary generation failed"})
# ------------------ OTHERS ------------------

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/save_live_lecture', methods=['POST'])
def save_live_lecture():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    title = data.get("title", "Live Session")
    subject = data.get("subject", "Live Transcription")
    transcript = data.get("transcript", "")
    summary = data.get("summary", "")

    if not transcript.strip():
        return jsonify({"error": "Transcript is empty"}), 400

    new_lecture = Lecture(
        title=title,
        subject=subject,
        file_path=None,  # no audio file saved here
        transcript=transcript,
        summary=summary,
        uploaded_by=session['user_id']
    )
    db.session.add(new_lecture)
    db.session.commit()

    return jsonify({"success": True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)