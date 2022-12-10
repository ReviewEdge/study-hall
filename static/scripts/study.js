window.addEventListener("DOMContentLoaded", function() {
    const flashcard = document.querySelector(".flashcard");
    flashcard.addEventListener("click", flip);
})

function flip() {
    document.querySelector(".flashcard").classList.toggle("flipCard");
}