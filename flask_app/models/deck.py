from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User
from flask import flash
import re

db = "mtgdb"

class Deck:
    def __init__(self, db_data):
        self.id = db_data['id']
        self.deck_name = db_data.get('deck_name')
        self.description = db_data.get('description')
        self.user_id = db_data.get('user_id')
        self.created_at = db_data.get('created_at')
        self.updated_at = db_data.get('updated_at')
        self.creator = None

    @classmethod
    def get_all(cls, user_id):
        query = """
                SELECT * FROM deck
                WHERE user_id = %(user_id)s;
                """
        data = {
            'user_id': user_id
        }
        results = connectToMySQL(db).query_db(query, data)
        decks = []
        for row in results:
            deck_data = {
                "id": row['id'],
                "deck_name": row['deck_name'],
                "description": row['description'],
                "card_count": row['card_count'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at'],
                "user_id": row['user_id']
            }
            deck = cls(deck_data)
            deck.cards = cls.get_deck_cards(deck.id)  # Set cards
            decks.append(deck)
        return decks

    @classmethod
    def get_by_id(cls, data):
        query = """
                SELECT * FROM deck
                WHERE id = %(id)s;
                """
        result = connectToMySQL(db).query_db(query, data)
        if not result:
            return False

        row = result[0]
        deck_data = {
            "id": row['id'],
            "deck_name": row['deck_name'],
            "description": row['description'],
            "card_count": row['card_count'],
            "created_at": row['created_at'],
            "updated_at": row['updated_at'],
            "user_id": row['user_id']
        }
        deck = cls(deck_data)
        deck.cards = cls.get_deck_cards(deck.id)  # Set cards
        return deck

    @classmethod
    def save(cls, form_data, deck_data):
        query = """
        INSERT INTO deck (deck_name, description, user_id, card_count, sideboard)
        VALUES (%(deck_name)s, %(description)s, %(user_id)s, %(card_count)s, %(sideboard)s);
        """
        deck_id = connectToMySQL(db).query_db(query, form_data)

        card_counts = {card['name']: card['count'] for card in deck_data}

        for card_name, count in card_counts.items():
            card_id = Card.save(card_name)
            deck_card_data = {
                'deck_id': deck_id,
                'card_id': card_id,
                'card_count': count
            }
            cls.add_card_to_deck(deck_card_data)

        # Update the card count in the deck
        cls.update_card_count(deck_id, sum(card_counts.values()))
        
        return deck_id

    @classmethod
    def update(cls, form_data, deck_data):
        query = """
                UPDATE deck
                SET deck_name = %(deck_name)s,
                card_count = %(card_count)s,
                description = %(description)s,
                sideboard = %(sideboard)s
                WHERE id = %(id)s;
                """
        connectToMySQL(db).query_db(query, form_data)

        # Remove existing cards
        DeckCard.delete_by_deck_id(form_data['id'])

        # Add new cards
        card_counts = {card['name']: card['count'] for card in deck_data}

        for card_name, count in card_counts.items():
            card_id = Card.save(card_name)
            deck_card_data = {
                'deck_id': form_data['id'],
                'card_id': card_id,
                'card_count': count
            }
            cls.add_card_to_deck(deck_card_data)

        # Update the card count in the deck
        cls.update_card_count(form_data['id'], sum(card_counts.values()))

        return form_data['id']

    @classmethod
    def update_card_count(cls, deck_id, card_count):
        query = """
                UPDATE deck
                SET card_count = %(card_count)s
                WHERE id = %(deck_id)s;
                """
        data = {
            "deck_id": deck_id,
            "card_count": card_count
        }
        connectToMySQL(db).query_db(query, data)

    @classmethod
    def destroy(cls, data):
        query = """
                DELETE FROM deck
                WHERE id = %(id)s;
                """
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def add_card_to_deck(cls, card_data):
        query = """
                INSERT INTO deck_cards (deck_id, card_id, card_count)
                VALUES (%(deck_id)s, %(card_id)s, %(card_count)s);
                """
        return connectToMySQL(db).query_db(query, card_data)

    @staticmethod
    def validate_deck(deck_data):
        is_valid = True
        error_message = ''

        try:
            deck = deck_data['deck']
            card_count = 0
            card_names = dict()

            for card in deck:
                if 'count' in card and 'name' in card:
                    count = card['count']
                    card_name = card['name']

                    if not card_name in card_names:
                        card_names[card_name] = int(count)
                    else:
                        card_names[card_name] += int(count)

                    card_count += int(count)
                else:
                    is_valid = False
                    error_message = f'Invalid card format: {card}.'
                    print(error_message)

            if card_count < 60:
                is_valid = False
                error_message = 'Deck must contain 60 or more cards.'
                print(error_message)

            for card_name, count in card_names.items():
                if card_name not in ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest'] and count > 4:
                    is_valid = False
                    error_message = 'Deck can have a maximum of 4 copies of each non-land card.'
                    print(error_message)
        except Exception as e:
            is_valid = False
            error_message = f'Unexpected error: {str(e)}.'
            print(error_message)

        return is_valid, error_message

    @classmethod
    def get_deck_cards(cls, deck_id):
        query = """
                SELECT card.card_name, deck_cards.card_count
                FROM deck_cards
                JOIN card ON deck_cards.card_id = card.id
                WHERE deck_cards.deck_id = %(deck_id)s;
                """
        data = {
            'deck_id': deck_id
        }
        results = connectToMySQL(db).query_db(query, data)
        cards = []
        for row in results:
            card_data = {
                "name": row['card_name'],
                "count": row['card_count']
            }
            cards.append(card_data)
        return cards

class Card:
    @classmethod
    def save(cls, card_name):
        # First, check if the card_name is already in the card table
        query = """
                SELECT id FROM card
                WHERE card_name = %(card_name)s;
                """
        data = {
            "card_name": card_name
        }
        result = connectToMySQL(db).query_db(query, data)
        if result:
            # If the card_name is already in the card table, return its id
            return result[0]['id']
        else:
            # If the card_name is not in the card table, insert it and return its id
            query = """
                    INSERT INTO card (card_name)
                    VALUES (%(card_name)s);
                    """
            return connectToMySQL(db).query_db(query, data)

class DeckCard:
    @classmethod
    def save(cls, deck_id, card_id, card_count):
        query = """
        INSERT INTO deck_cards (deck_id, card_id, card_count)
        VALUES (%(deck_id)s, %(card_id)s, %(card_count)s);
        """
        data = {
            "deck_id": deck_id,
            "card_id": card_id,
            "card_count": card_count
        }
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def delete_by_deck_id(cls, deck_id):
        query = """
                DELETE FROM deck_cards
                WHERE deck_id = %(deck_id)s;
                """
        data = {
            "deck_id": deck_id
        }
        return connectToMySQL(db).query_db(query, data)

