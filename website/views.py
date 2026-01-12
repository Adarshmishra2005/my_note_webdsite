from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    cursor = current_app.db.cursor(dictionary=True)

    if request.method == 'POST':
        note = request.form.get('note')

        if not note or len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            cursor.execute(
                "INSERT INTO notes (data, user_id) VALUES (%s, %s)",
                (note, current_user.id)
            )
            current_app.db.commit()
            flash('Note added!', category='success')

    # 🔹 Fetch notes of logged-in user
    cursor.execute(
        "SELECT id, data FROM notes WHERE user_id = %s",
        (current_user.id,)
    )
    notes = cursor.fetchall()
    cursor.close()

    return render_template("home.html", user=current_user, notes=notes)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    note_id = note.get('noteId')

    cursor = current_app.db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM notes WHERE id = %s",
        (note_id,)
    )
    note_obj = cursor.fetchone()

    if note_obj and note_obj['user_id'] == current_user.id:
        cursor.execute(
            "DELETE FROM notes WHERE id = %s",
            (note_id,)
        )
        current_app.db.commit()

    cursor.close()
    return jsonify({})
