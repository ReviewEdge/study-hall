window.addEventListener("DOMContentLoaded", function() {
    const flashcards = document.getElementsByClassName("flashcard");
    for (const f of flashcards) {
        const editBtn = f.getElementsByClassName("edit-btn")[0];
        editBtn.addEventListener("click", () => { editModeOn(f) });

        const saveBtn = f.getElementsByClassName("save-btn")[0];
        saveBtn.addEventListener("click", () => { editModeOff(f) });
    }
})

function editModeOn(flashcard) {
    flashcard.getElementsByClassName("front")[0].style.display = "none"
    flashcard.getElementsByClassName("back")[0].style.display = "none"
    flashcard.getElementsByClassName("edit-btn")[0].style.display = "none";

    flashcard.getElementsByClassName("front-editing")[0].style.display = "block";
    flashcard.getElementsByClassName("back-editing")[0].style.display = "block";
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
    
    flashcard.getElementsByClassName("front")[0].style.display = "block"
    flashcard.getElementsByClassName("back")[0].style.display = "block"
    flashcard.getElementsByClassName("edit-btn")[0].style.display = "inline";

    flashcard.getElementsByClassName("front-editing")[0].style.display = "none";
    flashcard.getElementsByClassName("back-editing")[0].style.display = "none";
    flashcard.getElementsByClassName("save-btn")[0].style.display = "none";
}
