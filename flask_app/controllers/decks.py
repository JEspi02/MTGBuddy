from flask_app import app
from flask import render_template, redirect, request, session, jsonify, flash
from flask_app.models.deck import Deck, Card, DeckCard
from flask_app.models.user import User

from mtgsdk import Card as MTGCard
import json

@app.route('/search/results')
def search_results():
    name = request.args.get('name')
    cards = MTGCard.where(name=name).all()
    return render_template('search_results.html', cards=cards[:25])

@app.route('/search')
def search():
    name = request.args.get('name')
    cards = MTGCard.where(name=name).all()

    search_results = []
    for card in cards[:5]:
        card_details = {
            'name': card.name,
            'type': card.types,
            'mana_cost': card.mana_cost,
        }
        search_results.append(card_details)

    return jsonify(results=search_results)


@app.route('/decktoolkit')
def decktoolkit():
    if 'user_id' not in session:
        return redirect('/user/login')

    user_id = session['user_id']
    decks = Deck.get_all(user_id)

    return render_template('decktoolkit.html', decks=decks)


@app.route('/deck/new')
def new_deck():
    if 'user_id' not in session:
        return redirect('/user/login')

    user_id = session['user_id']
    user = User.get_by_id({"id": user_id})

    return render_template("deck_new.html", user=user)

@app.route('/deck/new/process', methods=['POST'])
def process_new_deck():
    if 'user_id' not in session:
        return redirect('/user/login')

    try:
        deck_data = json.loads(request.form['deck'])
    except (KeyError, json.JSONDecodeError) as e:
        print("Error: ", e)
        return redirect('/deck/new')

    is_valid, error_message = Deck.validate_deck({'deck': deck_data})

    if not is_valid:
        flash(error_message)
        return redirect('/deck/new')

    deck_name = request.form.get('deck_name', '')
    description = request.form.get('description', '')
    sideboard = request.form.get('sideboard', '')

    deck_info = {
        'user_id': session['user_id'],
        'deck_name': deck_name,
        'description': description,
        'card_count': len(deck_data),  # card_count now equals the number of instances
        'sideboard': sideboard,
    }

    deck_id = Deck.save(deck_info, deck_data)

    return redirect('/decktoolkit')


"""
NOT USING CURRENTLY 
@app.route('/deck/<int:id>')
def view_deck(id):
    if 'user_id' not in session:
        return redirect('/user/login')

    user_id = session['user_id']
    user = User.get_by_id({"id": user_id})
    deck = Deck.get_by_id({'id': id})

    if not deck:
        flash("Deck not found!")
        return redirect('/decktoolkit')

    deck_cards = Deck.get_deck_cards({'deck_id': id})  # Updated line

    return render_template('deck_view.html', deck=deck, user=user, deck_cards=deck_cards)
"""

@app.route('/deck/edit/<int:id>')
def edit_deck(id):
    if 'user_id' not in session:
        return redirect('/user/login')

    user_id = session['user_id']
    user = User.get_by_id({"id": user_id})

    deck = Deck.get_by_id({'id': id})

    if not deck:
        flash("Deck not found!")
        return redirect('/decktoolkit')

    deck_cards = Deck.get_deck_cards(id)

    return render_template('deck_edit.html', deck=deck, user=user, deck_cards=deck_cards)


@app.route('/deck/edit/process/<int:id>', methods=['POST'])
def process_edit_deck(id):
    if 'user_id' not in session:
        return redirect('/user/login')

    try:
        deck_data = json.loads(request.form['deck'])
    except (KeyError, json.JSONDecodeError) as e:
        print("Error: ", e)
        return redirect(f'/deck/edit/{id}')

    is_valid, error_message = Deck.validate_deck({'deck': deck_data})

    if not is_valid:
        flash(error_message)
        return redirect(f'/deck/edit/{id}')

    data = {
        'id': id,
        'user_id': session['user_id'],
        'deck_name': request.form['deck_name'],
        'card_count': len(deck_data),  # card_count now equals the number of instances
        'description': request.form['description'],
        'sideboard': request.form['sideboard'],
    }
    
    Deck.update(data, deck_data)

    return redirect(f'/deck/edit/{id}')

@app.route('/deck/destroy/<int:id>')
def destroy_deck(id):
    if 'user_id' not in session:
        return redirect('/user/login')

    Deck.destroy({'id': id})

    return redirect('/decktoolkit')
