window.addEventListener("DOMContentLoaded", function() {
    loadFlashcards();

    const addFlashcardButton = document.getElementById("add-flashcard-btn");
    addFlashcardButton.addEventListener("click", postFlashcard);
})

async function loadFlashcards() { 
    const studySetID = document.getElementById("studyset-id").innerText;
    const getFlashcardsURL = `/api/flashcards/${studySetID}/`;

    fetch(getFlashcardsURL)
        .then(validateJSON)
        .then(data => {
            for (const flashcard of data.flashcards) {
                insertFlashcard(flashcard);
            }
        });
}

function insertFlashcard(flashcard) {
    const container = document.getElementById("flashcards-container");
    flashcardTemplate = document.getElementById("flashcard_template");

    const fDiv = flashcardTemplate.cloneNode(true);

    fDiv.id = flashcard.id;
    fDiv.style = "display: block;";

    const front = fDiv.querySelector(".front");
    const back = fDiv.querySelector(".back");
    const frontEditing = fDiv.querySelector(".front-editing");
    const backEditing = fDiv.querySelector(".back-editing");

    front.innerText = flashcard.frontText;
    frontEditing.innerText = flashcard.frontText;
    back.innerText = flashcard.backText;
    backEditing.innerText = flashcard.backText;


    const editBtn = fDiv.getElementsByClassName("edit-btn")[0];
    editBtn.addEventListener("click", () => { editModeOn(fDiv) });

    const saveBtn = fDiv.getElementsByClassName("save-btn")[0];
    saveBtn.addEventListener("click", () => { editModeOff(fDiv) });

    container.appendChild(fDiv);
}

function postFlashcard() {    
    const studySetID = document.getElementById("studyset-id").innerText;
    const postFlashcardURL = `/api/flashcard/create/${studySetID}/`;

    fetch(postFlashcardURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },  body: JSON.stringify({
        })
    })
    .then(validateJSON)
    .then(insertFlashcard);
}

function makeEditable() {
    
}

function editModeOn(flashcard) {
    flashcard.getElementsByClassName("front")[0].style.display = "none";
    flashcard.getElementsByClassName("back")[0].style.display = "none";
    flashcard.getElementsByClassName("edit-btn")[0].style.display = "none";
    flashcard.getElementsByClassName("hr")[0].style.display = "none";

    flashcard.getElementsByClassName("front-editing")[0].style.display = "block";
    flashcard.getElementsByClassName("back-editing")[0].style.display = "block";
    flashcard.getElementsByClassName("hr-editing")[0].style.display = "block";
    flashcard.getElementsByClassName("save-btn")[0].style.display = "inline";
}

function editModeOff(flashcard) {
    const fID = flashcard.id;
    const newFrontText = flashcard.getElementsByClassName("front-editing")[0].value;
    const newBackText = flashcard.getElementsByClassName("back-editing")[0].value;

    fetch(`/api/flashcard/${fID}`, {
        method: 'PATCH',
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
            id: fID,
            frontText: newFrontText,
            backText: newBackText,
        }),
    })
    .catch(error => console.log(error))
    flashcard.getElementsByClassName("front")[0].innerText = newFrontText
    flashcard.getElementsByClassName("back")[0].innerText = newBackText
    
    flashcard.getElementsByClassName("front")[0].style.display = "block";
    flashcard.getElementsByClassName("back")[0].style.display = "block";
    flashcard.getElementsByClassName("edit-btn")[0].style.display = "inline";
    flashcard.getElementsByClassName("hr")[0].style.display = "block";

    flashcard.getElementsByClassName("front-editing")[0].style.display = "none";
    flashcard.getElementsByClassName("back-editing")[0].style.display = "none";
    flashcard.getElementsByClassName("save-btn")[0].style.display = "none";
    flashcard.getElementsByClassName("hr-editing")[0].style.display = "none";
}

/**
 * Validate a response to ensure the HTTP status code indcates success.
 * 
 * @param {Response} response HTTP response to be checked
 * @returns {object} object encoded by JSON in the response
 */
 function validateJSON(response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}

