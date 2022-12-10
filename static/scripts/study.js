window.addEventListener("DOMContentLoaded", function() {
    const flashcard = document.querySelector(".flashcard");
    flashcard.addEventListener("click", flip);
})

function flip() {
    document.querySelector(".flashcard").classList.toggle("flipCard");
    document.getElementById("front").classList.toggle("h-0");
    document.getElementById("back").classList.toggle("h-0");
}
