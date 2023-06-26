const searchCard = () => {
    const searchInput = document.getElementById('search_card').value;
    const url = `/search?name=${searchInput}`;

    fetch(url)
        .then(response => response.json())
        .then(data => displaySearchResults(data.results))
        .catch(error => console.log(error));
};

const dbSearch = () => {
    const searchInput = document.getElementById('dashboard_search_card').value;
    const url = `/search/results?name=${searchInput}`;
    window.location.href = url;
};


const displaySearchResults = (results) => {
    const searchResultsContainer = document.getElementById('search-results-body');
    searchResultsContainer.innerHTML = "";

    for (const result of results) {
        const row = document.createElement('tr');

        const cardNameCell = document.createElement('td');
        const cardTypeCell = document.createElement('td');
        const addButtonCell = document.createElement('td');
        const addButtonForm = document.createElement('form');
        const addButton = document.createElement('button');

        cardNameCell.textContent = result.name;
        cardTypeCell.textContent = result.type.join(', '); 
        addButton.textContent = 'Add';

        addButtonForm.addEventListener('submit', (event) => {
            event.preventDefault();
            addCardToDeck(result);
            saveDeck();  // Save the deck after a card is added.
            const searchInput = document.getElementById('search_card');
            searchInput.value = '';
        });

        addButtonForm.appendChild(addButton);
        addButtonCell.appendChild(addButtonForm);
        row.appendChild(cardNameCell);
        row.appendChild(cardTypeCell);
        row.appendChild(addButtonCell);
        searchResultsContainer.appendChild(row);
    }
};

const addCardToDeck = (card) => {
    const deckContainer = document.getElementById('decklist');
    const existingCard = Array.from(deckContainer.children).find(
        (row) => row.cells[0].textContent === card.name
    );

    if (isBasicLand(card.name)) {
        if (existingCard) {
            const countCell = existingCard.cells[1];
            const count = parseInt(countCell.textContent.split('x')[1]);
            countCell.textContent = `x${count + 1}`;
        } else {
            const row = document.createElement('tr');
            const cardNameCell = document.createElement('td');
            const countCell = document.createElement('td');
            const removeButtonCell = document.createElement('td');
            const removeButtonForm = document.createElement('form');
            const removeButton = document.createElement('button');

            cardNameCell.textContent = card.name;
            countCell.textContent = 'x1';
            removeButton.textContent = 'Remove';

            removeButtonForm.addEventListener('submit', (event) => {
                event.preventDefault();
                removeCardFromDeck(card.name);
            });

            removeButtonForm.appendChild(removeButton);
            removeButtonCell.appendChild(removeButtonForm);
            row.appendChild(cardNameCell);
            row.appendChild(countCell);
            row.appendChild(removeButtonCell);
            deckContainer.appendChild(row);
        }
    } else {
        if (existingCard) {
            const countCell = existingCard.cells[1];
            const count = parseInt(countCell.textContent.split('x')[1]);
            if (count < 4) {
                countCell.textContent = `x${count + 1}`;
            }
        } else {
            const cardCount = Array.from(deckContainer.children).reduce(
                (count, row) => count + parseInt(row.cells[1].textContent.split('x')[1]),
                0
            );

            if (cardCount < 60) {
                const row = document.createElement('tr');
                const cardNameCell = document.createElement('td');
                const countCell = document.createElement('td');
                const removeButtonCell = document.createElement('td');
                const removeButtonForm = document.createElement('form');
                const removeButton = document.createElement('button');

                cardNameCell.textContent = card.name;
                countCell.textContent = 'x1';
                removeButton.textContent = 'Remove';

                removeButtonForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    removeCardFromDeck(card.name);
                });

                removeButtonForm.appendChild(removeButton);
                removeButtonCell.appendChild(removeButtonForm);
                row.appendChild(cardNameCell);
                row.appendChild(countCell);
                row.appendChild(removeButtonCell);
                deckContainer.appendChild(row);
            }
        }
    }
    updateCardCount();
};

const removeCardFromDeck = (cardName) => {
    const deckContainer = document.getElementById('decklist');
    const rows = deckContainer.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const nameCell = row.cells[0];

        if (nameCell.textContent === cardName) {
            const countCell = row.cells[1];
            const count = parseInt(countCell.textContent.split('x')[1]);

            if (count > 1) {
                countCell.textContent = `x${count - 1}`;
            } else {
                deckContainer.removeChild(row);
            }

            break;
        }
    }

    saveDeck();  // Save the deck after a card is removed.
    updateCardCount();
};

const saveDeck = () => {
    const deckContainer = document.getElementById('decklist');

    const cardList = Array.from(deckContainer.children).map(row => {
        const cardName = row.cells[0].textContent;
        const count = parseInt(row.cells[1].textContent.split('x')[1]);
        return { name: cardName, count: count };
    });

    const deckInput = document.getElementById('deck');
    deckInput.value = JSON.stringify(cardList);
};


const isBasicLand = (cardName) => {
    const basicLands = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest'];
    return basicLands.includes(cardName);
};

const updateCardCount = () => {
    const deckContainer = document.getElementById('decklist');
    const cardCount = Array.from(deckContainer.children).reduce(
        (count, row) => count + parseInt(row.cells[1].textContent.split('x')[1]),
        0
    );

    document.getElementById('card_count').value = cardCount;

    const createButton = document.getElementById('create_button');
    if (cardCount >= 60) {
        createButton.disabled = false;
    } else {
        createButton.disabled = true;
    }
};

window.removeCardFromDeck = removeCardFromDeck;
window.updateCardCount = updateCardCount;
window.dbSearch = dbSearch;
